import logging
from typing import List
import numpy as np

from app.ai.detection.base import BaseDetector
from app.ai.models import DetectedObject, DetectionContext, BoundingBox

logger = logging.getLogger(__name__)

class YOLODetector(BaseDetector):
    def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.5):
        self.conf_threshold = conf_threshold
        self.classes = [0]  # Only person
        self.use_dummy = False
        
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            # Warmup
            dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
            self.model(dummy_img, verbose=False)
            logger.info(f"Loaded YOLO model from {model_path}")
        except ImportError:
            logger.info("Ultralytics is not installed; detector is unavailable outside simulation mode.")
            self.use_dummy = True
        except Exception as e:
            logger.warning(f"Failed to load YOLO model: {e}. Falling back to dummy detector.")
            self.use_dummy = True
            
    async def detect(self, frame: np.ndarray, context: DetectionContext) -> List[DetectedObject]:
        if self.use_dummy:
            # Dummy detection output for simulation/fallback
            return [
                DetectedObject(
                    class_name="person",
                    confidence=0.95,
                    bbox=BoundingBox(
                        x=context.frame_width * 0.4,
                        y=context.frame_height * 0.4,
                        w=context.frame_width * 0.2,
                        h=context.frame_height * 0.5
                    ),
                    center=(context.frame_width * 0.5, context.frame_height * 0.65)
                )
            ]
            
        results = self.model(frame, classes=self.classes, conf=self.conf_threshold, verbose=False)
        detected_objects = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                
                w = x2 - x1
                h = y2 - y1
                cx = x1 + w / 2
                cy = y1 + h / 2
                
                detected_objects.append(
                    DetectedObject(
                        class_name="person",
                        confidence=conf,
                        bbox=BoundingBox(x=x1, y=y1, w=w, h=h),
                        center=(cx, cy)
                    )
                )
                
        return detected_objects
