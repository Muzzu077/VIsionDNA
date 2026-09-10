"""
VisionDNA - Multi-Condition Risk Analysis Engine
Calculates normalized 0-100 risk scores based on:
1. Fall Incidents (Critical horizontal biomechanical posture)
2. Restricted / Danger Zone Intrusion & Proximity
3. Multi-Person Collision Proximity
4. Abnormal / High-Velocity Movement
Features tactical visual hazard zones with perimeter indicators.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2

from src.activity import ActivityResult
from src.prediction import PredictionResult
from src.tracker import TrackedPerson


@dataclass
class RiskAssessment:
    """Encapsulates computed safety risk for an individual."""
    person_id: int
    risk_score: float  # 0.0 to 100.0
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    primary_reason: str
    all_reasons: List[str] = field(default_factory=list)
    in_danger_zone: bool = False
    approaching_danger_zone: bool = False
    is_fall: bool = False
    is_collision_risk: bool = False
    is_abnormal_movement: bool = False


class RiskEngine:
    """
    Evaluates real-time visual streams and predicted states against safety policies.
    """

    def __init__(
        self,
        danger_zones: Optional[List[Dict]] = None,
        proximity_threshold_px: float = 80.0,
        low_max: float = 30.0,
        medium_max: float = 60.0,
    ):
        self.danger_zones = danger_zones or [
            {
                "name": "Danger Zone Alpha",
                "points": [[420, 60], [620, 60], [620, 320], [420, 320]],
                "color": (0, 0, 255),
                "risk_weight": 45.0,
            }
        ]
        self.proximity_threshold_px = proximity_threshold_px
        self.low_max = low_max
        self.medium_max = medium_max

    def assess(
        self,
        person: TrackedPerson,
        all_people: List[TrackedPerson],
        activity_res: ActivityResult,
        prediction_res: Optional[PredictionResult] = None,
    ) -> RiskAssessment:
        """
        Calculates a deterministic composite risk score (0-100) and risk level.
        """
        score = 0.0
        reasons = []
        is_fall = False
        in_zone = False
        approaching_zone = False
        is_collision = False
        is_abnormal = False

        # Factor 1: Fall Detection (Weight: 75.0)
        if activity_res.activity == "Falling":
            fall_weight = 75.0 * activity_res.confidence
            score += fall_weight
            is_fall = True
            reasons.append("Possible Fall Detected (Critical Posture)")

        # Factor 2: Restricted Danger Zone Intrusion (Weight: 45.0)
        px, py = person.center
        for zone in self.danger_zones:
            pts = np.array(zone["points"], dtype=np.int32)
            dist_inside = cv2.pointPolygonTest(pts, (float(px), float(py)), False)
            if dist_inside >= 0:
                in_zone = True
                score += zone.get("risk_weight", 45.0)
                reasons.append(f"Restricted Zone Intrusion ({zone['name']})")
                break

        # Factor 3: Predictive Zone Approach (Weight: 25.0)
        if not in_zone and prediction_res and prediction_res.trajectory_trend == "Approaching Restricted Zone":
            approaching_zone = True
            score += 25.0
            reasons.append("Projected Trajectory Approaches Restricted Zone")

        # Factor 4: Inter-Person Proximity & Collision Risk (Weight: 30.0)
        for other in all_people:
            if other.track_id == person.track_id:
                continue
            ox, oy = other.center
            dist = np.sqrt((px - ox)**2 + (py - oy)**2)
            if dist < self.proximity_threshold_px:
                is_collision = True
                proximity_score = max(0.0, (self.proximity_threshold_px - dist) / self.proximity_threshold_px * 30.0)
                score += proximity_score
                reasons.append(f"Proximity Hazard: Collision Risk with Person #{other.track_id:02d}")
                break

        # Factor 5: Abnormal High Velocity Movement (Weight: 20.0)
        if person.velocity > 3.4 and activity_res.activity in ["Running"]:
            is_abnormal = True
            score += 20.0
            reasons.append("Abnormal High-Speed Movement Detected")

        # Normalize score between 0 and 100
        final_score = min(100.0, max(0.0, score))

        # Determine Risk Level Category
        if final_score > self.medium_max:
            level = "HIGH"
        elif final_score > self.low_max:
            level = "MEDIUM"
        else:
            level = "LOW"

        primary_reason = reasons[0] if len(reasons) > 0 else "Normal Operational Behavior"

        return RiskAssessment(
            person_id=person.track_id,
            risk_score=round(final_score, 1),
            risk_level=level,
            primary_reason=primary_reason,
            all_reasons=reasons,
            in_danger_zone=in_zone,
            approaching_danger_zone=approaching_zone,
            is_fall=is_fall,
            is_collision_risk=is_collision,
            is_abnormal_movement=is_abnormal,
        )

    def draw_zones(self, frame: np.ndarray) -> np.ndarray:
        """
        Draws tactical high-tech safety and danger zones onto the camera frame with
        semi-transparent red hatch fill, neon boundary lines, and caution badges.
        """
        for zone in self.danger_zones:
            pts = np.array(zone["points"], dtype=np.int32)
            color = zone.get("color", (0, 0, 240))
            name = zone.get("name", "Restricted Zone")

            # Semi-transparent fill
            overlay = frame.copy()
            cv2.fillPoly(overlay, [pts], color)
            cv2.addWeighted(overlay, 0.18, frame, 0.82, 0, frame)

            # High-intensity perimeter border
            cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2, lineType=cv2.LINE_AA)

            # Draw corner markers
            for pt in pts:
                cv2.circle(frame, (int(pt[0]), int(pt[1])), 4, (255, 255, 255), -1, cv2.LINE_AA)
                cv2.circle(frame, (int(pt[0]), int(pt[1])), 7, color, 1, cv2.LINE_AA)

            # Zone label badge
            min_x = int(np.min(pts[:, 0]))
            min_y = int(np.min(pts[:, 1]))
            badge_text = f"Restricted: {name}"
            (tw, th), _ = cv2.getTextSize(badge_text, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)

            cv2.rectangle(frame, (min_x, max(0, min_y - 20)), (min_x + tw + 10, max(th + 4, min_y)), (15, 23, 42), -1)
            cv2.rectangle(frame, (min_x, max(0, min_y - 20)), (min_x + tw + 10, max(th + 4, min_y)), color, 1)
            cv2.putText(
                frame,
                badge_text,
                (min_x + 5, max(th + 2, min_y - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.36,
                (248, 250, 252),
                1,
                cv2.LINE_AA,
            )

        return frame
