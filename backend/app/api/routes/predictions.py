"""
Prediction routes.
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_viewer
from app.models.models import Prediction, User
from app.schemas.schemas import PredictionResponse

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("", response_model=list[PredictionResponse])
async def list_predictions(
    person_id: UUID | None = None,
    prediction_type: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """List predictions with filters."""
    query = select(Prediction)

    if person_id is not None:
        query = query.where(Prediction.person_id == person_id)
    if prediction_type is not None:
        query = query.where(Prediction.prediction_type == prediction_type)
    if start is not None:
        query = query.where(Prediction.generated_at >= start)
    if end is not None:
        query = query.where(Prediction.generated_at <= end)

    query = query.order_by(Prediction.generated_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()
