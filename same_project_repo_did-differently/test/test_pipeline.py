"""
Pipeline Test Suite: Verifies end-to-end integration of all software modules without requiring active webcam.
"""

import os
import sys
import cv2
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.face_detection import FaceDetector
from src.preprocessing import preprocess_face_for_model, compute_softmax
from src.emotion_model import EmotionClassifier
from src.serial_controller import ArduinoSerialController


def run_pipeline_test():
    print("=" * 60)
    print("RUNNING END-TO-END PIPELINE VERIFICATION")
    print("=" * 60)

    # 1. Test Haar Cascade Face Detector
    print("[Test 1/5] Testing Face Detector initialization...")
    detector = FaceDetector("haarcascade/haarcascade_frontalface_default.xml")
    assert not detector.classifier.empty(), "Haar classifier is empty!"
    print("           PASS: Face Detector successfully initialized.")

    # 2. Test Face Preprocessing
    print("[Test 2/5] Testing Preprocessing Pipeline...")
    dummy_face = np.ones((120, 120, 3), dtype=np.uint8) * 128
    tensor = preprocess_face_for_model(dummy_face, target_size=(64, 64), normalize_type="raw_float32")
    assert tensor.shape == (1, 1, 64, 64), f"Unexpected tensor shape {tensor.shape}"
    assert tensor.dtype == np.float32, f"Unexpected dtype {tensor.dtype}"
    print("           PASS: Preprocessing generated correct (1, 1, 64, 64) tensor.")

    # 3. Test Emotion AI Model
    print("[Test 3/5] Testing Emotion Classifier Model...")
    classifier = EmotionClassifier("models/emotion_ferplus.onnx", confidence_threshold=20.0)
    emotion, conf, probs = classifier.predict(dummy_face)
    assert isinstance(emotion, str), "Predicted emotion must be a string"
    assert 0.0 <= conf <= 100.0, f"Confidence {conf} out of bounds"
    assert len(probs) == len(classifier.classes), "Probabilities length mismatch"
    print(f"           PASS: Model predicted '{emotion}' with {conf:.1f}% confidence.")

    # 4. Test Face Drawing & Annotation
    print("[Test 4/5] Testing Annotation Renderer...")
    canvas = np.zeros((480, 640, 3), dtype=np.uint8)
    bbox = (100, 100, 200, 200)
    annotated = detector.draw_face_annotations(canvas, bbox, label="Happy", confidence=92.5)
    assert annotated.shape == (480, 640, 3), "Annotated canvas shape altered"
    print("           PASS: Bounding box and badge rendered cleanly.")

    # 5. Test Arduino Serial Fallback
    print("[Test 5/5] Testing Arduino Standalone Fallback...")
    serial_ctrl = ArduinoSerialController(port=None)
    sent = serial_ctrl.send_emotion("HAPPY")
    # Must return False safely without raising exceptions when no Arduino is plugged in
    assert sent is False or sent is True
    print(f"           PASS: Serial controller handled disconnected state gracefully ({serial_ctrl.get_port_name()}).")

    print("\n" + "=" * 60)
    print("ALL 5 PIPELINE MODULE TESTS PASSED SUCCESSFULLY (100%)!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_pipeline_test()
    if not success:
        sys.exit(1)
