import numpy as np
from typing import List, Dict, Any
from app.ai.models import TrackedPerson

class FeatureExtractor:
    def __init__(self, window_size: int = 10, fps: int = 30):
        self.window_size = window_size
        self.fps = fps

    def extract(self, person_history: List[TrackedPerson]) -> dict:
        """
        Given a temporal sequence of tracking and pose data for a person, compute:
        - moving_average_velocity
        - direction_vector
        - posture_heuristic
        - temporal_variance
        """
        if not person_history:
            return {
                "moving_average_velocity": 0.0,
                "direction_vector": [0.0, 0.0],
                "posture_heuristic": "unknown",
                "temporal_variance": 0.0,
                "aspect_ratio": 1.0,
                "width": 0.0,
                "height": 0.0
            }

        # Work on the recent history up to window_size
        history = person_history[-self.window_size:]
        current_person = history[-1]
        
        centers = []
        timestamps = []
        for p in history:
            # We assume state_history holds standard center and time. If not, fallback to current bbox.
            # actually we can just use the p.bbox center
            cx = p.bbox.x + p.bbox.w / 2
            cy = p.bbox.y + p.bbox.h / 2
            centers.append([cx, cy])
            # if we have timestamp in state, we might use it, but assume uniform fps for now
            
        centers = np.array(centers)
        
        # Calculate velocity
        moving_average_velocity = 0.0
        direction_vector = [0.0, 0.0]
        temporal_variance = 0.0
        
        if len(centers) > 1:
            diffs = np.diff(centers, axis=0)
            distances = np.linalg.norm(diffs, axis=1)
            # multiply by fps to get units per second
            velocities = distances * self.fps
            moving_average_velocity = float(np.mean(velocities))
            
            # direction vector based on the first and last point
            total_displacement = centers[-1] - centers[0]
            norm = np.linalg.norm(total_displacement)
            if norm > 0:
                direction_vector = (total_displacement / norm).tolist()
                
            # temporal variance
            temporal_variance = float(np.var(distances))
            
        # Posture heuristic based on bounding box
        aspect_ratio = current_person.bbox.w / current_person.bbox.h if current_person.bbox.h > 0 else 1.0
        
        posture_heuristic = "standing"
        if aspect_ratio > 1.2:
            posture_heuristic = "fallen_or_lying"
        elif 0.8 < aspect_ratio <= 1.2:
            posture_heuristic = "sitting_or_bending"
        else:
            posture_heuristic = "standing"
            
        return {
            "moving_average_velocity": moving_average_velocity,
            "direction_vector": direction_vector,
            "posture_heuristic": posture_heuristic,
            "temporal_variance": temporal_variance,
            "aspect_ratio": aspect_ratio,
            "width": current_person.bbox.w,
            "height": current_person.bbox.h
        }
