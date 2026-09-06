from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.ai.models import TrackedPerson, ActivityResult

class BaseActivityRecognizer(ABC):
    @abstractmethod
    async def recognize(self, features: dict, tracking_history: List[TrackedPerson]) -> ActivityResult:
        """
        Recognize activity for a person based on extracted features and history.
        """
        pass
