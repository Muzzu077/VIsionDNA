"""
System health and metrics routes.
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_viewer
from app.core.config import settings
from app.models.models import User
from app.schemas.schemas import SystemHealth

router = APIRouter(prefix="/system", tags=["system"])

_start_time = time.monotonic()


@router.get("/health", response_model=SystemHealth)
async def health_check(
    db: AsyncSession = Depends(get_db),
):
    """Return the health status of all system components."""
    uptime = time.monotonic() - _start_time

    # Database check
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    # Inference engine check (placeholder – real check would ping the engine)
    inference_status = "healthy" if settings.DEMO_MODE else "unknown"

    # Video pipeline
    video_status = "healthy" if settings.DEMO_MODE else "unknown"

    # WebSocket (always healthy if server is running)
    ws_status = "healthy"

    # Disk space check
    import shutil

    total, used, free = shutil.disk_usage("/")
    free_pct = free / total
    disk_status = "healthy" if free_pct > 0.1 else ("degraded" if free_pct > 0.05 else "unhealthy")

    overall = "healthy"
    if db_status == "unhealthy":
        overall = "unhealthy"
    elif any(s == "degraded" for s in [db_status, inference_status, video_status, disk_status]):
        overall = "degraded"

    return SystemHealth(
        status=overall,
        database=db_status,
        inference_engine=inference_status,
        video_pipeline=video_status,
        websocket=ws_status,
        disk_space=disk_status,
        uptime_seconds=round(uptime, 2),
        version=settings.VERSION,
    )


@router.get("/metrics")
async def system_metrics(
    _user: User = Depends(require_viewer),
):
    """Return runtime metrics."""
    import os
    import psutil  # noqa: F811 – optional, graceful fallback

    process = psutil.Process(os.getpid())
    mem = process.memory_info()

    return {
        "inference_fps": settings.INFERENCE_FPS,
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
        "prediction_horizon_seconds": settings.PREDICTION_HORIZON_SECONDS,
        "max_history_length": settings.MAX_HISTORY_LENGTH,
        "demo_mode": settings.DEMO_MODE,
        "simulation_mode": settings.SIMULATION_MODE,
        "process": {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_rss_mb": round(mem.rss / (1024 * 1024), 2),
            "memory_vms_mb": round(mem.vms / (1024 * 1024), 2),
            "threads": process.num_threads(),
        },
        "uptime_seconds": round(time.monotonic() - _start_time, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
