from abc import ABC, abstractmethod
import numpy as np
from app.ai.models import TrackedPerson, PoseKeypoints

class BasePoseEstimator(ABC):
    @abstractmethod
    async def estimate_pose(self, frame: np.ndarray, person: TrackedPerson) -> PoseKeypoints:
        """
        Estimate pose keypoints for a tracked person.
        
        Args:
            frame (np.ndarray): The input image frame.
            person (TrackedPerson): The tracked person to estimate pose for.
            
        Returns:
            PoseKeypoints: The estimated pose keypoints.
        """
        pass
