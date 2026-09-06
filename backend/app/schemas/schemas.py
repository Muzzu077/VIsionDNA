"""
Pydantic v2 schemas for request / response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Auth ──────────────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── User ──────────────────────────────────────────────────────────────────────


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "VIEWER"


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ── Environment ───────────────────────────────────────────────────────────────


class EnvironmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None


class EnvironmentCreate(EnvironmentBase):
    pass


class EnvironmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None


class EnvironmentResponse(EnvironmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


# ── Camera ────────────────────────────────────────────────────────────────────


class CameraBase(BaseModel):
    name: str
    source_type: str
    source_url: Optional[str] = None
    fps: Optional[float] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None


class CameraCreate(CameraBase):
    environment_id: UUID


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    source_type: Optional[str] = None
    source_url: Optional[str] = None
    fps: Optional[float] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    is_active: Optional[bool] = None


class CameraResponse(CameraBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    environment_id: UUID
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ── Person ────────────────────────────────────────────────────────────────────


class PersonBase(BaseModel):
    tracking_id: str
    environment_id: UUID


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    status: Optional[str] = None


class PersonResponse(PersonBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_seen: datetime
    last_seen: datetime
    status: str


# ── PersonState ───────────────────────────────────────────────────────────────


class PersonStateBase(BaseModel):
    x: float
    y: float
    width: float
    height: float
    posture: Optional[str] = None
    activity: Optional[str] = None
    velocity: Optional[float] = 0.0
    direction: Optional[float] = 0.0
    confidence: float = 0.0


class PersonStateCreate(PersonStateBase):
    person_id: UUID


class PersonStateResponse(PersonStateBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    person_id: UUID
    timestamp: datetime


# ── ActivityEvent ─────────────────────────────────────────────────────────────


class ActivityEventBase(BaseModel):
    activity: str
    confidence: float
    model_version: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = Field(default=None, alias="metadata")


class ActivityEventCreate(ActivityEventBase):
    person_id: UUID
    camera_id: Optional[UUID] = None


class ActivityEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    person_id: UUID
    camera_id: Optional[UUID] = None
    activity: str
    confidence: float
    start_time: datetime
    end_time: Optional[datetime] = None
    model_version: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = Field(default=None, alias="metadata")


# ── DigitalTwinState ──────────────────────────────────────────────────────────


class DigitalTwinStateBase(BaseModel):
    current_activity: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    posture: Optional[str] = None
    movement_speed: Optional[float] = 0.0
    nearby_objects: Optional[List[Any]] = None
    zone: Optional[str] = None
    risk_score: Optional[float] = 0.0
    risk_level: Optional[str] = None
    state_json: Optional[Dict[str, Any]] = None


class DigitalTwinResponse(DigitalTwinStateBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    person_id: UUID
    timestamp: datetime


# ── RiskEvent ─────────────────────────────────────────────────────────────────


class RiskEventBase(BaseModel):
    risk_type: str
    risk_score: float
    severity: str
    confidence: float
    explanation: Optional[str] = None
    contributing_factors: Optional[List[Dict[str, Any]]] = None


class RiskEventCreate(RiskEventBase):
    person_id: UUID
    camera_id: Optional[UUID] = None


class RiskEventUpdate(BaseModel):
    status: Optional[str] = None
    resolved_at: Optional[datetime] = None


class RiskEventResponse(RiskEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    person_id: UUID
    camera_id: Optional[UUID] = None
    timestamp: datetime
    resolved_at: Optional[datetime] = None
    status: str


# ── Prediction ────────────────────────────────────────────────────────────────


class PredictionBase(BaseModel):
    prediction_type: str
    predicted_activity: Optional[str] = None
    predicted_risk: Optional[str] = None
    probability: float
    horizon_seconds: int
    explanation: Optional[str] = None
    model_version: Optional[str] = None


class PredictionCreate(PredictionBase):
    person_id: UUID


class PredictionResponse(PredictionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    person_id: UUID
    generated_at: datetime
    actual_outcome: Optional[str] = None
    was_correct: Optional[bool] = None


# ── Alert ─────────────────────────────────────────────────────────────────────


class AlertBase(BaseModel):
    severity: str
    title: str
    message: str
    recommended_action: Optional[str] = None


class AlertCreate(AlertBase):
    risk_event_id: UUID


class AlertResponse(AlertBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    risk_event_id: UUID
    acknowledged: bool
    acknowledged_by: Optional[UUID] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime


# ── Zone ──────────────────────────────────────────────────────────────────────


class ZoneBase(BaseModel):
    name: str
    zone_type: str
    polygon: List[Dict[str, float]]
    color: Optional[str] = "#FF0000"
    risk_level: int = 0


class ZoneCreate(ZoneBase):
    environment_id: UUID


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    zone_type: Optional[str] = None
    polygon: Optional[List[Dict[str, float]]] = None
    color: Optional[str] = None
    risk_level: Optional[int] = None
    is_active: Optional[bool] = None


class ZoneResponse(ZoneBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    environment_id: UUID
    is_active: bool
    created_at: datetime


# ── MonitoredObject ───────────────────────────────────────────────────────────


class MonitoredObjectBase(BaseModel):
    name: str
    object_type: str
    position_x: float
    position_y: float
    risk_radius: float = 1.0
    metadata_: Optional[Dict[str, Any]] = Field(default=None, alias="metadata")


class MonitoredObjectCreate(MonitoredObjectBase):
    environment_id: UUID


class MonitoredObjectResponse(MonitoredObjectBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    environment_id: UUID
    created_at: datetime


# ── ModelVersion ──────────────────────────────────────────────────────────────


class ModelVersionBase(BaseModel):
    name: str
    version: str
    model_type: str
    path: str
    metrics: Optional[Dict[str, Any]] = None


class ModelVersionCreate(ModelVersionBase):
    pass


class ModelVersionResponse(ModelVersionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime


# ── Composite / Utility Schemas ───────────────────────────────────────────────


class SystemHealth(BaseModel):
    status: str  # "healthy" | "degraded" | "unhealthy"
    database: str
    inference_engine: str
    video_pipeline: str
    websocket: str
    disk_space: str
    uptime_seconds: float
    version: str


class EventMessage(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    person_id: Optional[str] = None
    camera_id: Optional[str] = None
    activity: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    confidence: Optional[float] = None
    explanation: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RiskExplanation(BaseModel):
    total_score: float
    risk_level: str
    contributing_factors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of dicts with keys: name, score, description",
    )


class AnalyticsQuery(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    environment_id: Optional[UUID] = None
    camera_id: Optional[UUID] = None
    person_id: Optional[UUID] = None
    activity_types: Optional[List[str]] = None
    risk_levels: Optional[List[str]] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ActivityAnalytics(BaseModel):
    total_events: int
    activity_counts: Dict[str, int]
    hourly_distribution: List[Dict[str, Any]]
    top_activities: List[Dict[str, Any]]
    avg_confidence: float
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class RiskAnalytics(BaseModel):
    total_events: int
    severity_counts: Dict[str, int]
    avg_risk_score: float
    max_risk_score: float
    risk_trend: List[Dict[str, Any]]
    top_risk_types: List[Dict[str, Any]]
    resolution_rate: float
    avg_resolution_time_seconds: Optional[float] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
