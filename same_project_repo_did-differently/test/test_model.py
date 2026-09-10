"""
Stage 3: Emotion Model Standalone Test Script
Tests model loading, image preprocessing, and inference verification.
"""

import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.emotion_model import EmotionClassifier


def run_model_test():
    print("=" * 50)
    print("STAGE 3: EMOTION RECOGNITION MODEL TEST")
    print("=" * 50)

    model_path = "models/emotion_ferplus.onnx"
    print(f"Loading emotion model from '{model_path}'...")

    try:
        classifier = EmotionClassifier(model_path=model_path, confidence_threshold=20.0)
        print("[SUCCESS] EmotionClassifier successfully instantiated.")
        print(f"Supported Emotion Classes ({len(classifier.classes)}): {classifier.classes}\n")
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return False

    # Create synthetic test face image (e.g. 100x100 BGR mock face)
    print("Running inference on test face sample...")
    test_face = np.random.randint(50, 200, size=(100, 100, 3), dtype=np.uint8)

    top_emotion, confidence, prob_dict = classifier.predict(test_face)

    print("-" * 40)
    print(f"Top Predicted Emotion : {top_emotion}")
    print(f"Confidence Score      : {confidence:.2f}%")
    print("-" * 40)
    print("Full Probability Breakdown:")
    for emotion, prob in prob_dict.items():
        bar_len = int(prob / 2.5)  # Scale to 40 chars max
        bar = "#" * bar_len
        print(f" {emotion:<10}: {prob:6.2f}% | {bar}")
    print("-" * 40)

    print("[SUCCESS] Stage 3 Model test passed successfully!")
    return True


if __name__ == "__main__":
    run_model_test()
