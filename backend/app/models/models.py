"""
SQLAlchemy ORM models for VisionDNA.
"""

import enum
from datetime import datetime

import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


# ── Enumerations ──────────────────────────────────────────────────────────────


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"


class CameraSourceType(str, enum.Enum):
    WEBCAM = "WEBCAM"
    UPLOAD = "UPLOAD"
    RTSP = "RTSP"
    HTTP = "HTTP"


class CameraStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"


class PersonStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOST = "LOST"


class RiskSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskEventStatus(str, enum.Enum):
    DETECTED = "DETECTED"
    EVALUATING = "EVALUATING"
    CONFIRMED = "CONFIRMED"
    ALERTED = "ALERTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class AlertSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ZoneType(str, enum.Enum):
    SAFE = "SAFE"
    RESTRICTED = "RESTRICTED"
    HIGH_RISK = "HIGH_RISK"
    MONITORED = "MONITORED"


# ── Models ────────────────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    acknowledged_alerts = relationship("Alert", back_populates="acknowledged_by_user", foreign_keys="Alert.acknowledged_by")


class Environment(Base):
    __tablename__ = "environments"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    configuration = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    cameras = relationship("Camera", back_populates="environment", cascade="all, delete-orphan")
    persons = relationship("Person", back_populates="environment", cascade="all, delete-orphan")
    zones = relationship("Zone", back_populates="environment", cascade="all, delete-orphan")
    monitored_objects = relationship("MonitoredObject", back_populates="environment", cascade="all, delete-orphan")


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    environment_id = Column(Uuid, ForeignKey("environments.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(Enum(CameraSourceType), nullable=False)
    source_url = Column(String(1024), nullable=True)
    status = Column(Enum(CameraStatus), default=CameraStatus.OFFLINE, nullable=False)
    fps = Column(Float, nullable=True)
    resolution_width = Column(Integer, nullable=True)
    resolution_height = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    environment = relationship("Environment", back_populates="cameras")
    activity_events = relationship("ActivityEvent", back_populates="camera", cascade="all, delete-orphan")
    risk_events = relationship("RiskEvent", back_populates="camera", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_cameras_environment_status", "environment_id", "status"),
    )


class Person(Base):
    __tablename__ = "persons"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    tracking_id = Column(String(255), nullable=False, index=True)
    environment_id = Column(Uuid, ForeignKey("environments.id", ondelete="CASCADE"), nullable=False, index=True)
    first_seen = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(Enum(PersonStatus), default=PersonStatus.ACTIVE, nullable=False)

    # Relationships
    environment = relationship("Environment", back_populates="persons")
    states = relationship("PersonState", back_populates="person", cascade="all, delete-orphan", order_by="PersonState.timestamp.desc()")
    activity_events = relationship("ActivityEvent", back_populates="person", cascade="all, delete-orphan")
    digital_twin_states = relationship("DigitalTwinState", back_populates="person", cascade="all, delete-orphan")
    risk_events = relationship("RiskEvent", back_populates="person", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="person", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_persons_env_status", "environment_id", "status"),
        Index("ix_persons_tracking", "tracking_id", "environment_id"),
    )


class PersonState(Base):
    __tablename__ = "person_states"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    person_id = Column(Uuid, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    posture = Column(String(64), nullable=True)
    activity = Column(String(128), nullable=True)
    velocity = Column(Float, nullable=True, default=0.0)
    direction = Column(Float, nullable=True, default=0.0)
    confidence = Column(Float, nullable=False, default=0.0)

    # Relationships
    person = relationship("Person", back_populates="states")

    __table_args__ = (
        Index("ix_person_states_person_ts", "person_id", "timestamp"),
    )


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    person_id = Column(Uuid, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True)
    camera_id = Column(Uuid, ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True, index=True)
    activity = Column(String(128), nullable=False)
    confidence = Column(Float, nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    model_version = Column(String(64), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True, default=dict)

    # Relationships
    person = relationship("Person", back_populates="activity_events")
    camera = relationship("Camera", back_populates="activity_events")

    __table_args__ = (
        Index("ix_activity_events_person_time", "person_id", "start_time"),
        Index("ix_activity_events_camera_time", "camera_id", "start_time"),
        Index("ix_activity_events_activity", "activity"),
    )


class DigitalTwinState(Base):
    __tablename__ = "digital_twin_states"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    person_id = Column(Uuid, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    current_activity = Column(String(128), nullable=True)
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    posture = Column(String(64), nullable=True)
    movement_speed = Column(Float, nullable=True, default=0.0)
    nearby_objects = Column(JSON, nullable=True, default=list)
    zone = Column(String(128), nullable=True)
    risk_score = Column(Float, nullable=True, default=0.0)
    risk_level = Column(String(32), nullable=True)
    state_json = Column(JSON, nullable=True, default=dict)

    # Relationships
    person = relationship("Person", back_populates="digital_twin_states")

    __table_args__ = (
        Index("ix_digital_twin_person_ts", "person_id", "timestamp"),
    )


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    person_id = Column(Uuid, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True)
    camera_id = Column(Uuid, ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True, index=True)
    risk_type = Column(String(128), nullable=False)
    risk_score = Column(Float, nullable=False)
    severity = Column(Enum(RiskSeverity), nullable=False)
    confidence = Column(Float, nullable=False)
    explanation = Column(Text, nullable=True)
    contributing_factors = Column(JSON, nullable=True, default=list)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(RiskEventStatus), default=RiskEventStatus.DETECTED, nullable=False)

    # Relationships
    person = relationship("Person", back_populates="risk_events")
    camera = relationship("Camera", back_populates="risk_events")
    alerts = relationship("Alert", back_populates="risk_event", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_risk_events_person_ts", "person_id", "timestamp"),
        Index("ix_risk_events_severity", "severity"),
        Index("ix_risk_events_status", "status"),
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    person_id = Column(Uuid, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True)
    prediction_type = Column(String(64), nullable=False)
    predicted_activity = Column(String(128), nullable=True)
    predicted_risk = Column(String(128), nullable=True)
    probability = Column(Float, nullable=False)
    horizon_seconds = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)
    model_version = Column(String(64), nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    actual_outcome = Column(String(128), nullable=True)
    was_correct = Column(Boolean, nullable=True)

    # Relationships
    person = relationship("Person", back_populates="predictions")

    __table_args__ = (
        Index("ix_predictions_person_ts", "person_id", "generated_at"),
        Index("ix_predictions_type", "prediction_type"),
    )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    risk_event_id = Column(Uuid, ForeignKey("risk_events.id", ondelete="CASCADE"), nullable=False, index=True)
    severity = Column(Enum(AlertSeverity), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    recommended_action = Column(String(512), nullable=True)
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    risk_event = relationship("RiskEvent", back_populates="alerts")
    acknowledged_by_user = relationship("User", back_populates="acknowledged_alerts", foreign_keys=[acknowledged_by])

    __table_args__ = (
        Index("ix_alerts_severity_ack", "severity", "acknowledged"),
    )


class Zone(Base):
    __tablename__ = "zones"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    environment_id = Column(Uuid, ForeignKey("environments.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    zone_type = Column(Enum(ZoneType), nullable=False)
    polygon = Column(JSON, nullable=False)
    color = Column(String(32), nullable=True, default="#FF0000")
    risk_level = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    environment = relationship("Environment", back_populates="zones")


class MonitoredObject(Base):
    __tablename__ = "monitored_objects"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    environment_id = Column(Uuid, ForeignKey("environments.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    object_type = Column(String(128), nullable=False)
    position_x = Column(Float, nullable=False)
    position_y = Column(Float, nullable=False)
    risk_radius = Column(Float, nullable=False, default=1.0)
    metadata_ = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    environment = relationship("Environment", back_populates="monitored_objects")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    version = Column(String(64), nullable=False)
    model_type = Column(String(128), nullable=False)
    path = Column(String(1024), nullable=False)
    metrics = Column(JSON, nullable=True, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_model_versions_name_active", "name", "is_active"),
    )
