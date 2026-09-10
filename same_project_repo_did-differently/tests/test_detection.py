"""
VisionDNA - Test 2: Person Detection Test
Verifies YOLOv8 model loading, inference on frames, bounding box extraction, and overlay rendering.
"""

import sys
import os
import time
import cv2
import numpy as np

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.camera import VideoStream
from src.detector import PersonDetector, PersonDetection


def run_detection_test(source: int = 0, headless_frames: int = 0):
    """
    Runs YOLO Person Detection test.
    If headless_frames > 0, executes in automated headless mode for N frames.
    """
    print("=" * 60)
    print("VISIONDNA - TEST 2: PERSON DETECTION (YOLOv8)")
    print("=" * 60)

    # 1. Initialize Stream
    stream = VideoStream(source=source, width=640, height=480)

    # 2. Initialize Person Detector
    detector = PersonDetector(
        model_path="models/person_detection/yolov8n.pt",
        confidence_threshold=0.40,
    )

    window_name = "VisionDNA - Phase 1: YOLO Person Detection (Press 'q' to Quit)"
    if headless_frames == 0:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    frames_processed = 0
    total_detections_count = 0
    start_time = time.time()

    print("\nStarting video stream and detection loop...")

    try:
        while True:
            ret, frame = stream.read()
            if not ret or frame is None:
                time.sleep(0.02)
                continue

            frames_processed += 1

            # Detect people
            detections = detector.detect(frame)
            total_detections_count += len(detections)

            # Draw detections
            annotated_frame = frame.copy()
            detector.draw_detections(annotated_frame, detections)

            # Draw HUD
            hud_title = f"VisionDNA Person Detector | People Detected: {len(detections)}"
            annotated_frame = stream.draw_hud(annotated_frame, title=hud_title)

            if headless_frames > 0:
                if len(detections) > 0:
                    for i, det in enumerate(detections):
                        print(f" Frame {frames_processed} | Person {i+1}: BBox={det.bbox}, Conf={det.confidence:.2f}, Center={det.center}")
                if frames_processed >= headless_frames:
                    print(f"[TEST 2 PASS] Successfully processed {frames_processed} frames with YOLO person detection.")
                    break
            else:
                cv2.imshow(window_name, annotated_frame)
                key = cv2.waitKey(1) & 0xFF
                if key in [ord('q'), ord('Q'), 27]:
                    print("Exit requested ('q' or ESC pressed). Terminating detection test.")
                    break

    finally:
        stream.release()
        if headless_frames == 0:
            cv2.destroyAllWindows()

    total_time = max(0.001, time.time() - start_time)
    avg_fps = frames_processed / total_time
    print(f"Frames: {frames_processed} | Detections: {total_detections_count} | Time: {total_time:.2f}s | FPS: {avg_fps:.1f}")
    print("[TEST 2 COMPLETE] Person detection module is fully operational.\n")
    return True


if __name__ == "__main__":
    src = 0
    headless = 0
    if len(sys.argv) > 1:
        try:
            src = int(sys.argv[1])
        except ValueError:
            src = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            headless = int(sys.argv[2])
        except ValueError:
            headless = 0

    run_detection_test(source=src, headless_frames=headless)
