from abc import ABC, abstractmethod
from typing import List
import numpy as np
from app.ai.models import DetectedObject, TrackedPerson

class BaseTracker(ABC):
    @abstractmethod
    def update(self, detections: List[DetectedObject], frame: np.ndarray) -> List[TrackedPerson]:
        """
        Update the tracker with new detections.
        
        Args:
            detections (List[DetectedObject]): The list of current detections.
            frame (np.ndarray): The current frame (useful for optical flow based trackers).
            
        Returns:
            List[TrackedPerson]: A list of tracked persons with assigned IDs.
        """
        pass
