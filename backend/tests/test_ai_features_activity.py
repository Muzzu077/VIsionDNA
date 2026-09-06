"""
Tests for Feature Extraction and Activity Recognition modules.
"""

import pytest
from app.ai.models import BoundingBox, TrackedPerson
from app.ai.features.extractor import FeatureExtractor
from app.ai.activity.heuristic_recognizer import HeuristicActivityRecognizer


def test_feature_extractor_velocity():
    extractor = FeatureExtractor(window_size=10, fps=30)

    # Simulate walking movement across 5 frames
    history = [
        TrackedPerson(tracking_id="P001", bbox=BoundingBox(x=100 + i * 5, y=200, w=40, h=100))
        for i in range(5)
    ]
    features = extractor.extract(history)

    assert "moving_average_velocity" in features
    assert features["moving_average_velocity"] > 0
    assert features["aspect_ratio"] == 0.4
    assert features["posture_heuristic"] == "standing"


@pytest.mark.asyncio
async def test_activity_recognizer_standing_vs_running():
    recognizer = HeuristicActivityRecognizer(smoothing_window=3)

    # 1. Standing profile: low velocity, upright aspect ratio (0.4)
    history_standing = [
        TrackedPerson(tracking_id="P001", bbox=BoundingBox(x=100, y=200, w=40, h=100))
    ]
    features_standing = {
        "moving_average_velocity": 2.0,
        "aspect_ratio": 0.4,
    }
    result_standing = await recognizer.recognize(features_standing, history_standing)
    assert result_standing.activity == "standing"

    # 2. Running profile: high velocity, upright aspect ratio
    history_running = [
        TrackedPerson(tracking_id="P002", bbox=BoundingBox(x=100, y=200, w=40, h=100))
    ]
    features_running = {
        "moving_average_velocity": 180.0,
        "aspect_ratio": 0.4,
    }
    result_running = await recognizer.recognize(features_running, history_running)
    assert result_running.activity == "running"

    # 3. Lying down / Fall profile: wide aspect ratio > 1.2
    history_lying = [
        TrackedPerson(tracking_id="P003", bbox=BoundingBox(x=100, y=200, w=160, h=100))
    ]
    features_lying = {
        "moving_average_velocity": 5.0,
        "aspect_ratio": 1.6,
    }
    result_lying = await recognizer.recognize(features_lying, history_lying)
    assert result_lying.activity == "lying down"
