"""
Person retrieval routes.
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, require_viewer
from app.models.models import (
    ActivityEvent,
    Person,
    PersonState,
    PersonStatus,
    RiskEvent,
    User,
)
from app.schemas.schemas import (
    ActivityEventResponse,
    PersonResponse,
    PersonStateResponse,
    RiskEventResponse,
)

router = APIRouter(prefix="/persons", tags=["persons"])


@router.get("", response_model=list[PersonResponse])
async def list_persons(
    environment_id: UUID | None = None,
    person_status: str | None = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """List persons with optional filters."""
    query = select(Person)
    if environment_id is not None:
        query = query.where(Person.environment_id == environment_id)
    if person_status is not None:
        try:
            query = query.where(Person.status == PersonStatus(person_status))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{person_status}'",
            )
    query = query.order_by(Person.last_seen.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """Get a single person by ID."""
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()
    if person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    return person


@router.get("/{person_id}/timeline", response_model=list[PersonStateResponse])
async def get_person_timeline(
    person_id: UUID,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(200, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """Get the state timeline for a person."""
    # Verify person exists
    person_result = await db.execute(select(Person).where(Person.id == person_id))
    if person_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    query = select(PersonState).where(PersonState.person_id == person_id)
    if start is not None:
        query = query.where(PersonState.timestamp >= start)
    if end is not None:
        query = query.where(PersonState.timestamp <= end)
    query = query.order_by(PersonState.timestamp.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{person_id}/risk-history", response_model=list[RiskEventResponse])
async def get_person_risk_history(
    person_id: UUID,
    start: datetime | None = None,
    end: datetime | None = None,
    severity: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """Get risk event history for a person."""
    person_result = await db.execute(select(Person).where(Person.id == person_id))
    if person_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    query = select(RiskEvent).where(RiskEvent.person_id == person_id)
    if start is not None:
        query = query.where(RiskEvent.timestamp >= start)
    if end is not None:
        query = query.where(RiskEvent.timestamp <= end)
    if severity is not None:
        query = query.where(RiskEvent.severity == severity)
    query = query.order_by(RiskEvent.timestamp.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
