"""
VisionDNA - Person Tracking Module
Maintains persistent IDs across frames, attaches pose states, and computes jitter-free velocity
and spatial trajectories with futuristic HUD telemetry.
"""

from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2

from src.detector import PersonDetection, PoseResult


@dataclass
class TrackedPerson:
    """Represents a tracked individual over time."""
    track_id: int
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    center: Tuple[int, int]
    pose: Optional[PoseResult] = None
    velocity: float = 0.0  # Normalized pixels per second or m/s proxy
    direction: str = "Stationary"
    history: List[Tuple[float, int, int]] = field(default_factory=list)  # (timestamp, cx, cy)
    missing_frames: int = 0
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)


class PersonTracker:
    """
    Tracks detected individuals with multi-frame window velocity estimation,
    trajectory smoothing, and tactical HUD visual rendering.
    """

    COLOR_PALETTE = [
        (0, 240, 255),    # Neon Cyan
        (255, 165, 0),    # Bright Amber
        (50, 255, 120),   # Matrix Emerald
        (255, 105, 180),  # Neon Magenta
        (0, 191, 255),    # Deep Sky
        (186, 85, 211),   # Medium Orchid
        (255, 215, 0),    # Gold
    ]

    def __init__(
        self,
        max_disappeared: int = 15,
        max_distance: float = 110.0,
        history_len: int = 25,
        jitter_deadzone_px: float = 2.0,
    ):
        self.next_track_id = 1
        self.tracked_people: Dict[int, TrackedPerson] = {}
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        self.history_len = history_len
        self.jitter_deadzone_px = jitter_deadzone_px

    def update(self, detections: List[PersonDetection]) -> List[TrackedPerson]:
        """Updates active tracks with new frame detections."""
        curr_time = time.time()

        if len(detections) == 0:
            to_remove = []
            for track_id, person in self.tracked_people.items():
                person.missing_frames += 1
                person.velocity = 0.0
                person.direction = "Stationary"
                if person.missing_frames > self.max_disappeared:
                    to_remove.append(track_id)
            for track_id in to_remove:
                del self.tracked_people[track_id]
            return list(self.tracked_people.values())

        if len(self.tracked_people) == 0:
            for det in detections:
                self._register_person(det, curr_time)
            return list(self.tracked_people.values())

        track_ids = list(self.tracked_people.keys())
        track_centers = [self.tracked_people[tid].center for tid in track_ids]
        det_centers = [det.center for det in detections]

        distances = np.zeros((len(track_ids), len(detections)), dtype=np.float32)
        for i, tc in enumerate(track_centers):
            for j, dc in enumerate(det_centers):
                distances[i, j] = np.linalg.norm(np.array(tc) - np.array(dc))

        matched_tracks = set()
        matched_dets = set()

        if distances.size > 0:
            rows = distances.min(axis=1).argsort()
            cols = distances.argmin(axis=1)[rows]

            for row, col in zip(rows, cols):
                if row in matched_tracks or col in matched_dets:
                    continue
                if distances[row, col] > self.max_distance:
                    continue

                track_id = track_ids[row]
                det = detections[col]
                self._update_person(track_id, det, curr_time)

                matched_tracks.add(row)
                matched_dets.add(col)

        for i, track_id in enumerate(track_ids):
            if i not in matched_tracks:
                self.tracked_people[track_id].missing_frames += 1
                self.tracked_people[track_id].velocity = 0.0
                self.tracked_people[track_id].direction = "Stationary"

        to_remove = [
            tid for tid, p in self.tracked_people.items()
            if p.missing_frames > self.max_disappeared
        ]
        for tid in to_remove:
            del self.tracked_people[tid]

        for j, det in enumerate(detections):
            if j not in matched_dets:
                self._register_person(det, curr_time)

        return [p for p in self.tracked_people.values() if p.missing_frames == 0]

    def _register_person(self, det: PersonDetection, timestamp: float):
        person = TrackedPerson(
            track_id=self.next_track_id,
            bbox=det.bbox,
            confidence=det.confidence,
            center=det.center,
            pose=det.pose,
            velocity=0.0,
            direction="Stationary",
            history=[(timestamp, det.center[0], det.center[1])],
            first_seen=timestamp,
            last_seen=timestamp,
        )
        self.tracked_people[self.next_track_id] = person
        self.next_track_id += 1

    def _update_person(self, track_id: int, det: PersonDetection, timestamp: float):
        person = self.tracked_people[track_id]
        new_center = det.center

        # Append to history buffer
        person.history.append((timestamp, new_center[0], new_center[1]))
        if len(person.history) > self.history_len:
            person.history.pop(0)

        # Multi-frame window velocity estimation (looking back 4-8 frames for smooth, stable velocity)
        k = min(6, len(person.history) - 1)
        if k >= 1:
            past_time, past_x, past_y = person.history[-1 - k]
            dt_window = max(0.01, timestamp - past_time)
            dx_window = new_center[0] - past_x
            dy_window = new_center[1] - past_y
            dist_window = np.sqrt(dx_window**2 + dy_window**2)

            # Instantaneous speed in estimated m/s (approx 120 px = 1 meter)
            if dist_window < self.jitter_deadzone_px * k:
                est_speed = 0.0
                direction = "Stationary"
            else:
                est_speed = (dist_window / dt_window) / 120.0
                if abs(dx_window) > abs(dy_window):
                    direction = "Right" if dx_window > 0 else "Left"
                else:
                    direction = "Down" if dy_window > 0 else "Up"
        else:
            est_speed = 0.0
            direction = "Stationary"

        # Smooth velocity with exponential moving filter
        smoothed_velocity = 0.60 * person.velocity + 0.40 * est_speed if person.velocity > 0 else est_speed
        if smoothed_velocity < 0.10:
            smoothed_velocity = 0.0
            direction = "Stationary"

        person.bbox = det.bbox
        person.confidence = det.confidence
        person.center = new_center
        person.pose = det.pose
        person.velocity = round(smoothed_velocity, 2)
        person.direction = direction
        person.missing_frames = 0
        person.last_seen = timestamp

    def draw_tracks(
        self,
        frame: np.ndarray,
        tracks: List[TrackedPerson],
    ) -> np.ndarray:
        """
        Renders clean, professional trajectory trails, bounding boxes, and ID badges.
        """
        for person in tracks:
            x1, y1, x2, y2 = person.bbox
            tid = person.track_id

            # Color palette (professional enterprise blue/cyan/emerald)
            color = self.COLOR_PALETTE[(tid - 1) % len(self.COLOR_PALETTE)]

            # 1. Subtle Trajectory Trail
            if len(person.history) > 1:
                pts = [pt[1:] for pt in person.history]
                for i in range(1, len(pts)):
                    cv2.line(frame, pts[i - 1], pts[i], color, 2, cv2.LINE_AA)

            # 2. Clean Bounding Box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)

            # 3. Clean Identity Badge
            speed_txt = f"{person.velocity:.1f} m/s" if person.velocity > 0.1 else "Stationary"
            label = f"Person #{tid:02d}  {int(person.confidence*100)}%  {speed_txt}"
            (lbl_w, lbl_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)

            badge_y1 = max(0, y1 - lbl_h - 8)
            badge_y2 = y1
            badge_x2 = x1 + lbl_w + 12

            cv2.rectangle(frame, (x1, badge_y1), (badge_x2, badge_y2), (15, 23, 42), -1)
            cv2.rectangle(frame, (x1, badge_y1), (badge_x2, badge_y2), color, 1)
            cv2.putText(frame, label, (x1 + 6, badge_y2 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (248, 250, 252), 1, cv2.LINE_AA)

        return frame
