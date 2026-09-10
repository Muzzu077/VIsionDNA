"""
VisionDNA - Predictive Human Activity & Movement Module
Predicts likely next activities and future spatial trajectories based on historical transitions,
velocity vector extrapolation, and kinematic trends.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2


@dataclass
class PredictionResult:
    """Encapsulates predictive activity and movement forecasts."""
    current_activity: str
    predicted_next_activity: str
    probability: float  # 0.0 to 1.0
    predicted_future_position: Tuple[int, int]  # Extrapolated (x, y) 1-2 seconds ahead
    trajectory_trend: str  # "Accelerating", "Decelerating", "Approaching Zone", "Steady"
    is_sufficient_data: bool = True


class ActivityPredictor:
    """
    Predictive engine modeling sequence transitions and spatial vector trends.
    """

    # Empirical Markov transition matrix between fundamental human activities
    # Rows: current activity -> Columns: next activity
    ACTIVITIES = ["Standing", "Walking", "Sitting", "Running", "Bending", "Falling"]
    
    TRANSITIONS: Dict[str, Dict[str, float]] = {
        "Standing": {
            "Standing": 0.55,
            "Walking": 0.30,
            "Sitting": 0.08,
            "Bending": 0.05,
            "Running": 0.01,
            "Falling": 0.01,
        },
        "Walking": {
            "Walking": 0.60,
            "Standing": 0.22,
            "Running": 0.12,
            "Bending": 0.04,
            "Sitting": 0.01,
            "Falling": 0.01,
        },
        "Sitting": {
            "Sitting": 0.70,
            "Standing": 0.24,
            "Bending": 0.04,
            "Walking": 0.01,
            "Running": 0.00,
            "Falling": 0.01,
        },
        "Running": {
            "Running": 0.50,
            "Walking": 0.35,
            "Standing": 0.08,
            "Falling": 0.05,
            "Bending": 0.02,
            "Sitting": 0.00,
        },
        "Bending": {
            "Standing": 0.50,
            "Bending": 0.35,
            "Walking": 0.10,
            "Sitting": 0.03,
            "Falling": 0.02,
            "Running": 0.00,
        },
        "Falling": {
            "Falling": 0.60,
            "Sitting": 0.20,
            "Standing": 0.15,
            "Walking": 0.05,
            "Bending": 0.00,
            "Running": 0.00,
        },
    }

    def __init__(self, min_history_frames: int = 5, history_len: int = 20):
        self.min_history_frames = min_history_frames
        self.history_len = history_len
        # History storage per track ID: deque of (activity, velocity, (cx, cy))
        self.track_history: Dict[int, deque] = {}

    def update_history(
        self,
        track_id: int,
        activity: str,
        velocity: float,
        position: Tuple[int, int],
    ):
        """Records an observation into the track's temporal history buffer."""
        if track_id not in self.track_history:
            self.track_history[track_id] = deque(maxlen=self.history_len)
        self.track_history[track_id].append((activity, velocity, position))

    def predict(
        self,
        track_id: int,
        current_activity: str,
        current_velocity: float,
        current_position: Tuple[int, int],
        danger_zones: Optional[List[Dict]] = None,
    ) -> PredictionResult:
        """
        Predicts next activity and projected future position.
        """
        self.update_history(track_id, current_activity, current_velocity, current_position)
        history = self.track_history.get(track_id, deque())

        if len(history) < self.min_history_frames:
            return PredictionResult(
                current_activity=current_activity,
                predicted_next_activity="Insufficient Data",
                probability=0.0,
                predicted_future_position=current_position,
                trajectory_trend="Establishing Baseline",
                is_sufficient_data=False,
            )

        # 1. Extrapolate Future Position (1.0 second ahead)
        # Calculate recent velocity vector (dx, dy)
        positions = [p[2] for p in history]
        if len(positions) >= 3:
            dx = (positions[-1][0] - positions[0][0]) / (len(positions) - 1)
            dy = (positions[-1][1] - positions[0][1]) / (len(positions) - 1)
        else:
            dx, dy = 0, 0

        # Project 15 frames ahead (~0.5 - 1.0 sec)
        fut_x = int(current_position[0] + dx * 15)
        fut_y = int(current_position[1] + dy * 15)
        future_pos = (max(0, min(1280, fut_x)), max(0, min(720, fut_y)))

        # 2. Check Trajectory Trend & Kinematics
        velocities = [p[1] for p in history]
        vel_diff = velocities[-1] - velocities[0]
        if vel_diff > 0.8:
            trend = "Accelerating"
        elif vel_diff < -0.8:
            trend = "Decelerating"
        else:
            trend = "Steady"

        # Check if approaching danger zone
        approaching_zone = False
        if danger_zones:
            for zone in danger_zones:
                pts = np.array(zone["points"], dtype=np.int32)
                # If future position enters danger zone
                if cv2.pointPolygonTest(pts, (float(future_pos[0]), float(future_pos[1])), False) >= 0:
                    approaching_zone = True
                    trend = "Approaching Restricted Zone"
                    break

        # 3. Predict Next Activity using Markov Model conditioned on Velocity Trend
        transition_probs = self.TRANSITIONS.get(current_activity, self.TRANSITIONS["Standing"]).copy()

        # Dynamic adjustment based on acceleration
        if trend == "Accelerating" and current_activity in ["Standing", "Walking"]:
            transition_probs["Running"] = transition_probs.get("Running", 0.0) + 0.25
            transition_probs["Walking"] = transition_probs.get("Walking", 0.0) + 0.15
        elif trend == "Decelerating" and current_activity in ["Walking", "Running"]:
            transition_probs["Standing"] = transition_probs.get("Standing", 0.0) + 0.30

        # Normalize probabilities
        total_p = sum(transition_probs.values())
        normalized_probs = {k: v / total_p for k, v in transition_probs.items()}

        # Pick most likely next activity (other than just repeating current if transition is high)
        sorted_transitions = sorted(normalized_probs.items(), key=lambda item: item[1], reverse=True)
        likely_next, prob = sorted_transitions[0]

        # If highest is current activity and second highest has good probability, pick second highest if moving
        if likely_next == current_activity and len(sorted_transitions) > 1 and current_velocity > 0.5:
            second_next, second_prob = sorted_transitions[1]
            if second_prob > 0.25:
                likely_next, prob = second_next, second_prob

        return PredictionResult(
            current_activity=current_activity,
            predicted_next_activity=likely_next,
            probability=round(prob, 2),
            predicted_future_position=future_pos,
            trajectory_trend=trend,
            is_sufficient_data=True,
        )

    def cleanup(self, active_track_ids: List[int]):
        """Cleans history of disconnected tracks."""
        to_del = [tid for tid in self.track_history if tid not in active_track_ids]
        for tid in to_del:
            del self.track_history[tid]
