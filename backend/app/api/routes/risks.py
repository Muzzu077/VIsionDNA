"""
Risk event routes.
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_operator, require_viewer
from app.models.models import RiskEvent, RiskEventStatus, User
from app.schemas.schemas import RiskEventResponse

router = APIRouter(prefix="/risks", tags=["risks"])


@router.get("", response_model=list[RiskEventResponse])
async def list_risks(
    person_id: UUID | None = None,
    camera_id: UUID | None = None,
    severity: str | None = None,
    risk_status: str | None = Query(None, alias="status"),
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """List risk events with filters."""
    query = select(RiskEvent)

    if person_id is not None:
        query = query.where(RiskEvent.person_id == person_id)
    if camera_id is not None:
        query = query.where(RiskEvent.camera_id == camera_id)
    if severity is not None:
        query = query.where(RiskEvent.severity == severity)
    if risk_status is not None:
        try:
            query = query.where(RiskEvent.status == RiskEventStatus(risk_status))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{risk_status}'",
            )
    if start is not None:
        query = query.where(RiskEvent.timestamp >= start)
    if end is not None:
        query = query.where(RiskEvent.timestamp <= end)

    query = query.order_by(RiskEvent.timestamp.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{risk_id}", response_model=RiskEventResponse)
async def get_risk(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """Get a single risk event by ID."""
    result = await db.execute(select(RiskEvent).where(RiskEvent.id == risk_id))
    risk = result.scalar_one_or_none()
    if risk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk event not found")
    return risk


@router.put("/{risk_id}/acknowledge", response_model=RiskEventResponse)
async def acknowledge_risk(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    """Acknowledge a risk event (sets status to ACKNOWLEDGED)."""
    result = await db.execute(select(RiskEvent).where(RiskEvent.id == risk_id))
    risk = result.scalar_one_or_none()
    if risk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk event not found")

    risk.status = RiskEventStatus.ACKNOWLEDGED
    await db.flush()
    await db.refresh(risk)
    return risk
