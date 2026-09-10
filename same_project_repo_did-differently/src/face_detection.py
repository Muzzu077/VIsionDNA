"""
Module: face_detection.py
Provides robust OpenCV Haar Cascade face detection and bounding box utilities.
"""

import cv2
import os
import numpy as np
from typing import List, Tuple, Optional


class FaceDetector:
    """
    OpenCV Haar Cascade Face Detector.
    Detects single or multiple human faces in real-time camera frames.
    """

    def __init__(
        self,
        cascade_path: str = "haarcascade/haarcascade_frontalface_default.xml",
        scale_factor: float = 1.1,
        min_neighbors: int = 5,
        min_size: Tuple[int, int] = (40, 40),
    ):
        self.cascade_path = cascade_path
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size

        if not os.path.exists(self.cascade_path):
            # Fallback check
            alt_path = os.path.join(
                os.path.dirname(__file__), "..", "haarcascade", "haarcascade_frontalface_default.xml"
            )
            alt_path = os.path.abspath(alt_path)
            if os.path.exists(alt_path):
                self.cascade_path = alt_path
            else:
                raise FileNotFoundError(
                    f"Haar Cascade XML not found at '{cascade_path}'. "
                    "Ensure 'haarcascade/haarcascade_frontalface_default.xml' exists."
                )

        self.classifier = cv2.CascadeClassifier(self.cascade_path)
        if self.classifier.empty():
            raise RuntimeError(
                f"Failed to load Haar Cascade classifier from '{self.cascade_path}'."
            )

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in a BGR or Grayscale frame.

        Returns:
            List of tuples: [(x, y, w, h), ...]
        """
        if frame is None or frame.size == 0:
            return []

        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame

        # Optional histogram equalization for better detection in low light
        gray = cv2.equalizeHist(gray)

        faces = self.classifier.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size,
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        return [tuple(box) for box in faces]

    def extract_face_roi(
        self,
        frame: np.ndarray,
        bbox: Tuple[int, int, int, int],
        margin_percent: float = 0.0,
    ) -> Optional[np.ndarray]:
        """
        Safely extracts and crops the face Region of Interest (ROI) from the frame.
        Handles image boundary clipping safely.
        """
        if frame is None or frame.size == 0:
            return None

        h_img, w_img = frame.shape[:2]
        x, y, w, h = bbox

        if margin_percent > 0:
            margin_x = int(w * margin_percent)
            margin_y = int(h * margin_percent)
            x_min = max(0, x - margin_x)
            y_min = max(0, y - margin_y)
            x_max = min(w_img, x + w + margin_x)
            y_max = min(h_img, y + h + margin_y)
        else:
            x_min = max(0, x)
            y_min = max(0, y)
            x_max = min(w_img, x + w)
            y_max = min(h_img, y + h)

        if x_max <= x_min or y_max <= y_min:
            return None

        roi = frame[y_min:y_max, x_min:x_max]
        if roi.size == 0:
            return None

        return roi

    def draw_face_annotations(
        self,
        frame: np.ndarray,
        bbox: Tuple[int, int, int, int],
        label: Optional[str] = None,
        confidence: Optional[float] = None,
        color: Tuple[int, int, int] = (0, 255, 0),
    ) -> np.ndarray:
        """
        Draws professional bounding box and badge with emotion label and confidence.
        """
        x, y, w, h = bbox

        # Main bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        # Corner accents for a sleek modern UI look
        line_len = int(w * 0.15)
        thickness = 3
        # Top-left
        cv2.line(frame, (x, y), (x + line_len, y), color, thickness)
        cv2.line(frame, (x, y), (x, y + line_len), color, thickness)
        # Top-right
        cv2.line(frame, (x + w, y), (x + w - line_len, y), color, thickness)
        cv2.line(frame, (x + w, y), (x + w, y + line_len), color, thickness)
        # Bottom-left
        cv2.line(frame, (x, y + h), (x + line_len, y + h), color, thickness)
        cv2.line(frame, (x, y + h), (x, y + h - line_len), color, thickness)
        # Bottom-right
        cv2.line(frame, (x + w, y + h), (x + w - line_len, y + h), color, thickness)
        cv2.line(frame, (x + w, y + h), (x + w, y + h - line_len), color, thickness)

        if label:
            if confidence is not None:
                text = f"{label} ({confidence:.0f}%)"
            else:
                text = label

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.55
            font_thickness = 1
            (tw, th), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)

            # Badge background above box (or inside box if too close to top)
            badge_y1 = max(0, y - th - 10)
            badge_y2 = y
            if y - th - 10 < 0:
                badge_y1 = y
                badge_y2 = y + th + 10

            badge_x1 = x
            badge_x2 = min(frame.shape[1], x + tw + 14)

            cv2.rectangle(frame, (badge_x1, badge_y1), (badge_x2, badge_y2), color, -1)
            cv2.putText(
                frame,
                text,
                (badge_x1 + 6, badge_y2 - 5),
                font,
                font_scale,
                (0, 0, 0),  # Black text for high contrast on bright badge
                font_thickness,
                cv2.LINE_AA,
            )

        return frame
