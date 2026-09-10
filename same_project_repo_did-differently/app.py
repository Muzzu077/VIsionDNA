"""
=============================================================================
VisionDNA: AI-Based Visual Digital Twin for Predictive Human Activity & Risk Analysis
Standalone Desktop Operations Center (End-to-End Single-Pass Pipeline)
=============================================================================
"""

import argparse
import sys
import os
import time
import cv2
import numpy as np

from src.camera import VideoStream
from src.detector import UnifiedPersonPoseDetector
from src.tracker import PersonTracker
from src.activity import ActivityClassifier
from src.digital_twin import DigitalTwinEngine
from src.prediction import ActivityPredictor
from src.risk_engine import RiskEngine


def parse_args():
    parser = argparse.ArgumentParser(
        description="VisionDNA: AI-Based Visual Digital Twin - Standalone Desktop Runner"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="0",
        help="Camera index (e.g. 0) or path to video file or -1 for synthetic stream",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/person_detection/yolov8n-pose.pt",
        help="Path to YOLOv8-Pose model weights",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.35,
        help="Detection confidence threshold (0.0 to 1.0)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=640,
        help="Frame width",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=480,
        help="Frame height",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="split",
        choices=["split", "camera", "twin", "pip"],
        help="Initial view mode: split, camera, twin, or pip",
    )
    parser.add_argument(
        "--headless-frames",
        type=int,
        default=0,
        help="Run for N frames without opening a GUI window (for testing)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Parse source as int if purely digits or negative
    if args.source.isdigit():
        source = int(args.source)
    elif args.source.startswith("-") and args.source[1:].isdigit():
        source = int(args.source)
    else:
        source = args.source

    print("\n" + "=" * 76)
    print(" 🧬 VISIONDNA // AI-BASED VISUAL DIGITAL TWIN COMMAND CENTER")
    print("=" * 76)
    print(f" Source:            {source}")
    print(f" Pose Model:        {args.model}")
    print(f" Confidence Thresh: {args.conf}")
    print(f" Base Resolution:   {args.width}x{args.height}")
    print(f" View Mode:         {args.mode.upper()}")
    print("=" * 76)
    print(" HOTKEYS:")
    print("   [TAB] or [M] : Cycle Display Mode (Split Dual-View -> Full Perception -> Twin -> PiP)")
    print("   [S]          : Toggle Skeleton Overlay")
    print("   [Z]          : Toggle Danger Zones")
    print("   [H]          : Toggle HUD Banner")
    print("   [Q] or [ESC] : Clean Exit")
    print("=" * 76 + "\n")

    # 1. Initialize Pipeline Modules
    stream = VideoStream(source=source, width=args.width, height=args.height)
    detector = UnifiedPersonPoseDetector(model_path=args.model, confidence_threshold=args.conf)
    tracker = PersonTracker(history_len=25, jitter_deadzone_px=8.0)
    activity_classifier = ActivityClassifier(smoothing_window=5)
    digital_twin = DigitalTwinEngine()
    predictor = ActivityPredictor()
    risk_engine = RiskEngine()

    window_name = "VisionDNA // AI Visual Digital Twin Operations Center"
    if args.headless_frames == 0:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1280, 520)

    # View Mode state: 0: split, 1: camera, 2: twin, 3: pip
    mode_map = {"split": 0, "camera": 1, "twin": 2, "pip": 3}
    curr_mode = mode_map.get(args.mode, 0)
    mode_names = ["SPLIT-SCREEN DUAL MATRIX", "LIVE PERCEPTION FEED", "2D DIGITAL TWIN BLUEPRINT", "PICTURE-IN-PICTURE (PIP)"]

    show_skeleton = True
    show_danger_zones = True
    show_hud = True

    frames_processed = 0
    start_time = time.time()

    print("[VisionDNA] Neural Engine active. Monitoring visual stream...\n")

    try:
        while True:
            ret, frame = stream.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            frames_processed += 1

            # 1. Unified Single-Pass Detection & Pose Estimation
            detections = detector.detect_and_estimate(frame, inference_size=480)

            # 2. Tracking with persistent IDs
            tracks = tracker.update(detections)

            # 3. Perception Frame Rendering
            annotated_frame = frame.copy()
            if show_danger_zones:
                annotated_frame = risk_engine.draw_zones(annotated_frame)

            if show_skeleton:
                for p in tracks:
                    if p.pose and p.pose.is_valid:
                        annotated_frame = detector.draw_skeleton(annotated_frame, p.pose)

            annotated_frame = tracker.draw_tracks(annotated_frame, tracks)

            # 4. Multi-entity analysis
            highest_risk_level = "LOW"
            highest_risk_score = 0.0
            primary_reason = "Normal"
            active_pose_res = None

            for person in tracks:
                pose_res = person.pose
                if pose_res and pose_res.is_valid:
                    active_pose_res = pose_res

                # Activity Recognition
                act_res = activity_classifier.classify(pose_res, person, frame_height=frame.shape[0])

                # Predictive Trajectory & State
                pred_res = predictor.predict(
                    person.track_id,
                    act_res.activity,
                    person.velocity,
                    person.center,
                    danger_zones=risk_engine.danger_zones if show_danger_zones else None,
                )

                # Safety Risk Assessment
                risk_res = risk_engine.assess(person, tracks, act_res, pred_res)

                if risk_res.risk_score > highest_risk_score:
                    highest_risk_score = risk_res.risk_score
                    highest_risk_level = risk_res.risk_level
                    if len(risk_res.all_reasons) > 0:
                        primary_reason = risk_res.all_reasons[0]

                # Synchronize Digital Twin
                digital_twin.update_twin(
                    person=person,
                    activity_res=act_res,
                    pose_res=pose_res,
                    risk_score=risk_res.risk_score,
                    risk_level=risk_res.risk_level,
                    risk_reasons=risk_res.all_reasons,
                    predicted_activity=pred_res.predicted_next_activity,
                    prediction_conf=pred_res.probability,
                )

            digital_twin.cleanup_twins([p.track_id for p in tracks])

            # 5. Render 2D Digital Twin Canvas
            twin_canvas = digital_twin.render_canvas(
                width=args.width,
                height=args.height,
                pose_res=active_pose_res,
            )

            # Top HUD banner on perception feed
            if show_hud:
                hud_title = f"VisionDNA Perception  |  Tracked: {len(tracks):02d}  |  Risk: {highest_risk_level}"
                annotated_frame = stream.draw_hud(annotated_frame, title=hud_title, subtitle=mode_names[curr_mode])

            # 6. Compose View According to Display Mode
            if curr_mode == 0:
                # Mode 0: Split-Screen Side-by-Side
                display_frame = np.hstack((annotated_frame, twin_canvas))
            elif curr_mode == 1:
                # Mode 1: Perception Feed Only
                display_frame = annotated_frame
            elif curr_mode == 2:
                # Mode 2: Digital Twin Only
                display_frame = twin_canvas
            else:
                # Mode 3: PiP (Picture in Picture)
                display_frame = annotated_frame.copy()
                pip_w = int(args.width * 0.38)
                pip_h = int(args.height * 0.38)
                pip_resized = cv2.resize(twin_canvas, (pip_w, pip_h))
                # Bottom-Right Corner placement
                py1 = args.height - pip_h - 12
                px1 = args.width - pip_w - 12
                # Border
                cv2.rectangle(display_frame, (px1 - 2, py1 - 2), (px1 + pip_w + 2, py1 + pip_h + 2), (0, 220, 255), 2)
                display_frame[py1:py1+pip_h, px1:px1+pip_w] = pip_resized

            # Check headless mode
            if args.headless_frames > 0:
                if frames_processed >= args.headless_frames:
                    print(f"[VisionDNA] Processed {frames_processed} frames successfully in headless mode.")
                    break
            else:
                cv2.imshow(window_name, display_frame)
                key = cv2.waitKey(1) & 0xFF
                if key in [ord("q"), ord("Q"), 27]:
                    print("\n[VisionDNA] Exit signal received. Shutting down cleanly...")
                    break
                elif key in [ord("\t"), ord("m"), ord("M")]:
                    curr_mode = (curr_mode + 1) % 4
                    print(f"[VisionDNA] Switched View Mode -> {mode_names[curr_mode]}")
                elif key in [ord("s"), ord("S")]:
                    show_skeleton = not show_skeleton
                    print(f"[VisionDNA] Skeleton Overlay: {'ENABLED' if show_skeleton else 'DISABLED'}")
                elif key in [ord("z"), ord("Z")]:
                    show_danger_zones = not show_danger_zones
                    print(f"[VisionDNA] Danger Zones: {'ENABLED' if show_danger_zones else 'DISABLED'}")
                elif key in [ord("h"), ord("H")]:
                    show_hud = not show_hud
                    print(f"[VisionDNA] HUD Banner: {'ENABLED' if show_hud else 'DISABLED'}")

    except KeyboardInterrupt:
        print("\n[VisionDNA] Process interrupted by user.")
    finally:
        stream.release()
        if args.headless_frames == 0:
            cv2.destroyAllWindows()

    elapsed = max(0.001, time.time() - start_time)
    print(f"\n[VisionDNA] Session summary: {frames_processed} frames processed in {elapsed:.2f}s ({frames_processed / elapsed:.1f} FPS).")
    print("[VisionDNA] Shutdown complete.")


if __name__ == "__main__":
    main()
