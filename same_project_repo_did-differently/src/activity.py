"""
VisionDNA - Human Activity Recognition (HAR) Module
High-precision biomechanical activity & motion state classifier tailored for real-world
webcam streams, desk environments, and full-body surveillance.
Accurately distinguishes Standing, Walking, Sitting, Running, Bending, Falling, and Gesturing.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

from src.detector import PoseResult
from src.tracker import TrackedPerson


@dataclass
class ActivityResult:
    """Represents the activity and motion state classification for a tracked person."""
    activity: str = "Standing"
    motion_state: str = "Stationary (Standing Upright)"
    confidence: float = 0.85
    posture_summary: str = "Upright Torso"
    features: Dict[str, float] = field(default_factory=dict)


class ActivityClassifier:
    """
    Biomechanical and kinematic activity classifier with multi-cue spatial geometry,
    temporal stability filtering, and robust standing vs seated distinction.
    """

    ACTIVITIES = ["Standing", "Walking", "Sitting", "Running", "Bending", "Falling", "Gesturing"]

    def __init__(self, smoothing_window: int = 5):
        self.smoothing_window = smoothing_window
        self.track_activity_history: Dict[int, deque] = {}
        self.track_motion_history: Dict[int, deque] = {}

    def classify(
        self,
        pose: Optional[PoseResult],
        person: Optional[TrackedPerson] = None,
        frame_height: int = 480,
    ) -> ActivityResult:
        """
        Determines current human motion state with multi-cue biomechanical analysis.
        """
        track_id = person.track_id if person else 0
        velocity = person.velocity if person else 0.0
        direction = person.direction if person else "Stationary"
        bbox = person.bbox if person else (0, 0, 100, 100)

        # Calculate bounding box dimensions
        bx1, by1, bx2, by2 = bbox
        bw = max(1, bx2 - bx1)
        bh = max(1, by2 - by1)
        aspect_ratio = float(bh / bw)
        norm_top_y = by1 / max(1.0, float(frame_height))
        norm_height = bh / max(1.0, float(frame_height))

        raw_activity = "Standing"
        motion_state = "Stationary (Standing Upright)"
        conf = 0.85
        posture_summary = "Upright Torso"

        # -------------------------------------------------------------
        # 1. TRANSLATIONAL LOCOMOTION (Walking & Running)
        # -------------------------------------------------------------
        if velocity >= 1.8:
            raw_activity = "Running"
            motion_state = f"High-Speed Movement ({velocity:.2f} m/s {direction})"
            conf = min(0.98, 0.82 + min(1.0, (velocity - 1.8) / 1.5) * 0.16)
            posture_summary = "Dynamic Locomotion"

        elif velocity >= 0.20:
            raw_activity = "Walking"
            dir_tag = f" ({direction})" if direction != "Stationary" else ""
            motion_state = f"Active Locomotion (Walking{dir_tag} @ {velocity:.2f} m/s)"
            conf = min(0.96, 0.80 + min(1.0, velocity / 1.5) * 0.16)
            posture_summary = "Upright Locomotion"

        # -------------------------------------------------------------
        # 2. STATIONARY / BIOMECHANICAL POSTURE ANALYSIS
        # -------------------------------------------------------------
        elif not pose or not pose.is_valid:
            # Fallback when skeleton landmarks are unavailable
            if norm_top_y < 0.15 and norm_height > 0.60:
                raw_activity = "Standing"
                motion_state = "Stationary (Standing Upright)"
                conf = 0.82
                posture_summary = "Extended Vertical Profile"
            elif norm_top_y > 0.25 or aspect_ratio < 1.30:
                raw_activity = "Sitting"
                motion_state = "Stationary (Seated / Desk View)"
                conf = 0.82
                posture_summary = "Desk Profile"
            else:
                raw_activity = "Standing"
                motion_state = "Stationary (Standing Upright)"
                conf = 0.80
                posture_summary = "Vertical Profile"

        else:
            spine = pose.spine_angle
            lms = pose.landmarks

            # Extract key landmarks
            nose = lms.get("nose")
            l_sh = lms.get("left_shoulder")
            r_sh = lms.get("right_shoulder")
            l_wr = lms.get("left_wrist")
            r_wr = lms.get("right_wrist")
            l_hip = lms.get("left_hip")
            r_hip = lms.get("right_hip")
            l_knee = lms.get("left_knee")
            r_knee = lms.get("right_knee")

            head_y = nose.pixel_y if (nose and nose.visibility > 0.3) else None
            head_norm_y = nose.y if (nose and nose.visibility > 0.3) else None

            hip_y = None
            if l_hip and r_hip and l_hip.visibility > 0.3 and r_hip.visibility > 0.3:
                hip_y = (l_hip.pixel_y + r_hip.pixel_y) / 2.0
            elif l_hip and l_hip.visibility > 0.3:
                hip_y = l_hip.pixel_y
            elif r_hip and r_hip.visibility > 0.3:
                hip_y = r_hip.pixel_y

            sh_y = None
            if l_sh and r_sh and l_sh.visibility > 0.3 and r_sh.visibility > 0.3:
                sh_y = (l_sh.pixel_y + r_sh.pixel_y) / 2.0
            elif l_sh and l_sh.visibility > 0.3:
                sh_y = l_sh.pixel_y
            elif r_sh and r_sh.visibility > 0.3:
                sh_y = r_sh.pixel_y

            # Check arm gesturing
            hands_raised = False
            if sh_y is not None:
                if (l_wr and l_wr.visibility > 0.4 and l_wr.pixel_y < sh_y + 15) or \
                   (r_wr and r_wr.visibility > 0.4 and r_wr.pixel_y < sh_y + 15):
                    hands_raised = True

            # ---------------------------------------------------------
            # 2A. FALL DETECTION (Critical Horizontal Spine / Head Drop)
            # ---------------------------------------------------------
            is_horizontal = spine > 50.0 and aspect_ratio < 1.25
            head_below_hips = (head_y is not None and hip_y is not None and head_y >= (hip_y - 20))

            if is_horizontal or (head_below_hips and spine > 42.0):
                raw_activity = "Falling"
                motion_state = "Critical Fall Hazard (Horizontal Posture)"
                conf = min(0.98, 0.80 + (spine / 90.0) * 0.18)
                posture_summary = f"Horizontal Floor ({spine:.1f}° Spine)"

            # ---------------------------------------------------------
            # 2B. BENDING / FORWARD LEAN
            # ---------------------------------------------------------
            elif 26.0 <= spine <= 62.0 and not head_below_hips:
                raw_activity = "Bending"
                motion_state = "Forward Lean / Bending Posture"
                conf = min(0.96, 0.78 + (spine / 50.0) * 0.18)
                posture_summary = f"Torso Lean ({spine:.1f}° Tilt)"

            # ---------------------------------------------------------
            # 2C. GESTURING / UPPER-BODY DYNAMICS (Stationary)
            # ---------------------------------------------------------
            elif hands_raised:
                raw_activity = "Gesturing"
                motion_state = "Dynamic Arm Gesturing / Upper Movement"
                conf = 0.88
                posture_summary = f"Active Gestures ({spine:.1f}° Spine)"

            # ---------------------------------------------------------
            # 2D. STANDING vs SITTING (High Precision Biomechanical Cueing)
            # ---------------------------------------------------------
            else:
                if pose.lower_body_visible and getattr(pose, "has_knee_data", False):
                    # Full Body Visible: Check Knee Flexion & Thigh Vector
                    knee_avg = (pose.left_knee_angle + pose.right_knee_angle) / 2.0
                    
                    # Knee angle flexed (< 142°) indicates sitting on a chair
                    # Knee angle extended (> 150°) indicates standing
                    if knee_avg < 144.0:
                        raw_activity = "Sitting"
                        motion_state = "Stationary (Seated on Chair)"
                        conf = min(0.96, 0.82 + (180.0 - knee_avg) / 180.0 * 0.16)
                        posture_summary = f"Seated (Knees: {knee_avg:.0f}°)"
                    else:
                        raw_activity = "Standing"
                        motion_state = "Stationary (Standing Upright)"
                        conf = 0.94
                        posture_summary = f"Standing Upright ({spine:.1f}° Spine)"

                else:
                    # Upper Body / Desk / Webcam Framing (Knees not visible in frame)
                    # Determine whether person is Standing or Sitting using upper body elevation:
                    # 1. When STANDING in front of webcam:
                    #    - Head is at the upper top of the frame (head_norm_y < 0.28 or by1 < 0.15 * H)
                    #    - Torso is elongated vertically (bh > 0.55 * H)
                    # 2. When SITTING at desk:
                    #    - Head is positioned lower in frame (head_norm_y >= 0.28 and by1 >= 0.15 * H)
                    #    - Torso is relaxed or closer to bottom
                    is_high_in_frame = (head_norm_y is not None and head_norm_y < 0.28) or norm_top_y < 0.14
                    is_tall_span = norm_height > 0.58 and aspect_ratio > 1.30

                    if is_high_in_frame and is_tall_span:
                        raw_activity = "Standing"
                        motion_state = "Stationary (Standing Upright)"
                        conf = 0.90
                        posture_summary = f"Standing Upright ({spine:.1f}° Spine)"
                    elif (head_norm_y is not None and head_norm_y >= 0.28) or aspect_ratio <= 1.35 or norm_top_y >= 0.18:
                        raw_activity = "Sitting"
                        motion_state = "Stationary (Seated / Desk View)"
                        conf = 0.90
                        posture_summary = f"Desk Posture ({spine:.1f}° Spine)"
                    else:
                        # Default to Standing if upright and unconstrained
                        raw_activity = "Standing"
                        motion_state = "Stationary (Standing Upright)"
                        conf = 0.85
                        posture_summary = f"Upright Posture ({spine:.1f}° Spine)"

        # -------------------------------------------------------------
        # Temporal Smoothing Filter
        # -------------------------------------------------------------
        if track_id not in self.track_activity_history:
            self.track_activity_history[track_id] = deque(maxlen=self.smoothing_window)
            self.track_motion_history[track_id] = deque(maxlen=self.smoothing_window)

        hist_act = self.track_activity_history[track_id]
        hist_mot = self.track_motion_history[track_id]

        hist_act.append(raw_activity)
        hist_mot.append(motion_state)

        # Immediate override for critical safety state Falling and rapid Walking
        if raw_activity in ["Falling", "Walking", "Running"]:
            smoothed_activity = raw_activity
            smoothed_motion = motion_state
        else:
            smoothed_activity = max(set(hist_act), key=hist_act.count)
            smoothed_motion = max(set(hist_mot), key=hist_mot.count)

        features = {
            "spine_angle": round(pose.spine_angle, 1) if pose else 0.0,
            "aspect_ratio": round(aspect_ratio, 2),
            "velocity": velocity,
            "lower_body_visible": float(pose.lower_body_visible) if pose else 0.0,
            "has_knee_data": float(getattr(pose, "has_knee_data", False)) if pose else 0.0,
        }

        return ActivityResult(
            activity=smoothed_activity,
            motion_state=smoothed_motion,
            confidence=round(conf, 2),
            posture_summary=posture_summary,
            features=features,
        )
