"""
Digital twin state routes.
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_viewer
from app.models.models import DigitalTwinState, Person, User
from app.schemas.schemas import DigitalTwinResponse

router = APIRouter(prefix="/digital-twins", tags=["digital-twins"])


@router.get("", response_model=list[DigitalTwinResponse])
async def list_digital_twins(
    environment_id: UUID | None = None,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """
    Get the latest digital twin state for each active person.

    If environment_id is given, only persons in that environment are included.
    """
    # Subquery: latest timestamp per person
    from sqlalchemy import func

    latest_sub = (
        select(
            DigitalTwinState.person_id,
            func.max(DigitalTwinState.timestamp).label("max_ts"),
        )
        .group_by(DigitalTwinState.person_id)
        .subquery()
    )

    query = (
        select(DigitalTwinState)
        .join(
            latest_sub,
            (DigitalTwinState.person_id == latest_sub.c.person_id)
            & (DigitalTwinState.timestamp == latest_sub.c.max_ts),
        )
    )

    if environment_id is not None:
        query = query.join(Person, Person.id == DigitalTwinState.person_id).where(
            Person.environment_id == environment_id
        )

    query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{person_id}", response_model=list[DigitalTwinResponse])
async def get_digital_twin(
    person_id: UUID,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """Get digital twin state history for a specific person."""
    person_result = await db.execute(select(Person).where(Person.id == person_id))
    if person_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    query = select(DigitalTwinState).where(DigitalTwinState.person_id == person_id)
    if start is not None:
        query = query.where(DigitalTwinState.timestamp >= start)
    if end is not None:
        query = query.where(DigitalTwinState.timestamp <= end)
    query = query.order_by(DigitalTwinState.timestamp.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
