"""
Tests for Behavior and Trajectory Risk Prediction Engine.
"""

import pytest
from app.ai.prediction.predictor import BehaviorPredictor


def test_trajectory_prediction_restricted_zone_collision():
    predictor = BehaviorPredictor()
    predictor.fps = 30

    # Restricted polygon at x: [600, 800], y: [100, 300]
    restricted_zone = {
        "id": "zone-restricted",
        "name": "Restricted Sector",
        "type": "restricted",
        "points": [
            {"x": 600.0, "y": 100.0},
            {"x": 800.0, "y": 100.0},
            {"x": 800.0, "y": 300.0},
            {"x": 600.0, "y": 300.0},
        ],
    }

    # Simulate Person P001 moving toward the restricted zone:
    # Frame history: moving from (400, 200) to (550, 200) -> heading directly into (600, 200)
    history = [
        {"persons": [{"tracking_id": "P001", "position": {"x": 400.0, "y": 200.0}}]},
        {"persons": [{"tracking_id": "P001", "position": {"x": 450.0, "y": 200.0}}]},
        {"persons": [{"tracking_id": "P001", "position": {"x": 500.0, "y": 200.0}}]},
    ]

    current_state = {
        "persons": [{"tracking_id": "P001", "position": {"x": 550.0, "y": 200.0}}],
        "zones": [restricted_zone],
    }

    predictions = predictor.predict(current_state, history)
    assert "P001" in predictions
    p_preds = predictions["P001"]
    assert len(p_preds) >= 1
    assert p_preds[0]["prediction"] == "restricted_zone_entry"
    assert p_preds[0]["probability"] > 0.5
    assert p_preds[0]["horizon_seconds"] <= 3.0
    assert p_preds[0]["risk_level"] == "HIGH"
