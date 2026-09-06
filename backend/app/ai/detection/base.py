from abc import ABC, abstractmethod
from typing import List
import numpy as np
from app.ai.models import DetectedObject, DetectionContext

class BaseDetector(ABC):
    @abstractmethod
    async def detect(self, frame: np.ndarray, context: DetectionContext) -> List[DetectedObject]:
        """
        Detect objects in a frame.
        
        Args:
            frame (np.ndarray): The input image frame.
            context (DetectionContext): Context information about the frame.
            
        Returns:
            List[DetectedObject]: A list of detected objects.
        """
        pass
