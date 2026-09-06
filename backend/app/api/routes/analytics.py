"""
Analytics routes.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_viewer
from app.models.models import (
    ActivityEvent,
    Camera,
    Person,
    Prediction,
    RiskEvent,
    User,
)
from app.schemas.schemas import ActivityAnalytics, RiskAnalytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/activities", response_model=ActivityAnalytics)
async def activity_analytics(
    start: datetime | None = None,
    end: datetime | None = None,
    environment_id: UUID | None = None,
    camera_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """Aggregate activity analytics."""
    now = datetime.now(timezone.utc)
    if end is None:
        end = now
    if start is None:
        start = end - timedelta(days=7)

    base = select(ActivityEvent).where(
        ActivityEvent.start_time.between(start, end)
    )
    if camera_id is not None:
        base = base.where(ActivityEvent.camera_id == camera_id)
    if environment_id is not None:
        base = base.join(Person, Person.id == ActivityEvent.person_id).where(
            Person.environment_id == environment_id
        )

    # Total count
    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Counts by activity
    activity_q = (
        select(ActivityEvent.activity, func.count().label("cnt"))
        .where(ActivityEvent.start_time.between(start, end))
    )
    if camera_id is not None:
        activity_q = activity_q.where(ActivityEvent.camera_id == camera_id)
    activity_q = activity_q.group_by(ActivityEvent.activity).order_by(func.count().desc())
    activity_rows = (await db.execute(activity_q)).all()
    activity_counts = {row[0]: row[1] for row in activity_rows}

    # Top activities
    top_activities = [
        {"activity": row[0], "count": row[1]} for row in activity_rows[:10]
    ]

    # Average confidence
    avg_q = select(func.avg(ActivityEvent.confidence)).where(
        ActivityEvent.start_time.between(start, end)
    )
    if camera_id is not None:
        avg_q = avg_q.where(ActivityEvent.camera_id == camera_id)
    avg_conf = (await db.execute(avg_q)).scalar() or 0.0

    # Hourly distribution
    hour_q = (
        select(
            func.extract("hour", ActivityEvent.start_time).label("hour"),
            func.count().label("cnt"),
        )
        .where(ActivityEvent.start_time.between(start, end))
        .group_by("hour")
        .order_by("hour")
    )
    if camera_id is not None:
        hour_q = hour_q.where(ActivityEvent.camera_id == camera_id)
    hour_rows = (await db.execute(hour_q)).all()
    hourly_distribution = [
        {"hour": int(row[0]), "count": row[1]} for row in hour_rows
    ]

    return ActivityAnalytics(
        total_events=total,
        activity_counts=activity_counts,
        hourly_distribution=hourly_distribution,
        top_activities=top_activities,
        avg_confidence=round(float(avg_conf), 4),
        period_start=start,
        period_end=end,
    )


@router.get("/risks", response_model=RiskAnalytics)
async def risk_analytics(
    start: datetime | None = None,
    end: datetime | None = None,
    environment_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """Aggregate risk analytics."""
    now = datetime.now(timezone.utc)
    if end is None:
        end = now
    if start is None:
        start = end - timedelta(days=7)

    base_filter = RiskEvent.timestamp.between(start, end)

    # Total
    total = (
        await db.execute(select(func.count()).where(base_filter).select_from(RiskEvent))
    ).scalar() or 0

    # Severity counts
    sev_q = (
        select(RiskEvent.severity, func.count().label("cnt"))
        .where(base_filter)
        .group_by(RiskEvent.severity)
    )
    sev_rows = (await db.execute(sev_q)).all()
    severity_counts = {row[0].value if hasattr(row[0], "value") else str(row[0]): row[1] for row in sev_rows}

    # Avg / max risk score
    stats_q = select(
        func.avg(RiskEvent.risk_score),
        func.max(RiskEvent.risk_score),
    ).where(base_filter)
    stats_row = (await db.execute(stats_q)).one()
    avg_score = float(stats_row[0] or 0.0)
    max_score = float(stats_row[1] or 0.0)

    # Risk trend (daily)
    trend_q = (
        select(
            func.date_trunc("day", RiskEvent.timestamp).label("day"),
            func.count().label("cnt"),
            func.avg(RiskEvent.risk_score).label("avg_score"),
        )
        .where(base_filter)
        .group_by("day")
        .order_by("day")
    )
    trend_rows = (await db.execute(trend_q)).all()
    risk_trend = [
        {
            "date": row[0].isoformat() if row[0] else None,
            "count": row[1],
            "avg_score": round(float(row[2] or 0), 4),
        }
        for row in trend_rows
    ]

    # Top risk types
    type_q = (
        select(RiskEvent.risk_type, func.count().label("cnt"))
        .where(base_filter)
        .group_by(RiskEvent.risk_type)
        .order_by(func.count().desc())
        .limit(10)
    )
    type_rows = (await db.execute(type_q)).all()
    top_risk_types = [{"risk_type": row[0], "count": row[1]} for row in type_rows]

    # Resolution rate
    resolved_count = (
        await db.execute(
            select(func.count())
            .where(base_filter)
            .where(RiskEvent.resolved_at.isnot(None))
            .select_from(RiskEvent)
        )
    ).scalar() or 0
    resolution_rate = (resolved_count / total) if total > 0 else 0.0

    # Average resolution time
    avg_res_q = select(
        func.avg(
            func.extract("epoch", RiskEvent.resolved_at - RiskEvent.timestamp)
        )
    ).where(base_filter).where(RiskEvent.resolved_at.isnot(None))
    avg_res = (await db.execute(avg_res_q)).scalar()

    return RiskAnalytics(
        total_events=total,
        severity_counts=severity_counts,
        avg_risk_score=round(avg_score, 4),
        max_risk_score=round(max_score, 4),
        risk_trend=risk_trend,
        top_risk_types=top_risk_types,
        resolution_rate=round(resolution_rate, 4),
        avg_resolution_time_seconds=round(float(avg_res), 2) if avg_res else None,
        period_start=start,
        period_end=end,
    )


@router.get("/predictions")
async def prediction_analytics(
    start: datetime | None = None,
    end: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """Aggregate prediction accuracy analytics."""
    now = datetime.now(timezone.utc)
    if end is None:
        end = now
    if start is None:
        start = end - timedelta(days=7)

    base_filter = Prediction.generated_at.between(start, end)

    total = (
        await db.execute(
            select(func.count()).where(base_filter).select_from(Prediction)
        )
    ).scalar() or 0

    # Accuracy (where was_correct is not null)
    evaluated = (
        await db.execute(
            select(func.count())
            .where(base_filter)
            .where(Prediction.was_correct.isnot(None))
            .select_from(Prediction)
        )
    ).scalar() or 0

    correct = (
        await db.execute(
            select(func.count())
            .where(base_filter)
            .where(Prediction.was_correct == True)  # noqa: E712
            .select_from(Prediction)
        )
    ).scalar() or 0

    accuracy = (correct / evaluated) if evaluated > 0 else None

    # By type
    type_q = (
        select(
            Prediction.prediction_type,
            func.count().label("total"),
            func.sum(case((Prediction.was_correct == True, 1), else_=0)).label("correct"),  # noqa: E712
        )
        .where(base_filter)
        .group_by(Prediction.prediction_type)
    )
    type_rows = (await db.execute(type_q)).all()
    by_type = [
        {
            "prediction_type": row[0],
            "total": row[1],
            "correct": int(row[2] or 0),
            "accuracy": round(int(row[2] or 0) / row[1], 4) if row[1] > 0 else None,
        }
        for row in type_rows
    ]

    return {
        "total_predictions": total,
        "evaluated": evaluated,
        "correct": correct,
        "accuracy": round(accuracy, 4) if accuracy is not None else None,
        "by_type": by_type,
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
    }


@router.get("/overview")
async def analytics_overview(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_viewer),
):
    """High-level system overview metrics."""
    now = datetime.now(timezone.utc)
    last_24h = now - timedelta(hours=24)

    total_persons = (
        await db.execute(select(func.count()).select_from(Person))
    ).scalar() or 0

    active_persons = (
        await db.execute(
            select(func.count())
            .where(Person.status == "ACTIVE")
            .select_from(Person)
        )
    ).scalar() or 0

    total_cameras = (
        await db.execute(select(func.count()).select_from(Camera))
    ).scalar() or 0

    online_cameras = (
        await db.execute(
            select(func.count())
            .where(Camera.status == "ONLINE")
            .select_from(Camera)
        )
    ).scalar() or 0

    recent_activities = (
        await db.execute(
            select(func.count())
            .where(ActivityEvent.start_time >= last_24h)
            .select_from(ActivityEvent)
        )
    ).scalar() or 0

    recent_risks = (
        await db.execute(
            select(func.count())
            .where(RiskEvent.timestamp >= last_24h)
            .select_from(RiskEvent)
        )
    ).scalar() or 0

    high_risk_count = (
        await db.execute(
            select(func.count())
            .where(RiskEvent.timestamp >= last_24h)
            .where(RiskEvent.severity.in_(["HIGH", "CRITICAL"]))
            .select_from(RiskEvent)
        )
    ).scalar() or 0

    return {
        "total_persons": total_persons,
        "active_persons": active_persons,
        "total_cameras": total_cameras,
        "online_cameras": online_cameras,
        "recent_activities_24h": recent_activities,
        "recent_risks_24h": recent_risks,
        "high_risk_count_24h": high_risk_count,
        "timestamp": now.isoformat(),
    }
