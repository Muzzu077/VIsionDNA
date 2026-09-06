"""
Import all ORM models so Alembic and the application can discover them.
"""

from app.models.models import (  # noqa: F401
    ActivityEvent,
    Alert,
    AlertSeverity,
    Camera,
    CameraSourceType,
    CameraStatus,
    DigitalTwinState,
    Environment,
    ModelVersion,
    MonitoredObject,
    Person,
    PersonState,
    PersonStatus,
    Prediction,
    RiskEvent,
    RiskEventStatus,
    RiskSeverity,
    User,
    UserRole,
    Zone,
    ZoneType,
)
