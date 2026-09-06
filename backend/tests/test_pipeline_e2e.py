"""
End-to-End Pipeline Integration Test.

Tests the full sequence:
Frame Acquisition -> Detection -> Tracking -> Pose -> Feature Extraction
-> Activity Recognition -> Digital Twin State Update -> Anomaly Detection
-> Risk Assessment -> Prediction -> Alert Flagging.
"""

import numpy as np
import pytest
from app.ai.pipeline import AIPipelineManager
from app.ai.digital_twin.models import ZonePolygon, Point2D


@pytest.mark.asyncio
async def test_full_pipeline_e2e():
    pipeline = AIPipelineManager()

    # Configure environment zones in digital twin
    restricted_zone = ZonePolygon(
        id="zone-restricted-alpha",
        name="Server Vault",
        type="restricted",
        points=[
            Point2D(x=500.0, y=0.0),
            Point2D(x=800.0, y=0.0),
            Point2D(x=800.0, y=500.0),
            Point2D(x=500.0, y=500.0),
        ],
    )
    pipeline.digital_twin_engine.add_zone(restricted_zone)

    # Synthetic test frame (480x640)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Process frame through pipeline
    result = await pipeline.process_frame(frame, camera_id="cam-sector-1")

    assert "camera_id" in result
    assert result["camera_id"] == "cam-sector-1"
    assert "digital_twin_state" in result

    twin = result["digital_twin_state"]
    assert "persons" in twin
    assert "anomalies" in twin
    assert "risk" in twin
    assert "predictions" in twin
    assert "alert" in twin

    # Verify risk structure
    risk = twin["risk"]
    assert "overall_score" in risk
    assert "overall_level" in risk
    assert risk["overall_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
