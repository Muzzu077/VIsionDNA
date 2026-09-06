import cv2
import numpy as np
import logging
import math
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.ai.digital_twin.models import (
    Point2D, 
    ZonePolygon, 
    MonitoredObject,
    PersonTwin, 
    EnvironmentState
)

logger = logging.getLogger(__name__)

class DigitalTwinStateEngine:
    def __init__(self):
        self.zones: Dict[str, ZonePolygon] = {}
        self.objects: Dict[str, MonitoredObject] = {}
        
        # State tracking per person: tracking_id -> last_zone_id
        self.person_last_zone: Dict[str, str] = {}
        
    def add_zone(self, zone: ZonePolygon):
        self.zones[zone.id] = zone
        
    def add_object(self, obj: MonitoredObject):
        self.objects[obj.id] = obj

    def _determine_zone(self, pt: Point2D) -> Optional[str]:
        # cv2.pointPolygonTest requires points as a numpy array of shape (N, 1, 2)
        test_pt = (pt.x, pt.y)
        for zone_id, zone in self.zones.items():
            pts = np.array([[p.x, p.y] for p in zone.points], dtype=np.float32)
            # Returns +1 if inside, 0 if on boundary, -1 if outside
            dist = cv2.pointPolygonTest(pts, test_pt, False)
            if dist >= 0:
                return zone.id
        return None

    def _calculate_distance(self, p1: Point2D, p2: Point2D) -> float:
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def update_from_pipeline(self, pipeline_output: dict) -> List[dict]:
        """
        Inputs: pipeline_output dict should contain key "tracked_persons" and optionally "activities".
        
        In the pipeline, we augment tracked_persons with 'activity' and 'features'. 
        Or pipeline_output is dict with timestamp, camera_id, and rich per-person details.
        
        Returns:
            List[dict]: Fully realized DigitalTwinState dictionary representation for each person.
        """
        timestamp_str = pipeline_output.get("timestamp", datetime.now().isoformat())
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
        except ValueError:
            timestamp = datetime.now()
            
        tracked_persons_data = pipeline_output.get("tracked_persons", [])
        
        persons_twins = []
        transitions = []
        
        for person_data in tracked_persons_data:
            track_id = person_data.get("tracking_id", "")
            if not track_id:
                continue
                
            # Get center or bottom-center (feet) for ground-plane projection
            # Here, we use center of bbox, assuming a 2D digital twin mapped to image coords
            bbox = person_data.get("bbox", {})
            x = bbox.get("x", 0.0)
            y = bbox.get("y", 0.0)
            w = bbox.get("w", 0.0)
            h = bbox.get("h", 0.0)
            
            # Using bottom of bbox for feet location instead of center
            pt = Point2D(x=x + w / 2, y=y + h)
            
            activity = person_data.get("activity", "standing")
            confidence = person_data.get("activity_confidence", 0.0)
            
            # 1. Determine zone
            current_zone_id = self._determine_zone(pt)
            
            # 2. Identify zone transitions
            last_zone_id = self.person_last_zone.get(track_id)
            if last_zone_id != current_zone_id:
                # Transition occurred
                transitions.append({
                    "tracking_id": track_id,
                    "from_zone": last_zone_id,
                    "to_zone": current_zone_id,
                    "timestamp": timestamp.isoformat()
                })
                self.person_last_zone[track_id] = current_zone_id
                
            # 3. Calculate distances to objects
            distances = {}
            for obj_id, obj in self.objects.items():
                distances[obj_id] = self._calculate_distance(pt, obj.position)
                
            # 4. Create Twin Model
            person_twin = PersonTwin(
                tracking_id=track_id,
                position=pt,
                activity=activity,
                activity_confidence=confidence,
                current_zone=current_zone_id,
                distances_to_objects=distances
            )
            persons_twins.append(person_twin)
            
        # Return state as list of dicts for each person for persistence/broadcast
        return [pt.model_dump() for pt in persons_twins]
