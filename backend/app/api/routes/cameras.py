"""
Camera CRUD routes.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_operator, require_viewer
from app.models.models import Camera, CameraSourceType, CameraStatus, Environment, User
from app.schemas.schemas import CameraCreate, CameraResponse, CameraUpdate
from app.services.ai_service import ai_service

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("", response_model=list[CameraResponse])
async def list_cameras(
    environment_id: UUID | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """List cameras with optional filters."""
    query = select(Camera)
    if environment_id is not None:
        query = query.where(Camera.environment_id == environment_id)
    if is_active is not None:
        query = query.where(Camera.is_active == is_active)
    query = query.order_by(Camera.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """Get a single camera by ID."""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return camera


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    payload: CameraCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator),
):
    """Create a new camera."""
    # Validate environment exists
    env_result = await db.execute(
        select(Environment).where(Environment.id == payload.environment_id)
    )
    if env_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment not found",
        )

    try:
        source_type = CameraSourceType(payload.source_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid source_type '{payload.source_type}'",
        )

    camera = Camera(
        environment_id=payload.environment_id,
        name=payload.name,
        source_type=source_type,
        source_url=payload.source_url,
        fps=payload.fps,
        resolution_width=payload.resolution_width,
        resolution_height=payload.resolution_height,
    )
    db.add(camera)
    await db.flush()
    await db.refresh(camera)
    return camera


@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: UUID,
    payload: CameraUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator),
):
    """Update an existing camera."""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "source_type" in update_data and update_data["source_type"] is not None:
        try:
            update_data["source_type"] = CameraSourceType(update_data["source_type"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid source_type '{update_data['source_type']}'",
            )

    for field, value in update_data.items():
        setattr(camera, field, value)

    await db.flush()
    await db.refresh(camera)
    return camera


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator),
):
    """Delete a camera."""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    await db.delete(camera)
    await db.flush()


@router.post("/{camera_id}/test-connection")
async def test_camera_connection(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator),
):
    """Test connectivity to a camera source."""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    connected = False
    message = "Unknown error"

    if camera.source_type == CameraSourceType.WEBCAM:
        try:
            import cv2

            cap = cv2.VideoCapture(int(camera.source_url or 0))
            connected = cap.isOpened()
            message = "Webcam accessible" if connected else "Cannot open webcam"
            cap.release()
        except Exception as exc:
            message = f"Webcam test failed: {exc}"

    elif camera.source_type in (CameraSourceType.RTSP, CameraSourceType.HTTP):
        if not camera.source_url:
            message = "No source URL configured"
        else:
            try:
                import cv2

                cap = cv2.VideoCapture(camera.source_url)
                connected = cap.isOpened()
                message = "Stream accessible" if connected else "Cannot open stream"
                cap.release()
            except Exception as exc:
                message = f"Stream test failed: {exc}"

    elif camera.source_type == CameraSourceType.UPLOAD:
        connected = True
        message = "Upload source does not require connectivity test"

    # Update camera status based on test
    camera.status = CameraStatus.ONLINE if connected else CameraStatus.ERROR
    await db.flush()

    return {"camera_id": str(camera.id), "connected": connected, "message": message}

@router.post("/{camera_id}/start")
async def start_camera_processing(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator),
):
    """Start video processing and AI pipeline for a camera."""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    camera_id_str = str(camera_id)
    if ai_service.is_stream_running(camera_id_str):
        return {"status": "already running"}

    # Start the Background Task (which loop indefinitely)
    # BackgroundTasks runs after the response is sent. 
    # But since it's an infinite loop, asyncio.create_task is cleaner.
    asyncio.create_task(ai_service.start_demo_stream(camera_id_str))
    
    camera.status = CameraStatus.ONLINE
    await db.flush()

    return {"status": "started"}


@router.post("/{camera_id}/stop")
async def stop_camera_processing(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator),
):
    """Stop a running processing stream without deleting the camera."""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    ai_service.stop_stream(str(camera_id))
    camera.status = CameraStatus.OFFLINE
    await db.flush()
    return {"status": "stopped"}

@router.get("/{camera_id}/stream")
async def stream_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Serve a mock MJPEG video stream."""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    async def generate():
        # Yield empty or dummy MJPEG frames. We don't have real images right now.
        blank_frame = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xFF\xDB\x00\x43\x00\x02\x01\x01\x02\x01\x01\x02\x02\x02\x02\x02\x02\x02\x02\x03\x05\x03\x03\x03\x03\x03\x06\x04\x04\x03\x05\x07\x06\x07\x07\x07\x06\x07\x07\x08\x09\x0B\x09\x08\x08\x0A\x08\x07\x07\x0A\r\x0A\x0B\x0C\x0C\x0C\x0C\x07\x09\x0E\x0F\r\x0C\x0E\x0B\x0C\x0C\x0C\xFF\xC0\x00\x0B\x08\x00\x10\x00\x10\x01\x01\x11\x00\xFF\xC4\x00\x1F\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\x0A\x0B\xFF\xC4\x00\xB5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01\x7D\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q\x142\x81\x91\xA1\x08#B\xB1\xC1\x15R\xD1\xF0$3br\x82\t\n\x16\x17\x18\x19\x1A%&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8A\x92\x93\x94\x95\x96\x97\x98\x99\x9A\xA2\xA3\xA4\xA5\xA6\xA7\xA8\xA9\xAA\xB2\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA\xC2\xC3\xC4\xC5\xC6\xC7\xC8\xC9\xCA\xD2\xD3\xD4\xD5\xD6\xD7\xD8\xD9\xDA\xE1\xE2\xE3\xE4\xE5\xE6\xE7\xE8\xE9\xEA\xF1\xF2\xF3\xF4\xF5\xF6\xF7\xF8\xF9\xFA\xFF\xDA\x00\x08\x01\x01\x00\x00?\x00\xFD\xFC\xFF\xD9"
        while True:
            yield b"--frame\r\n"
            yield b"Content-Type: image/jpeg\r\n\r\n" + blank_frame + b"\r\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
