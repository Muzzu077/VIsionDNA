import logging
import numpy as np
from typing import Dict, List

from app.ai.pose.base import BasePoseEstimator
from app.ai.models import TrackedPerson, PoseKeypoints

logger = logging.getLogger(__name__)

class MediaPipePoseEstimator(BasePoseEstimator):
    def __init__(self):
        self.use_dummy = False
        try:
            import mediapipe as mp
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            logger.info("Loaded MediaPipe Pose model")
        except ImportError:
            logger.info("MediaPipe is not installed; pose estimation is unavailable outside simulation mode.")
            self.use_dummy = True
        except Exception as e:
            logger.warning(f"Failed to load MediaPipe Pose: {e}. Falling back to dummy estimator.")
            self.use_dummy = True

    async def estimate_pose(self, frame: np.ndarray, person: TrackedPerson) -> PoseKeypoints:
        if self.use_dummy:
            # Generate fake keypoints for simulation based on person bbox
            return self._generate_dummy_keypoints(person)
            
        # Crop frame to person bbox to improve pose estimation
        bbox = person.bbox
        h, w, _ = frame.shape
        x1 = max(0, int(bbox.x))
        y1 = max(0, int(bbox.y))
        x2 = min(w, int(bbox.x + bbox.w))
        y2 = min(h, int(bbox.y + bbox.h))
        
        # Ensure valid crop
        if x2 <= x1 or y2 <= y1:
            return self._generate_dummy_keypoints(person)
            
        person_crop = frame[y1:y2, x1:x2]
        
        # Convert to RGB as MediaPipe expects RGB
        import cv2
        try:
            person_crop_rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
            results = self.pose.process(person_crop_rgb)
        except Exception as e:
            logger.error(f"MediaPipe processing error: {e}")
            return self._generate_dummy_keypoints(person)
            
        keypoints_dict: Dict[str, List[float]] = {}
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            # MediaPipe landmarks map (subset):
            # 0: nose, 11: left_shoulder, 12: right_shoulder, 13: left_elbow, 14: right_elbow, etc.
            names = {
                0: "nose",
                11: "left_shoulder",
                12: "right_shoulder",
                13: "left_elbow",
                14: "right_elbow",
                15: "left_wrist",
                16: "right_wrist",
                23: "left_hip",
                24: "right_hip",
                25: "left_knee",
                26: "right_knee",
                27: "left_ankle",
                28: "right_ankle"
            }
            
            crop_w = x2 - x1
            crop_h = y2 - y1
            
            for idx, name in names.items():
                if idx < len(landmarks):
                    lm = landmarks[idx]
                    # Convert normalized coordinates back to absolute image coordinates
                    abs_x = x1 + lm.x * crop_w
                    abs_y = y1 + lm.y * crop_h
                    keypoints_dict[name] = [abs_x, abs_y, lm.visibility]
                    
            return PoseKeypoints(keypoints=keypoints_dict)
            
        return self._generate_dummy_keypoints(person)

    def _generate_dummy_keypoints(self, person: TrackedPerson) -> PoseKeypoints:
        """Fallback to generate mock keypoints based on bounding box."""
        b = person.bbox
        # Rough skeleton relative to bbox
        keypoints = {
            "nose": [b.x + b.w/2, b.y + b.h*0.1, 0.9],
            "left_shoulder": [b.x + b.w*0.2, b.y + b.h*0.2, 0.8],
            "right_shoulder": [b.x + b.w*0.8, b.y + b.h*0.2, 0.8],
            "left_hip": [b.x + b.w*0.3, b.y + b.h*0.5, 0.7],
            "right_hip": [b.x + b.w*0.7, b.y + b.h*0.5, 0.7],
        }
        return PoseKeypoints(keypoints=keypoints)
