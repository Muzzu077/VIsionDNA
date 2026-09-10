"""
VisionDNA - Unified Person Detection & Pose Module
Uses YOLOv8-Pose in a single high-efficiency inference pass on CPU to extract
both person bounding boxes and 17 full-body keypoints simultaneously.
Features tactical Sci-Fi HUD overlays, corner-bracket reticles, and glowing multi-color skeleton rendering.
"""

from dataclasses import dataclass, field
import os
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2
from ultralytics import YOLO


@dataclass
class PoseLandmark:
    """Structured coordinate container for a single landmark point."""
    x: float  # Normalized 0.0 to 1.0
    y: float  # Normalized 0.0 to 1.0
    visibility: float
    pixel_x: int = 0
    pixel_y: int = 0


@dataclass
class PoseResult:
    """Full body pose state with calculated geometric angles and body proportions."""
    landmarks: Dict[str, PoseLandmark] = field(default_factory=dict)
    spine_angle: float = 0.0  # Angle of torso relative to vertical (0 = upright, 90 = horizontal)
    left_knee_angle: float = 180.0
    right_knee_angle: float = 180.0
    left_hip_angle: float = 180.0
    right_hip_angle: float = 180.0
    left_elbow_angle: float = 180.0
    right_elbow_angle: float = 180.0
    body_aspect_ratio: float = 1.0  # (height / width)
    lower_body_visible: bool = False
    has_knee_data: bool = False
    has_hip_data: bool = False
    torso_length_px: float = 0.0
    is_valid: bool = False


@dataclass
class PersonDetection:
    """Structured data container for a detected individual."""
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    center: Tuple[int, int] = (0, 0)
    width: int = 0
    height: int = 0
    pose: Optional[PoseResult] = None

    def __post_init__(self):
        x1, y1, x2, y2 = self.bbox
        self.width = max(0, x2 - x1)
        self.height = max(0, y2 - y1)
        self.center = (int(x1 + self.width / 2), int(y1 + self.height / 2))


