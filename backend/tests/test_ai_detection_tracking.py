"""
Tests for Detection and Multi-Object Tracking components.
"""

import numpy as np
import pytest
from app.ai.detection.yolo_detector import YOLODetector
from app.ai.tracking.sort_tracker import SortTrackerWrapper, calculate_iou
from app.ai.models import BoundingBox, DetectedObject, DetectionContext


def test_iou_calculation():
    box1 = BoundingBox(x=0, y=0, w=10, h=10)
    box2 = BoundingBox(x=5, y=0, w=10, h=10)
    # Intersection = 5x10 = 50, Union = 100 + 100 - 50 = 150 -> IoU = 1/3
    iou = calculate_iou(box1, box2)
    assert pytest.approx(iou, 0.01) == 0.333


def test_tracker_id_persistence():
    tracker = SortTrackerWrapper(iou_threshold=0.3, max_age=5)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Frame 1: Detection at (100, 100)
    det1 = [
        DetectedObject(
            class_name="person",
            confidence=0.9,
            bbox=BoundingBox(x=100, y=100, w=50, h=120),
            center=(125, 160),
        )
    ]
    tracks1 = tracker.update(det1, frame)
    assert len(tracks1) == 1
    p_id = tracks1[0].tracking_id
    assert p_id == "P001"

    # Frame 2: Person moves slightly to (105, 102) -> Should retain ID P001
    det2 = [
        DetectedObject(
            class_name="person",
            confidence=0.92,
            bbox=BoundingBox(x=105, y=102, w=50, h=120),
            center=(130, 162),
        )
    ]
    tracks2 = tracker.update(det2, frame)
    assert len(tracks2) == 1
    assert tracks2[0].tracking_id == p_id
    assert len(tracker.tracked_objects[p_id]["history"]) == 2


@pytest.mark.asyncio
async def test_detector_interface():
    detector = YOLODetector()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    ctx = DetectionContext(frame_width=640, frame_height=480, camera_id="test-cam")
    detections = await detector.detect(frame, ctx)
    assert isinstance(detections, list)
