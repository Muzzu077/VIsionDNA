from pydantic import BaseModel, Field
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

class Point2D(BaseModel):
    x: float
    y: float

class ZonePolygon(BaseModel):
    id: str
    name: str
    type: str # e.g., "safe", "restricted", "danger"
    points: List[Point2D]

class MonitoredObject(BaseModel):
    id: str
    type: str
    position: Point2D
    status: str = "active"

class PersonTwin(BaseModel):
    tracking_id: str
    position: Point2D
    activity: str
    activity_confidence: float
    current_zone: Optional[str] = None
    distances_to_objects: Dict[str, float] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EnvironmentState(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    persons: List[PersonTwin] = Field(default_factory=list)
    zones: List[ZonePolygon] = Field(default_factory=list)
    objects: List[MonitoredObject] = Field(default_factory=list)
    zone_transitions: List[Dict[str, Any]] = Field(default_factory=list)

class SystemState(BaseModel):
    environment_state: EnvironmentState
    # Can include sensor health, system alerts, etc.
    active_alerts: List[Dict[str, Any]] = Field(default_factory=list)
