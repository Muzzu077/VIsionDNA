from collections import deque, Counter
from typing import List, Dict, Any
from app.ai.models import TrackedPerson, ActivityResult
from app.ai.activity.base import BaseActivityRecognizer

class HeuristicActivityRecognizer(BaseActivityRecognizer):
    def __init__(self, smoothing_window: int = 5):
        self.smoothing_window = smoothing_window
        self.history: Dict[str, deque] = {}
        self.walk_threshold = 50.0  # arbitrary unit/s
        self.run_threshold = 150.0

    async def recognize(self, features: dict, tracking_history: List[TrackedPerson]) -> ActivityResult:
        if not tracking_history:
            return ActivityResult(activity="standing", confidence=0.0)
            
        current_person = tracking_history[-1]
        track_id = current_person.tracking_id
        
        # 1. Raw classification based on heuristics
        vel = features.get("moving_average_velocity", 0.0)
        aspect_ratio = features.get("aspect_ratio", 1.0)
        
        raw_activity = "standing"
        
        if aspect_ratio > 1.2:
            if vel < self.walk_threshold:
                raw_activity = "lying down"
            else:
                raw_activity = "running" # unusual, but maybe sliding?
        elif aspect_ratio > 0.8:
            if vel > self.walk_threshold:
                raw_activity = "walking" # or running
            else:
                # height roughly equal to width could be bending or sitting
                if aspect_ratio > 1.0:
                    raw_activity = "bending"
                else:
                    raw_activity = "sitting"
        else:
            # tall and narrow
            if vel > self.run_threshold:
                raw_activity = "running"
            elif vel > self.walk_threshold:
                raw_activity = "walking"
            else:
                raw_activity = "standing"
                
        # 2. Temporal Smoothing
        if track_id not in self.history:
            self.history[track_id] = deque(maxlen=self.smoothing_window)
            
        self.history[track_id].append(raw_activity)
        
        # Majority vote
        counts = Counter(self.history[track_id])
        smoothed_activity, count = counts.most_common(1)[0]
        confidence = count / max(1, len(self.history[track_id]))
        
        return ActivityResult(
            activity=smoothed_activity,
            confidence=confidence,
            metadata={
                "velocity": vel,
                "aspect_ratio": aspect_ratio,
                "raw_activity": raw_activity
            }
        )
