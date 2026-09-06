"""
Zone CRUD routes.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_operator, require_viewer
from app.models.models import Environment, User, Zone, ZoneType
from app.schemas.schemas import ZoneCreate, ZoneResponse, ZoneUpdate

router = APIRouter(prefix="/zones", tags=["zones"])


@router.get("", response_model=list[ZoneResponse])
async def list_zones(
    environment_id: UUID | None = None,
    zone_type: str | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """List zones with optional filters."""
    query = select(Zone)
    if environment_id is not None:
        query = query.where(Zone.environment_id == environment_id)
    if zone_type is not None:
        try:
            query = query.where(Zone.zone_type == ZoneType(zone_type))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid zone_type '{zone_type}'",
            )
    if is_active is not None:
        query = query.where(Zone.is_active == is_active)
    query = query.order_by(Zone.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{zone_id}", response_model=ZoneResponse)
async def get_zone(
    zone_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """Get a single zone by ID."""
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    return zone


@router.post("", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_zone(
    payload: ZoneCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator),
):
    """Create a new zone."""
    env_result = await db.execute(
        select(Environment).where(Environment.id == payload.environment_id)
    )
    if env_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment not found",
        )

    try:
        zt = ZoneType(payload.zone_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid zone_type '{payload.zone_type}'",
        )

    zone = Zone(
        environment_id=payload.environment_id,
        name=payload.name,
        zone_type=zt,
        polygon=payload.polygon,
        color=payload.color,
        risk_level=payload.risk_level,
    )
    db.add(zone)
    await db.flush()
    await db.refresh(zone)
    return zone


@router.put("/{zone_id}", response_model=ZoneResponse)
async def update_zone(
    zone_id: UUID,
    payload: ZoneUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator),
):
    """Update an existing zone."""
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "zone_type" in update_data and update_data["zone_type"] is not None:
        try:
            update_data["zone_type"] = ZoneType(update_data["zone_type"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid zone_type '{update_data['zone_type']}'",
            )

    for field, value in update_data.items():
        setattr(zone, field, value)

    await db.flush()
    await db.refresh(zone)
    return zone


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zone(
    zone_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator),
):
    """Delete a zone."""
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    await db.delete(zone)
    await db.flush()
