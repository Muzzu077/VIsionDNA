"""
Stage 1: Webcam Test Script
Tests webcam connectivity, video frame capture, FPS rendering, and clean exit.
"""

import cv2
import time
import sys


def run_camera_test(camera_index: int = 0):
    print("=" * 50)
    print("STAGE 1: WEBCAM CONNECTIVITY TEST")
    print("=" * 50)
    print(f"Attempting to open camera at index {camera_index}...")

    cap = cv2.VideoCapture(camera_index)

    # Try fallback to DirectShow on Windows if default backend takes time
    if not cap.isOpened():
        print(f"Standard backend failed. Trying DirectShow backend for index {camera_index}...")
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print(f"\n[ERROR] Unable to access webcam at index {camera_index}.")
        print("Suggestions:")
        print(" 1. Ensure your webcam is connected properly.")
        print(" 2. Check if another application (e.g. Zoom, Teams, Camera App) is using the webcam.")
        print(" 3. Try changing the camera index to 1 in the script if you have multiple cameras.")
        return False

    # Optional camera optimizations
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[SUCCESS] Webcam connected successfully! Resolution: {actual_width}x{actual_height}")
    print("A video window will now open. Press 'q' or 'ESC' to exit cleanly.\n")

    window_name = "Stage 1 - Webcam Test (Press Q to Exit)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    prev_time = time.time()
    fps = 0.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("[WARNING] Failed to grab frame from webcam. Retrying...")
                time.sleep(0.05)
                continue

            # Calculate FPS
            curr_time = time.time()
            dt = curr_time - prev_time
            if dt > 0:
                fps = 0.9 * fps + 0.1 * (1.0 / dt) if fps > 0 else (1.0 / dt)
            prev_time = curr_time

            # Overlay information HUD
            h, w, _ = frame.shape
            
            # Semi-transparent top banner
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 50), (20, 20, 20), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

            cv2.putText(
                frame,
                "STAGE 1: WEBCAM FEED TEST",
                (15, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame,
                f"FPS: {fps:.1f} | Res: {w}x{h} | Press 'q' to Quit",
                (15, 43),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (200, 200, 200),
                1,
                cv2.LINE_AA,
            )

            cv2.imshow(window_name, frame)

            # Wait for key press (1ms)
            key = cv2.waitKey(1) & 0xFF
            if key in [ord('q'), ord('Q'), 27]:  # 'q', 'Q', or ESC
                print("Exit signal received ('q' or ESC). Closing camera...")
                break

    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[DONE] Webcam released and windows destroyed cleanly.")

    return True


if __name__ == "__main__":
    cam_id = 0
    if len(sys.argv) > 1:
        try:
            cam_id = int(sys.argv[1])
        except ValueError:
            print(f"Invalid camera index '{sys.argv[1]}', using 0.")
    run_camera_test(cam_id)
