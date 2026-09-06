from pydantic import BaseModel, Field
from typing import List, Dict, Tuple, Optional
from datetime import datetime

class BoundingBox(BaseModel):
    x: float
    y: float
    w: float
    h: float

class DetectionContext(BaseModel):
    frame_width: int
    frame_height: int
    timestamp: datetime = Field(default_factory=datetime.now)
    camera_id: str

class DetectedObject(BaseModel):
    id: Optional[str] = None
    class_name: str
    confidence: float
    bbox: BoundingBox
    center: Tuple[float, float]

class TrackedPerson(BaseModel):
    tracking_id: str
    bbox: BoundingBox
    state_history: List[dict] = Field(default_factory=list)

class PoseKeypoints(BaseModel):
    keypoints: Dict[str, List[float]]  # Mapping string to list of [x, y, confidence]

class ActivityResult(BaseModel):
    activity: str
    confidence: float
    metadata: dict = Field(default_factory=dict)