class UnifiedPersonPoseDetector:
    """
    Unified YOLOv8-Pose engine delivering ultra-fast single-pass detection + pose estimation on CPU
    with tactical sci-fi HUD rendering.
    """

    KEYPOINT_NAMES = [
        "nose",            # 0
        "left_eye",        # 1
        "right_eye",       # 2
        "left_ear",        # 3
        "right_ear",       # 4
        "left_shoulder",   # 5
        "right_shoulder",  # 6
        "left_elbow",      # 7
        "right_elbow",     # 8
        "left_wrist",      # 9
        "right_wrist",     # 10
        "left_hip",        # 11
        "right_hip",       # 12
        "left_knee",       # 13
        "right_knee",      # 14
        "left_ankle",      # 15
        "right_ankle",     # 16
    ]

    CONNECTIONS = [
        ("left_shoulder", "right_shoulder", (0, 240, 255)),   # Cyan
        ("left_shoulder", "left_elbow", (0, 220, 255)),
        ("left_elbow", "left_wrist", (0, 180, 255)),
        ("right_shoulder", "right_elbow", (0, 220, 255)),
        ("right_elbow", "right_wrist", (0, 180, 255)),
        ("left_shoulder", "left_hip", (255, 180, 50)),       # Sky Blue
        ("right_shoulder", "right_hip", (255, 180, 50)),
        ("left_hip", "right_hip", (255, 180, 50)),
        ("left_hip", "left_knee", (0, 255, 140)),            # Neon Emerald
        ("left_knee", "left_ankle", (0, 255, 140)),
        ("right_hip", "right_knee", (0, 255, 140)),
        ("right_knee", "right_ankle", (0, 255, 140)),
    ]

    def __init__(
        self,
        model_path: str = "models/person_detection/yolov8n-pose.pt",
        confidence_threshold: float = 0.35,
        device: str = "cpu",
    ):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = device

        if not os.path.exists(self.model_path):
            self.model = YOLO("yolov8n-pose.pt")
            try:
                self.model.save(self.model_path)
            except Exception:
                pass
        else:
            self.model = YOLO(self.model_path)

        print(f"[UnifiedPersonPoseDetector] Single-pass YOLOv8-Pose engine loaded on {self.device}")

    def detect_and_estimate(
        self,
        frame: np.ndarray,
        inference_size: int = 480,
    ) -> List[PersonDetection]:
        """
        Runs single-pass inference returning list of PersonDetection containing both bounding boxes and full pose data.
        """
        if frame is None or frame.size == 0:
            return []

        h, w, _ = frame.shape

        # Fast inference with optimized image size for CPU
        results = self.model.predict(
            source=frame,
            conf=self.confidence_threshold,
            imgsz=inference_size,
            device=self.device,
            verbose=False,
        )

        detections: List[PersonDetection] = []
        if not results or len(results) == 0:
            return detections

        result = results[0]
        if result.boxes is None or len(result.boxes) == 0:
            return detections

        boxes_data = result.boxes.data.cpu().numpy()  # [x1, y1, x2, y2, conf, cls]
        has_kps = result.keypoints is not None and len(result.keypoints) > 0
        kp_xy_all = result.keypoints.xy.cpu().numpy() if has_kps else []
        kp_conf_all = result.keypoints.conf.cpu().numpy() if (has_kps and result.keypoints.conf is not None) else None

        for idx, row in enumerate(boxes_data):
            x1, y1, x2, y2, conf = row[:5]
            if conf < self.confidence_threshold:
                continue

            bbox = (int(max(0, x1)), int(max(0, y1)), int(min(w, x2)), int(min(h, y2)))
            
            # Extract keypoints for this person
            pose_res = None
            if has_kps and idx < len(kp_xy_all):
                person_xy = kp_xy_all[idx]
                person_conf = kp_conf_all[idx] if kp_conf_all is not None and idx < len(kp_conf_all) else np.ones(17)
                pose_res = self._build_pose_result(person_xy, person_conf, w, h, bbox)

            det = PersonDetection(
                bbox=bbox,
                confidence=float(conf),
                pose=pose_res,
            )
            detections.append(det)

        return detections

    def _build_pose_result(
        self,
        person_xy: np.ndarray,
        person_conf: np.ndarray,
        w: int,
        h: int,
        bbox: Tuple[int, int, int, int],
    ) -> PoseResult:
        """Constructs a PoseResult with joint angles and posture heuristics."""
        landmarks_dict: Dict[str, PoseLandmark] = {}
        for k_idx, name in enumerate(self.KEYPOINT_NAMES):
            px, py = person_xy[k_idx]
            conf = float(person_conf[k_idx]) if k_idx < len(person_conf) else 0.0
            norm_x = float(px / w) if w > 0 else 0.0
            norm_y = float(py / h) if h > 0 else 0.0

            landmarks_dict[name] = PoseLandmark(
                x=norm_x,
                y=norm_y,
                visibility=conf,
                pixel_x=int(px),
                pixel_y=int(py),
            )

        spine_angle = self._compute_spine_angle(landmarks_dict)
        
        # Check lower body keypoints presence
        lk = landmarks_dict.get("left_knee")
        rk = landmarks_dict.get("right_knee")
        la = landmarks_dict.get("left_ankle")
        ra = landmarks_dict.get("right_ankle")
        l_hip = landmarks_dict.get("left_hip")
        r_hip = landmarks_dict.get("right_hip")

        has_knee = (lk and lk.visibility > 0.35) or (rk and rk.visibility > 0.35)
        has_hip = (l_hip and l_hip.visibility > 0.35) or (r_hip and r_hip.visibility > 0.35)
        lower_visible = has_knee and ((la and la.visibility > 0.3) or (ra and ra.visibility > 0.3))

        l_knee_angle = self._compute_angle(l_hip, lk, la) if (l_hip and lk and la) else 180.0
        r_knee_angle = self._compute_angle(r_hip, rk, ra) if (r_hip and rk and ra) else 180.0
        l_hip_angle = self._compute_angle(landmarks_dict.get("left_shoulder"), l_hip, lk) if (l_hip and lk) else 180.0
        r_hip_angle = self._compute_angle(landmarks_dict.get("right_shoulder"), r_hip, rk) if (r_hip and rk) else 180.0
        
        # Elbow angles
        l_elbow_angle = self._compute_angle(landmarks_dict.get("left_shoulder"), landmarks_dict.get("left_elbow"), landmarks_dict.get("left_wrist"))
        r_elbow_angle = self._compute_angle(landmarks_dict.get("right_shoulder"), landmarks_dict.get("right_elbow"), landmarks_dict.get("right_wrist"))

        # Aspect ratio of bounding box
        bx1, by1, bx2, by2 = bbox
        bw = max(1, bx2 - bx1)
        bh = max(1, by2 - by1)
        aspect_ratio = float(bh / bw)

        # Torso length
        l_sh = landmarks_dict.get("left_shoulder")
        r_sh = landmarks_dict.get("right_shoulder")
        torso_len = 0.0
        if (l_sh or r_sh) and (l_hip or r_hip):
            sh_y = (l_sh.pixel_y if l_sh and l_sh.visibility > 0.3 else (r_sh.pixel_y if r_sh else 0))
            hp_y = (l_hip.pixel_y if l_hip and l_hip.visibility > 0.3 else (r_hip.pixel_y if r_hip else 0))
            torso_len = abs(hp_y - sh_y)

        return PoseResult(
            landmarks=landmarks_dict,
            spine_angle=round(spine_angle, 1),
            left_knee_angle=round(l_knee_angle, 1),
            right_knee_angle=round(r_knee_angle, 1),
            left_hip_angle=round(l_hip_angle, 1),
            right_hip_angle=round(r_hip_angle, 1),
            left_elbow_angle=round(l_elbow_angle, 1),
            right_elbow_angle=round(r_elbow_angle, 1),
            body_aspect_ratio=round(aspect_ratio, 2),
            lower_body_visible=lower_visible,
            has_knee_data=has_knee,
            has_hip_data=has_hip,
            torso_length_px=torso_len,
            is_valid=True,
        )

    def _compute_angle(
        self,
        a: Optional[PoseLandmark],
        b: Optional[PoseLandmark],
        c: Optional[PoseLandmark],
    ) -> float:
        if not a or not b or not c or a.visibility < 0.25 or b.visibility < 0.25 or c.visibility < 0.25:
            return 180.0
        p1 = np.array([a.pixel_x, a.pixel_y], dtype=np.float32)
        p2 = np.array([b.pixel_x, b.pixel_y], dtype=np.float32)
        p3 = np.array([c.pixel_x, c.pixel_y], dtype=np.float32)
        v1 = p1 - p2
        v2 = p3 - p2
        norm = np.linalg.norm(v1) * np.linalg.norm(v2)
        if norm == 0:
            return 180.0
        cosine_angle = np.clip(np.dot(v1, v2) / norm, -1.0, 1.0)
        return float(np.degrees(np.arccos(cosine_angle)))

    def _compute_spine_angle(self, lms: Dict[str, PoseLandmark]) -> float:
        l_sh = lms.get("left_shoulder")
        r_sh = lms.get("right_shoulder")
        l_hip = lms.get("left_hip")
        r_hip = lms.get("right_hip")

        if not ((l_sh or r_sh) and (l_hip or r_hip)):
            return 0.0

        sh_x = (l_sh.pixel_x + r_sh.pixel_x)/2.0 if (l_sh and r_sh) else (l_sh.pixel_x if l_sh else r_sh.pixel_x)
        sh_y = (l_sh.pixel_y + r_sh.pixel_y)/2.0 if (l_sh and r_sh) else (l_sh.pixel_y if l_sh else r_sh.pixel_y)
        hp_x = (l_hip.pixel_x + r_hip.pixel_x)/2.0 if (l_hip and r_hip) else (l_hip.pixel_x if l_hip else r_hip.pixel_x)
        hp_y = (l_hip.pixel_y + r_hip.pixel_y)/2.0 if (l_hip and r_hip) else (l_hip.pixel_y if l_hip else r_hip.pixel_y)

        dx = sh_x - hp_x
        dy = hp_y - sh_y
        return float(np.degrees(np.arctan2(abs(dx), max(0.001, abs(dy)))))

    def draw_skeleton(
        self,
        frame: np.ndarray,
        pose_res: PoseResult,
    ) -> np.ndarray:
        """Draws clean, professional anatomical skeleton lines and joint markers."""
        if not pose_res or not pose_res.is_valid:
            return frame

        # Draw limb connections with clean anti-aliased lines
        for conn in self.CONNECTIONS:
            start_name, end_name, color = conn
            p1 = pose_res.landmarks.get(start_name)
            p2 = pose_res.landmarks.get(end_name)
            if p1 and p2 and p1.visibility > 0.3 and p2.visibility > 0.3 and p1.pixel_x > 0 and p2.pixel_x > 0:
                cv2.line(frame, (p1.pixel_x, p1.pixel_y), (p2.pixel_x, p2.pixel_y), color, 2, cv2.LINE_AA)

        # Draw clean joint nodes
        for name, lm in pose_res.landmarks.items():
            if lm.visibility > 0.35 and lm.pixel_x > 0:
                cv2.circle(frame, (lm.pixel_x, lm.pixel_y), 3, (240, 240, 255), -1, cv2.LINE_AA)
                cv2.circle(frame, (lm.pixel_x, lm.pixel_y), 4, (56, 189, 248), 1, cv2.LINE_AA)

        return frame

    def detect(self, frame: np.ndarray) -> List[PersonDetection]:
        """Convenience method for person detection."""
        return self.detect_and_estimate(frame)

    def estimate(self, frame: np.ndarray) -> PoseResult:
        """Convenience method for pose estimation."""
        dets = self.detect_and_estimate(frame)
        if len(dets) > 0 and dets[0].pose is not None:
            return dets[0].pose
        return PoseResult(is_valid=False)

    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[PersonDetection],
        color: Tuple[int, int, int] = (248, 189, 56),
    ) -> np.ndarray:
        """
        Draws clean, professional bounding outlines and compact confidence badges.
        """
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)

            label = f"Person  {int(det.confidence*100)}%"
            (lbl_w, lbl_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
            badge_y1 = max(0, y1 - lbl_h - 8)
            badge_y2 = y1
            badge_x2 = x1 + lbl_w + 12

            cv2.rectangle(frame, (x1, badge_y1), (badge_x2, badge_y2), (15, 23, 42), -1)
            cv2.rectangle(frame, (x1, badge_y1), (badge_x2, badge_y2), color, 1)
            cv2.putText(frame, label, (x1 + 6, badge_y2 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (248, 250, 252), 1, cv2.LINE_AA)

        return frame


# Backward-compatibility aliases
PersonDetector = UnifiedPersonPoseDetector
PoseEstimator = UnifiedPersonPoseDetector
