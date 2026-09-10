"""
Module: emotion_model.py
Loads pre-trained emotion recognition neural network models (ONNX / OpenCV DNN)
and performs inference to predict emotions and confidence scores.
"""

import os
import cv2
import numpy as np
from typing import Dict, Tuple, Optional, List

from src.preprocessing import preprocess_face_for_model, compute_softmax


# Standard 8-class FERPlus mapping
FERPLUS_CLASSES = [
    "Neutral",
    "Happy",
    "Surprise",
    "Sad",
    "Angry",
    "Disgust",
    "Fear",
    "Contempt",
]

# Standard 7-class FER2013 mapping
FER2013_CLASSES = [
    "Angry",
    "Disgust",
    "Fear",
    "Happy",
    "Sad",
    "Surprise",
    "Neutral",
]

# Color palette (BGR) for drawing emotion bounding boxes & badges
EMOTION_COLORS = {
    "Happy": (0, 255, 0),       # Green
    "Surprise": (0, 255, 255),  # Yellow
    "Neutral": (200, 200, 200), # Light Gray
    "Sad": (255, 140, 0),       # Blue / Amber
    "Angry": (0, 0, 255),       # Red
    "Disgust": (0, 140, 255),   # Orange
    "Fear": (255, 0, 255),      # Purple / Magenta
    "Contempt": (180, 180, 180),# Gray
    "Uncertain": (128, 128, 128)# Muted Gray
}


class EmotionClassifier:
    """
    Emotion Recognition Model Loader & Inference Engine.
    Supports ONNX Runtime and OpenCV DNN backends.
    """

    def __init__(
        self,
        model_path: str = "models/emotion_ferplus.onnx",
        classes: Optional[List[str]] = None,
        confidence_threshold: float = 35.0,
    ):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.backend = None
        self.session = None
        self.net = None

        if not os.path.exists(self.model_path):
            alt_path = os.path.join(
                os.path.dirname(__file__), "..", "models", os.path.basename(model_path)
            )
            alt_path = os.path.abspath(alt_path)
            if os.path.exists(alt_path):
                self.model_path = alt_path
            else:
                raise FileNotFoundError(
                    f"Emotion model file not found at '{model_path}'. "
                    "Please verify the model exists in the 'models/' directory."
                )

        # Assign classes
        if classes is not None:
            self.classes = classes
        elif "ferplus" in self.model_path.lower():
            self.classes = FERPLUS_CLASSES
        else:
            self.classes = FER2013_CLASSES

        self._load_model()

    def _load_model(self):
        """
        Loads the model using ONNXRuntime if available, falling back to cv2.dnn.
        """
        try:
            import onnxruntime as ort
            self.session = ort.InferenceSession(self.model_path)
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            self.backend = "onnxruntime"
            print(f"[SUCCESS] Loaded emotion model using ONNXRuntime backend: {self.model_path}")
        except Exception as ort_err:
            print(f"[INFO] ONNXRuntime fallback: {ort_err}. Using OpenCV DNN backend...")
            try:
                self.net = cv2.dnn.readNetFromONNX(self.model_path)
                self.backend = "cv2_dnn"
                print(f"[SUCCESS] Loaded emotion model using OpenCV DNN backend: {self.model_path}")
            except Exception as cv2_err:
                raise RuntimeError(
                    f"Failed to load model with both ONNXRuntime and OpenCV DNN. Error: {cv2_err}"
                )

    def predict(
        self, face_roi: np.ndarray, target_size: Tuple[int, int] = (64, 64)
    ) -> Tuple[str, float, Dict[str, float]]:
        """
        Preprocesses face ROI and predicts emotion and confidence.

        Returns:
            (top_emotion, confidence_percentage, all_probabilities_dict)
        """
        if face_roi is None or face_roi.size == 0:
            return "Uncertain", 0.0, {}

        # Preprocess input image to (1, 1, 64, 64)
        input_tensor = preprocess_face_for_model(
            face_roi, target_size=target_size, normalize_type="raw_float32"
        )

        # Forward pass
        if self.backend == "onnxruntime":
            outputs = self.session.run([self.output_name], {self.input_name: input_tensor})
            raw_logits = outputs[0]
        elif self.backend == "cv2_dnn":
            self.net.setInput(input_tensor)
            raw_logits = self.net.forward()
        else:
            raise RuntimeError("No model backend initialized.")

        # Compute probabilities
        probabilities = compute_softmax(raw_logits)

        # Map to class labels
        prob_dict = {
            self.classes[i]: float(probabilities[i] * 100.0)
            for i in range(min(len(self.classes), len(probabilities)))
        }

        top_idx = int(np.argmax(probabilities))
        top_prob = float(probabilities[top_idx] * 100.0)
        top_label = self.classes[top_idx] if top_idx < len(self.classes) else "Unknown"

        # Apply confidence thresholding
        if top_prob < self.confidence_threshold:
            top_label = "Uncertain"

        return top_label, top_prob, prob_dict

    def get_color(self, emotion: str) -> Tuple[int, int, int]:
        """Returns BGR color code for an emotion label."""
        return EMOTION_COLORS.get(emotion, (255, 255, 255))
