"""
VisionDNA - Digital Twin Module
Renders an ultra-clear, high-definition humanoid biomechanical avatar for every detected person,
accurately reflecting real-world spatial position, posture, limb articulation, and motion state
in both Light Enterprise Studio and Dark Slate modes.
"""

from dataclasses import dataclass, field
import time
import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2

from src.activity import ActivityResult
from src.pose import PoseResult
from src.tracker import TrackedPerson


@dataclass
class DigitalTwinState:
    """Structured digital representation of a real-world person."""
    person_id: int
    position: Tuple[int, int]  # (x, y) coordinates in scene
    bbox: Tuple[int, int, int, int] = (0, 0, 100, 100)
    activity: str = "Standing"
    motion_state: str = "Stationary (Standing)"
    activity_confidence: float = 0.85
    posture_summary: str = "Upright Torso"
    velocity: float = 0.0  # m/s proxy
    direction: str = "Stationary"
    pose_state: str = "Upright"  # "Upright", "Bent Forward", "Seated", "Horizontal/Fallen"
    spine_angle: float = 0.0
    knee_angle: float = 180.0
    risk_level: str = "LOW"  # "LOW", "MEDIUM", "HIGH"
    risk_score: float = 0.0  # 0 to 100
    risk_reasons: List[str] = field(default_factory=list)
    predicted_activity: str = "Standing"
    prediction_confidence: float = 0.0
    trajectory_history: List[Tuple[int, int]] = field(default_factory=list)
    pose_landmarks: Optional[Dict] = None
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().strftime("%H:%M:%S"))


