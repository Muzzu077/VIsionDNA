"""
Activity event routes.
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_viewer
from app.models.models import ActivityEvent, User
from app.schemas.schemas import ActivityEventResponse

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("", response_model=list[ActivityEventResponse])
async def list_activities(
    person_id: UUID | None = None,
    camera_id: UUID | None = None,
    activity: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """List activity events with filters."""
    query = select(ActivityEvent)

    if person_id is not None:
        query = query.where(ActivityEvent.person_id == person_id)
    if camera_id is not None:
        query = query.where(ActivityEvent.camera_id == camera_id)
    if activity is not None:
        query = query.where(ActivityEvent.activity == activity)
    if start is not None:
        query = query.where(ActivityEvent.start_time >= start)
    if end is not None:
        query = query.where(ActivityEvent.start_time <= end)

    query = query.order_by(ActivityEvent.start_time.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()
