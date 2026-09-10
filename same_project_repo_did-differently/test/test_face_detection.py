"""
Stage 2: Face Detection Live Test Script
Tests real-time OpenCV Haar Cascade face detection on camera feed.
"""

import cv2
import time
import sys
import os

# Add parent directory to sys.path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.face_detection import FaceDetector


def run_face_detection_test(camera_index: int = 0):
    print("=" * 50)
    print("STAGE 2: FACE DETECTION LIVE TEST")
    print("=" * 50)

    try:
        detector = FaceDetector(cascade_path="haarcascade/haarcascade_frontalface_default.xml")
        print("[SUCCESS] Haar Cascade Face Detector initialized.")
    except Exception as e:
        print(f"[ERROR] Failed to initialize FaceDetector: {e}")
        return False

    print(f"Opening camera index {camera_index}...")
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print(f"[ERROR] Unable to access camera at index {camera_index}.")
        return False

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    window_name = "Stage 2 - Face Detection (Press Q to Exit)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    prev_time = time.time()
    fps = 0.0

    print("Camera feed active. Point camera at your face.")
    print("Press 'q' or 'ESC' to exit.\n")

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            # Calculate FPS
            curr_time = time.time()
            dt = curr_time - prev_time
            if dt > 0:
                fps = 0.9 * fps + 0.1 * (1.0 / dt) if fps > 0 else (1.0 / dt)
            prev_time = curr_time

            # Detect faces
            faces = detector.detect_faces(frame)

            # Draw faces
            for idx, bbox in enumerate(faces, start=1):
                detector.draw_face_annotations(
                    frame,
                    bbox,
                    label=f"Face #{idx}",
                    confidence=None,
                    color=(0, 255, 0),
                )

            # Status HUD
            h, w, _ = frame.shape
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 55), (25, 25, 25), -1)
            cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

            status_text = f"Faces Detected: {len(faces)}"
            status_color = (0, 255, 0) if len(faces) > 0 else (0, 165, 255)

            cv2.putText(
                frame,
                "STAGE 2: FACE DETECTION TEST",
                (15, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame,
                f"{status_text} | FPS: {fps:.1f} | Press 'q' to Quit",
                (15, 46),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                status_color,
                1,
                cv2.LINE_AA,
            )

            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key in [ord('q'), ord('Q'), 27]:
                print("Exit signal received. Closing...")
                break

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[DONE] Camera released and windows closed.")

    return True


if __name__ == "__main__":
    cam_id = 0
    if len(sys.argv) > 1:
        try:
            cam_id = int(sys.argv[1])
        except ValueError:
            pass
    run_face_detection_test(cam_id)