class DigitalTwinEngine:
    """
    Maintains active Digital Twins for all detected individuals and renders a high-definition
    multi-entity humanoid biomechanical blueprint canvas with real human posture and positions.
    """

    def __init__(self):
        self.twins: Dict[int, DigitalTwinState] = {}

    def update_twin(
        self,
        person: TrackedPerson,
        activity_res: ActivityResult,
        pose_res: Optional[PoseResult] = None,
        risk_score: float = 0.0,
        risk_level: str = "LOW",
        risk_reasons: Optional[List[str]] = None,
        predicted_activity: str = "Insufficient Data",
        prediction_conf: float = 0.0,
    ) -> DigitalTwinState:
        """Updates or registers a digital twin state for a tracked person."""
        pose_state = "Upright"
        spine_ang = 0.0
        knee_ang = 180.0

        if pose_res and pose_res.is_valid:
            spine_ang = pose_res.spine_angle
            if getattr(pose_res, "has_knee_data", False):
                knee_ang = (pose_res.left_knee_angle + pose_res.right_knee_angle) / 2.0
            
            if spine_ang > 48:
                pose_state = "Horizontal/Fallen"
            elif spine_ang > 26:
                pose_state = "Bent Forward"
            elif getattr(activity_res, "activity", "") == "Sitting":
                pose_state = "Seated"
        elif getattr(activity_res, "activity", "") == "Sitting":
            pose_state = "Seated"

        traj_coords = [(pt[1], pt[2]) for pt in person.history] if person.history else [person.center]

        twin = DigitalTwinState(
            person_id=person.track_id,
            position=person.center,
            bbox=person.bbox,
            activity=getattr(activity_res, "activity", "Standing"),
            motion_state=getattr(activity_res, "motion_state", getattr(activity_res, "activity", "Stationary")),
            activity_confidence=getattr(activity_res, "confidence", 0.85),
            posture_summary=getattr(activity_res, "posture_summary", "Upright"),
            velocity=person.velocity,
            direction=person.direction,
            pose_state=pose_state,
            spine_angle=round(spine_ang, 1),
            knee_angle=round(knee_ang, 1),
            risk_level=risk_level,
            risk_score=round(risk_score, 1),
            risk_reasons=risk_reasons or [],
            predicted_activity=predicted_activity,
            prediction_confidence=round(prediction_conf, 2),
            trajectory_history=traj_coords,
            pose_landmarks=pose_res.landmarks if (pose_res and pose_res.is_valid) else None,
            timestamp=datetime.datetime.now().strftime("%H:%M:%S"),
        )
        self.twins[person.track_id] = twin
        return twin

    def cleanup_twins(self, active_track_ids: List[int]):
        """Removes digital twins for inactive tracks."""
        to_delete = [tid for tid in self.twins if tid not in active_track_ids]
        for tid in to_delete:
            del self.twins[tid]

    def _draw_humanoid_avatar(
        self,
        canvas: np.ndarray,
        twin: DigitalTwinState,
        accent_color: Tuple[int, int, int],
        glow_color: Tuple[int, int, int],
        is_light_mode: bool = True,
    ):
        """
        Renders a clean, anatomical humanoid mannequin avatar showing real human posture.
        """
        cx, cy = twin.position
        w_box = max(60, min(140, twin.bbox[2] - twin.bbox[0]))
        h_box = max(100, min(220, twin.bbox[3] - twin.bbox[1]))

        # Ground target shadow disk
        ground_y = min(canvas.shape[0] - 25, cy + h_box // 2)
        cv2.ellipse(canvas, (cx, ground_y), (36, 12), 0, 0, 360, glow_color, -1)
        cv2.ellipse(canvas, (cx, ground_y), (36, 12), 0, 0, 360, accent_color, 1, cv2.LINE_AA)

        # Scale avatar height
        avatar_h = int(min(170, max(100, h_box * 0.92)))
        head_radius = max(10, int(avatar_h * 0.10))
        shoulder_span = int(avatar_h * 0.28)
        hip_span = int(avatar_h * 0.20)
        torso_len = int(avatar_h * 0.35)
        leg_len = int(avatar_h * 0.40)

        act = twin.activity
        spine_tilt = twin.spine_angle

        # -------------------------------------------------------------
        # A. FALLEN / HORIZONTAL POSTURE
        # -------------------------------------------------------------
        if act == "Falling" or twin.pose_state == "Horizontal/Fallen":
            hy = ground_y - 12
            head_x = cx - avatar_h // 2 + head_radius
            hip_x = cx + 15
            feet_x = cx + avatar_h // 2

            cv2.circle(canvas, (head_x, hy), head_radius, glow_color, -1)
            cv2.circle(canvas, (head_x, hy), head_radius, accent_color, 2, cv2.LINE_AA)
            cv2.line(canvas, (head_x + head_radius, hy), (hip_x, hy), accent_color, 5, cv2.LINE_AA)
            cv2.circle(canvas, (hip_x, hy), 5, (255, 255, 255), -1)
            cv2.line(canvas, (hip_x, hy), (feet_x, hy + 4), accent_color, 4, cv2.LINE_AA)
            cv2.circle(canvas, (cx, hy), 40, (220, 38, 38), 2, cv2.LINE_AA)

        # -------------------------------------------------------------
        # B. SEATED POSTURE
        # -------------------------------------------------------------
        elif act == "Sitting" or twin.pose_state == "Seated":
            seat_y = ground_y - int(leg_len * 0.55)
            hip_pt = (cx, seat_y)
            neck_y = seat_y - torso_len
            head_center = (cx, neck_y - head_radius - 2)

            chair_col = (148, 163, 184) if is_light_mode else (51, 65, 85)
            cv2.line(canvas, (cx - 20, seat_y), (cx + 20, seat_y), chair_col, 2, cv2.LINE_AA)
            cv2.line(canvas, (cx - 16, seat_y), (cx - 16, seat_y - torso_len + 8), chair_col, 2, cv2.LINE_AA)
            cv2.line(canvas, (cx - 16, seat_y), (cx - 16, ground_y), chair_col, 2, cv2.LINE_AA)
            cv2.line(canvas, (cx + 16, seat_y), (cx + 16, ground_y), chair_col, 2, cv2.LINE_AA)

            # Head & Visor
            cv2.circle(canvas, head_center, head_radius, glow_color, -1)
            cv2.circle(canvas, head_center, head_radius, accent_color, 2, cv2.LINE_AA)

            # Torso
            cv2.line(canvas, (cx, neck_y), hip_pt, accent_color, 6, cv2.LINE_AA)

            # Arms
            l_sh = (cx - shoulder_span // 2, neck_y + 4)
            r_sh = (cx + shoulder_span // 2, neck_y + 4)
            cv2.line(canvas, l_sh, r_sh, accent_color, 3, cv2.LINE_AA)
            l_elb = (cx - shoulder_span // 2 - 4, neck_y + torso_len // 2)
            r_elb = (cx + shoulder_span // 2 + 4, neck_y + torso_len // 2)
            l_hnd = (cx - 10, seat_y - 2)
            r_hnd = (cx + 10, seat_y - 2)
            cv2.line(canvas, l_sh, l_elb, accent_color, 3, cv2.LINE_AA)
            cv2.line(canvas, l_elb, l_hnd, accent_color, 3, cv2.LINE_AA)
            cv2.line(canvas, r_sh, r_elb, accent_color, 3, cv2.LINE_AA)
            cv2.line(canvas, r_elb, r_hnd, accent_color, 3, cv2.LINE_AA)

            # Seated Legs
            l_knee = (cx - 15, seat_y)
            r_knee = (cx + 15, seat_y)
            l_foot = (cx - 15, ground_y)
            r_foot = (cx + 15, ground_y)
            cv2.line(canvas, hip_pt, l_knee, accent_color, 4, cv2.LINE_AA)
            cv2.line(canvas, hip_pt, r_knee, accent_color, 4, cv2.LINE_AA)
            cv2.line(canvas, l_knee, l_foot, accent_color, 4, cv2.LINE_AA)
            cv2.line(canvas, r_knee, r_foot, accent_color, 4, cv2.LINE_AA)
            cv2.circle(canvas, l_knee, 3, (255, 255, 255), -1)
            cv2.circle(canvas, r_knee, 3, (255, 255, 255), -1)

        # -------------------------------------------------------------
        # C. UPRIGHT STANDING & WALKING POSTURE
        # -------------------------------------------------------------
        else:
            hip_y = ground_y - leg_len
            hip_pt = (cx, hip_y)
            
            tilt_rad = np.radians(min(55, spine_tilt)) if spine_tilt > 15 else 0.0
            neck_dx = int(torso_len * np.sin(tilt_rad))
            neck_dy = int(torso_len * np.cos(tilt_rad))
            neck_pt = (cx + neck_dx, hip_y - neck_dy)
            head_center = (neck_pt[0] + int(head_radius * np.sin(tilt_rad)), neck_pt[1] - head_radius - 2)

            # Head
            cv2.circle(canvas, head_center, head_radius, glow_color, -1)
            cv2.circle(canvas, head_center, head_radius, accent_color, 2, cv2.LINE_AA)

            # Torso Column
            cv2.line(canvas, neck_pt, hip_pt, accent_color, 6, cv2.LINE_AA)

            # Arms
            l_sh = (neck_pt[0] - shoulder_span // 2, neck_pt[1] + 4)
            r_sh = (neck_pt[0] + shoulder_span // 2, neck_pt[1] + 4)
            cv2.line(canvas, l_sh, r_sh, accent_color, 4, cv2.LINE_AA)

            if act in ["Walking", "Running"]:
                arm_offset = int(16 * np.sin(time.time() * 6.0))
                l_elb = (l_sh[0] - 4, l_sh[1] + torso_len // 2 + arm_offset)
                r_elb = (r_sh[0] + 4, r_sh[1] + torso_len // 2 - arm_offset)
                l_hnd = (l_elb[0] + 3, l_elb[1] + torso_len // 2)
                r_hnd = (r_elb[0] - 3, r_elb[1] + torso_len // 2)
            else:
                l_elb = (l_sh[0] - 6, l_sh[1] + torso_len // 2)
                r_elb = (r_sh[0] + 6, r_sh[1] + torso_len // 2)
                l_hnd = (l_sh[0] - 8, hip_y + 4)
                r_hnd = (r_sh[0] + 8, hip_y + 4)

            cv2.line(canvas, l_sh, l_elb, accent_color, 3, cv2.LINE_AA)
            cv2.line(canvas, l_elb, l_hnd, accent_color, 3, cv2.LINE_AA)
            cv2.line(canvas, r_sh, r_elb, accent_color, 3, cv2.LINE_AA)
            cv2.line(canvas, r_elb, r_hnd, accent_color, 3, cv2.LINE_AA)
            cv2.circle(canvas, l_elb, 3, (255, 255, 255), -1)
            cv2.circle(canvas, r_elb, 3, (255, 255, 255), -1)

            # Pelvis & Articulated Legs
            cv2.circle(canvas, hip_pt, 5, (255, 255, 255), -1)
            l_hip = (cx - hip_span // 2, hip_y)
            r_hip = (cx + hip_span // 2, hip_y)
            cv2.line(canvas, l_hip, r_hip, accent_color, 4, cv2.LINE_AA)

            if act in ["Walking", "Running"]:
                leg_stride = int(20 * np.sin(time.time() * 6.0))
                l_knee = (l_hip[0] - leg_stride // 2, hip_y + leg_len // 2)
                r_knee = (r_hip[0] + leg_stride // 2, hip_y + leg_len // 2)
                l_foot = (l_knee[0] - leg_stride // 2, ground_y)
                r_foot = (r_knee[0] + leg_stride // 2, ground_y)
            else:
                l_knee = (l_hip[0] - 3, hip_y + leg_len // 2)
                r_knee = (r_hip[0] + 3, hip_y + leg_len // 2)
                l_foot = (l_hip[0] - 5, ground_y)
                r_foot = (r_hip[0] + 5, ground_y)

            cv2.line(canvas, l_hip, l_knee, accent_color, 4, cv2.LINE_AA)
            cv2.line(canvas, l_knee, l_foot, accent_color, 4, cv2.LINE_AA)
            cv2.line(canvas, r_hip, r_knee, accent_color, 4, cv2.LINE_AA)
            cv2.line(canvas, r_knee, r_foot, accent_color, 4, cv2.LINE_AA)
            cv2.circle(canvas, l_knee, 3, (255, 255, 255), -1)
            cv2.circle(canvas, r_knee, 3, (255, 255, 255), -1)

            cv2.line(canvas, (l_foot[0] - 5, ground_y), (l_foot[0] + 5, ground_y), accent_color, 2, cv2.LINE_AA)
            cv2.line(canvas, (r_foot[0] - 5, ground_y), (r_foot[0] + 5, ground_y), accent_color, 2, cv2.LINE_AA)

        # Floating Identity Badge
        badge_y = max(38, cy - avatar_h // 2 - 20)
        badge_label = f"P{twin.person_id:02d}  {twin.activity}"
        (bw, bh), _ = cv2.getTextSize(badge_label, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)

        box_bg = (255, 255, 255) if is_light_mode else (15, 23, 42)
        txt_col = (15, 23, 42) if is_light_mode else (248, 250, 252)

        cv2.rectangle(canvas, (cx - bw // 2 - 6, badge_y - bh - 6), (cx + bw // 2 + 6, badge_y + 2), box_bg, -1)
        cv2.rectangle(canvas, (cx - bw // 2 - 6, badge_y - bh - 6), (cx + bw // 2 + 6, badge_y + 2), accent_color, 1)
        cv2.putText(canvas, badge_label, (cx - bw // 2, badge_y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.36, txt_col, 1, cv2.LINE_AA)

    def render_canvas(
        self,
        width: int = 640,
        height: int = 480,
        pose_res: Optional[PoseResult] = None,
        theme_colors: Optional[Dict] = None,
        danger_zones: Optional[List[Dict]] = None,
    ) -> np.ndarray:
        """
        Renders the Digital Twin Blueprint canvas containing realistic humanoid avatars.
        """
        canvas = np.zeros((height, width, 3), dtype=np.uint8)

        is_light = theme_colors.get("is_light", True) if theme_colors else True
        bg_rgb = theme_colors.get("cv_bg", (248, 250, 252)) if theme_colors else (248, 250, 252)
        grid_rgb = theme_colors.get("cv_grid", (226, 232, 240)) if theme_colors else (226, 232, 240)
        hdr_bg = theme_colors.get("hdr_bg", (255, 255, 255)) if theme_colors else (255, 255, 255)
        text_primary = theme_colors.get("text_primary", (15, 23, 42)) if theme_colors else (15, 23, 42)
        text_muted = theme_colors.get("text_muted", (100, 116, 139)) if theme_colors else (100, 116, 139)

        # 1. Background Grid
        canvas[:] = bg_rgb
        for x in range(0, width, 40):
            cv2.line(canvas, (x, 0), (x, height), grid_rgb, 1)
        for y in range(0, height, 40):
            cv2.line(canvas, (0, y), (width, y), grid_rgb, 1)

        # 2. Draw Danger Zones on Digital Twin Map
        if danger_zones:
            for zone in danger_zones:
                pts = np.array(zone["points"], dtype=np.int32)
                zone_overlay = canvas.copy()
                cv2.fillPoly(zone_overlay, [pts], (220, 38, 38))
                cv2.addWeighted(zone_overlay, 0.15, canvas, 0.85, 0, canvas)
                cv2.polylines(canvas, [pts], isClosed=True, color=(220, 38, 38), thickness=2, lineType=cv2.LINE_AA)
                
                min_x = int(np.min(pts[:, 0]))
                min_y = int(np.min(pts[:, 1]))
                cv2.putText(
                    canvas,
                    f"Restricted: {zone.get('name', 'Alpha')}",
                    (min_x + 6, max(20, min_y + 18)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.38,
                    (220, 38, 38),
                    1,
                    cv2.LINE_AA,
                )

        # 3. Top Header
        cv2.rectangle(canvas, (0, 0), (width, 36), hdr_bg, -1)
        cv2.line(canvas, (0, 36), (width, 36), grid_rgb, 1)

        cv2.putText(
            canvas,
            "Digital Twin",
            (14, 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            text_primary,
            2,
            cv2.LINE_AA,
        )

        active_cnt = len(self.twins)
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        header_stats = f"{active_cnt} Active Entities  |  Synchronized {now_time}"
        (hw, _), _ = cv2.getTextSize(header_stats, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
        cv2.putText(
            canvas,
            header_stats,
            (width - hw - 14, 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            text_muted,
            1,
            cv2.LINE_AA,
        )

        # Zero entities message
        if active_cnt == 0:
            cv2.putText(
                canvas,
                "No entities currently detected in active scene",
                (int(width * 0.20), int(height * 0.52)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                text_muted,
                1,
                cv2.LINE_AA,
            )
            return canvas

        # 4. Render Humanoid Avatars
        primary_twin = None
        for tid, twin in self.twins.items():
            if len(twin.trajectory_history) > 1:
                t_pts = np.array(twin.trajectory_history, np.int32).reshape((-1, 1, 2))
                t_color = (220, 38, 38) if twin.risk_level == "HIGH" else ((217, 119, 6) if twin.risk_level == "MEDIUM" else (2, 132, 199))
                cv2.polylines(canvas, [t_pts], isClosed=False, color=t_color, thickness=2, lineType=cv2.LINE_AA)

            if twin.risk_level == "HIGH":
                e_color = (220, 38, 38)     # Red
                e_glow = (254, 226, 226) if is_light else (153, 27, 27)
            elif twin.risk_level == "MEDIUM":
                e_color = (217, 119, 6)     # Amber
                e_glow = (254, 243, 199) if is_light else (146, 64, 14)
            else:
                e_color = (2, 132, 199)     # Enterprise Cobalt
                e_glow = (224, 242, 254) if is_light else (7, 89, 133)

            self._draw_humanoid_avatar(canvas, twin, e_color, e_glow, is_light_mode=is_light)

            if primary_twin is None or twin.risk_score > primary_twin.risk_score:
                primary_twin = twin

        # 5. Bottom Telemetry Bar
        if primary_twin is not None:
            hud_y = height - 34
            cv2.rectangle(canvas, (0, hud_y), (width, height), hdr_bg, -1)
            cv2.line(canvas, (0, hud_y), (width, hud_y), grid_rgb, 1)

            p_risk_color = (220, 38, 38) if primary_twin.risk_level == "HIGH" else ((217, 119, 6) if primary_twin.risk_level == "MEDIUM" else (5, 150, 105))
            hud_text = f"Target: P{primary_twin.person_id:02d}  |  {primary_twin.motion_state}  |  {primary_twin.velocity:.1f} m/s  |  Status: {primary_twin.risk_level}"
            cv2.putText(canvas, hud_text, (12, hud_y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.38, text_primary, 1, cv2.LINE_AA)
            cv2.circle(canvas, (width - 16, hud_y + 17), 4, p_risk_color, -1)

        return canvas
