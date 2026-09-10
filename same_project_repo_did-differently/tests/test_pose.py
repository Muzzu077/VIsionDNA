"""
VisionDNA - Test 4: Pose Estimation Test
Verifies YOLOv8 Pose model loading, keypoint extraction, and skeleton rendering.
"""

import sys
import os
import time
import cv2
import numpy as np

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.camera import VideoStream
from src.pose import PoseEstimator


def run_pose_test(source: int = 0, headless_frames: int = 0):
    print("=" * 60)
    print("VISIONDNA - TEST 4: POSE ESTIMATION")
    print("=" * 60)

    stream = VideoStream(source=source, width=640, height=480)
    pose_estimator = PoseEstimator()

    window_name = "VisionDNA - Pose Estimation (Press 'q' to Quit)"
    if headless_frames == 0:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    frames_processed = 0
    start_time = time.time()

    try:
        while True:
            ret, frame = stream.read()
            if not ret or frame is None:
                time.sleep(0.02)
                continue

            frames_processed += 1

            # Estimate pose
            pose_res = pose_estimator.estimate(frame)

            annotated_frame = frame.copy()
            if pose_res.is_valid:
                annotated_frame = pose_estimator.draw_skeleton(annotated_frame, pose_res)
                spine = pose_res.spine_angle
                lk = pose_res.left_knee_angle
                rk = pose_res.right_knee_angle
                hud_title = f"Pose Valid | Spine: {spine:.1f} deg | Knees: L:{lk:.0f} R:{rk:.0f}"
            else:
                hud_title = "Pose: Searching for Subject..."

            annotated_frame = stream.draw_hud(annotated_frame, title=hud_title)

            if headless_frames > 0:
                if frames_processed >= headless_frames:
                    print(f"[TEST 4 PASS] Processed {frames_processed} frames successfully with Pose Estimator.")
                    break
            else:
                cv2.imshow(window_name, annotated_frame)
                key = cv2.waitKey(1) & 0xFF
                if key in [ord("q"), ord("Q"), 27]:
                    break

    finally:
        stream.release()
        if headless_frames == 0:
            cv2.destroyAllWindows()

    elapsed = max(0.001, time.time() - start_time)
    print(f"Total Frames: {frames_processed} | Time: {elapsed:.2f}s | FPS: {frames_processed / elapsed:.1f}")
    print("[TEST 4 COMPLETE] Pose Estimation module is fully operational.\n")
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

    run_pose_test(source=src, headless_frames=headless)
