"""
Tests for Anomaly Detection and Multi-Factor Risk Engine.
"""

import pytest
from app.ai.anomaly.rule_detector import RuleBasedAnomalyDetector
from app.ai.risk.risk_engine import RiskEngine


def test_rule_based_anomaly_restricted_zone():
    detector = RuleBasedAnomalyDetector()

    twin_state = {
        "persons": [
            {
                "tracking_id": "P001",
                "activity": "walking",
                "current_zone": "zone-restricted-1",
                "position": {"x": 650, "y": 150},
                "distances_to_objects": {},
            }
        ],
        "zones": [
            {
                "id": "zone-restricted-1",
                "name": "High Voltage Room",
                "type": "restricted",
            }
        ],
        "objects": [],
    }

    anomalies = detector.check(twin_state, history=[])
    assert len(anomalies) >= 1
    assert any(a["type"] == "restricted_zone_entry" for a in anomalies)
    assert anomalies[0]["severity"] == "CRITICAL"


def test_rule_based_anomaly_dangerous_proximity():
    detector = RuleBasedAnomalyDetector()
    detector.dangerous_proximity_threshold = 50.0

    twin_state = {
        "persons": [
            {
                "tracking_id": "P002",
                "activity": "standing",
                "current_zone": "zone-safe",
                "position": {"x": 200, "y": 200},
                "distances_to_objects": {"machine-1": 15.0},  # 15.0 < 50.0 threshold
            }
        ],
        "zones": [{"id": "zone-safe", "name": "Main Floor", "type": "safe"}],
        "objects": [{"id": "machine-1", "name": "Conveyor"}],
    }

    anomalies = detector.check(twin_state, history=[])
    assert any(a["type"] == "dangerous_proximity" for a in anomalies)


def test_multi_factor_risk_engine_scoring_and_explanation():
    engine = RiskEngine()

    twin_state = {
        "persons": [
            {
                "tracking_id": "P001",
                "activity": "falling",
                "current_zone": "zone-danger",
            }
        ],
        "zones": [
            {"id": "zone-danger", "name": "Chemical Bay", "type": "restricted"}
        ],
    }

    anomalies = [
        {
            "type": "restricted_zone_entry",
            "severity": "CRITICAL",
            "person_id": "P001",
            "description": "Person P001 in restricted zone",
        }
    ]

    risk_output = engine.evaluate(twin_state, anomalies)
    assert "persons" in risk_output
    assert "P001" in risk_output["persons"]

    p_risk = risk_output["persons"]["P001"]
    assert p_risk["score"] >= 50.0
    assert p_risk["level"] in ["MEDIUM", "HIGH", "CRITICAL"]
    assert len(p_risk["factors"]) > 0
    assert "Top factor" in p_risk["explanation"]
