"""
VisionDNA - Test 1: Camera Acquisition Test
Verifies camera capture, FPS computation, display HUD, and clean exit.
"""

import sys
import os
import time
import cv2

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.camera import VideoStream


def run_camera_test(source: int = 0, headless_frames: int = 0):
    """
    Runs Camera test.
    If headless_frames > 0, runs non-interactively for the given frame count.
    """
    print("=" * 60)
    print("VISIONDNA - TEST 1: CAMERA ACQUISITION")
    print("=" * 60)
    print(f"Initializing VideoStream with source={source}...")

    stream = VideoStream(source=source, width=640, height=480)
    print(f"Stream opened: {stream.is_opened}")
    print(f"Resolution: {stream.actual_width}x{stream.actual_height}")

    window_name = "VisionDNA - Test 1: Camera (Press 'q' to Exit)"
    if headless_frames == 0:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    frames_processed = 0
    start_time = time.time()

    try:
        while True:
            ret, frame = stream.read()
            if not ret or frame is None:
                print("[WARNING] Frame capture returned None.")
                time.sleep(0.03)
                continue

            frames_processed += 1
            frame = stream.draw_hud(frame, title="VisionDNA - Camera Test")

            if headless_frames > 0:
                if frames_processed >= headless_frames:
                    print(f"[TEST 1 PASS] Processed {frames_processed} frames successfully in headless mode.")
                    break
            else:
                cv2.imshow(window_name, frame)
                key = cv2.waitKey(1) & 0xFF
                if key in [ord('q'), ord('Q'), 27]:
                    print("Exit key received. Quitting camera test.")
                    break

    finally:
        stream.release()
        if headless_frames == 0:
            cv2.destroyAllWindows()

    total_time = max(0.001, time.time() - start_time)
    avg_fps = frames_processed / total_time
    print(f"Total Frames: {frames_processed} | Time: {total_time:.2f}s | Avg FPS: {avg_fps:.1f}")
    print("[TEST 1 COMPLETE] Camera module functioning properly.\n")
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

    run_camera_test(source=src, headless_frames=headless)
