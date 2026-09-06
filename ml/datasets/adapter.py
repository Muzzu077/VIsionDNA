"""
Dataset adapters for VisionDNA ML Pipeline.

Supports loading and standardizing datasets for:
- Human Activity Recognition (UCF101 / HMDB51 / NTU RGB+D / Fall Detection)
- Synthetic Kinematic Behavioral Sequences for Risk Prediction
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any


ACTIVITY_CLASSES = [
    "standing",
    "walking",
    "sitting",
    "running",
    "bending",
    "lying_down",
    "falling",
]

RISK_CLASSES = [
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
]


class DatasetAdapter:
    """Base adapter for converting raw datasets into temporal feature vectors."""

    def __init__(self, sequence_length: int = 30, feature_dim: int = 12):
        self.sequence_length = sequence_length
        self.feature_dim = feature_dim

    def generate_synthetic_dataset(
        self, num_samples: int = 1200, seed: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate reproducible temporal sequences of kinematic human features.
        Features per timestep (12 dims):
        0: pos_x (normalized [0, 1])
        1: pos_y (normalized [0, 1])
        2: velocity_x
        3: velocity_y
        4: speed (magnitude)
        5: acceleration
        6: bbox_aspect_ratio (width/height)
        7: bbox_area_norm
        8: posture_vertical_span
        9: dist_to_restricted_zone
        10: heading_angle (radians)
        11: temporal_variance
        
        Returns:
            X: Array of shape (num_samples, sequence_length, feature_dim)
            y_activity: Integer class labels for activity [0..6]
            y_risk_score: Float risk score [0..100]
            y_risk_class: Integer risk category [0..3]
        """
        np.random.seed(seed)
        X = np.zeros((num_samples, self.sequence_length, self.feature_dim), dtype=np.float32)
        y_activity = np.zeros(num_samples, dtype=np.int64)
        y_risk_score = np.zeros(num_samples, dtype=np.float32)
        y_risk_class = np.zeros(num_samples, dtype=np.int64)

        samples_per_class = num_samples // len(ACTIVITY_CLASSES)

        for i in range(num_samples):
            act_idx = min(i // samples_per_class, len(ACTIVITY_CLASSES) - 1)
            y_activity[i] = act_idx
            act_name = ACTIVITY_CLASSES[act_idx]

            # Generate kinematic trajectory based on activity class
            t = np.linspace(0, 1, self.sequence_length)
            noise = np.random.normal(0, 0.02, (self.sequence_length, self.feature_dim))

            if act_name == "standing":
                # Static position, low speed, tall narrow bbox (aspect ratio ~0.35)
                base_x = np.full(self.sequence_length, np.random.uniform(0.2, 0.8))
                base_y = np.full(self.sequence_length, np.random.uniform(0.4, 0.8))
                aspect = np.full(self.sequence_length, 0.35)
                speed = np.full(self.sequence_length, 0.02)
                risk = np.random.uniform(5, 20)

            elif act_name == "walking":
                # Moderate linear displacement, aspect ratio ~0.4, speed ~0.2
                dx = np.random.uniform(-0.3, 0.3)
                dy = np.random.uniform(-0.3, 0.3)
                start_x = np.random.uniform(0.3, 0.7)
                start_y = np.random.uniform(0.3, 0.7)
                base_x = start_x + dx * t
                base_y = start_y + dy * t
                aspect = 0.40 + 0.05 * np.sin(t * 10)
                speed = np.hypot(dx, dy) + 0.1
                risk = np.random.uniform(15, 35)

            elif act_name == "sitting":
                # Static position, lower height, squarish aspect ratio ~0.8
                base_x = np.full(self.sequence_length, np.random.uniform(0.2, 0.8))
                base_y = np.full(self.sequence_length, np.random.uniform(0.4, 0.8))
                aspect = np.full(self.sequence_length, 0.85)
                speed = np.full(self.sequence_length, 0.01)
                risk = np.random.uniform(5, 18)

            elif act_name == "running":
                # Rapid displacement, aspect ratio ~0.45, speed ~0.6
                dx = np.random.uniform(-0.6, 0.6)
                dy = np.random.uniform(-0.6, 0.6)
                start_x = np.random.uniform(0.2, 0.8)
                start_y = np.random.uniform(0.2, 0.8)
                base_x = np.clip(start_x + dx * t, 0, 1)
                base_y = np.clip(start_y + dy * t, 0, 1)
                aspect = 0.45 + 0.1 * np.sin(t * 18)
                speed = np.hypot(dx, dy) * 1.5 + 0.4
                risk = np.random.uniform(45, 75)

            elif act_name == "bending":
                # Bbox height decreases, aspect ratio increases to ~1.1
                base_x = np.full(self.sequence_length, np.random.uniform(0.2, 0.8))
                base_y = np.full(self.sequence_length, np.random.uniform(0.4, 0.8))
                aspect = 0.4 + 0.7 * (1.0 - np.cos(t * np.pi)) / 2.0
                speed = np.full(self.sequence_length, 0.05)
                risk = np.random.uniform(25, 45)

            elif act_name == "lying_down":
                # Horizontal orientation, wide aspect ratio ~1.8
                base_x = np.full(self.sequence_length, np.random.uniform(0.2, 0.8))
                base_y = np.full(self.sequence_length, np.random.uniform(0.6, 0.9))
                aspect = np.full(self.sequence_length, 1.8)
                speed = np.full(self.sequence_length, 0.02)
                risk = np.random.uniform(40, 65)

            elif act_name == "falling":
                # Transition from upright to lying down with sudden downward velocity spike
                base_x = np.full(self.sequence_length, np.random.uniform(0.3, 0.7))
                fall_start = int(self.sequence_length * 0.4)
                base_y = np.linspace(0.4, 0.85, self.sequence_length)
                aspect = np.zeros(self.sequence_length)
                aspect[:fall_start] = 0.4
                aspect[fall_start:] = np.linspace(0.4, 1.9, self.sequence_length - fall_start)
                speed = np.zeros(self.sequence_length)
                speed[fall_start : fall_start + 5] = 0.85
                risk = np.random.uniform(80, 98)

            # Zone proximity simulation (closer to restricted zone in top-right [0.7, 0.2] increases risk)
            dist_to_zone = np.sqrt((base_x - 0.75) ** 2 + (base_y - 0.2) ** 2)
            if np.min(dist_to_zone) < 0.15:
                risk = min(100.0, risk + 35.0)

            # Assign feature matrix
            vx = np.gradient(base_x)
            vy = np.gradient(base_y)
            acc = np.gradient(np.hypot(vx, vy))

            X[i, :, 0] = base_x
            X[i, :, 1] = base_y
            X[i, :, 2] = vx
            X[i, :, 3] = vy
            X[i, :, 4] = speed
            X[i, :, 5] = acc
            X[i, :, 6] = aspect
            X[i, :, 7] = aspect * 0.1
            X[i, :, 8] = 1.0 / (aspect + 0.1)
            X[i, :, 9] = dist_to_zone
            X[i, :, 10] = np.arctan2(vy, vx + 1e-6)
            X[i, :, 11] = np.var(speed)

            # Add noise
            X[i] = np.clip(X[i] + noise, -2.0, 2.0)

            y_risk_score[i] = float(np.clip(risk, 0.0, 100.0))
            if y_risk_score[i] < 30.0:
                y_risk_class[i] = 0  # LOW
            elif y_risk_score[i] < 60.0:
                y_risk_class[i] = 1  # MEDIUM
            elif y_risk_score[i] < 80.0:
                y_risk_class[i] = 2  # HIGH
            else:
                y_risk_class[i] = 3  # CRITICAL

        return X, y_activity, y_risk_score, y_risk_class
