"""
VisionDNA - Visual Data Acquisition Module
Handles video streams from webcam or video files with full seeking,
duration telemetry, smoothed FPS calculation, and explicit synthetic test mode.
"""

import cv2
import time
import os
import datetime
from typing import Optional, Tuple, Union
import numpy as np


class VideoStream:
    """
    Robust video capture class supporting webcams (with Windows DirectShow fallback),
    real video files with frame seeking, and explicit synthetic frame generation.
    """

    def __init__(
        self,
        source: Union[int, str] = 0,
        width: int = 640,
        height: int = 480,
        fps_limit: int = 30,
        use_directshow: bool = True,
    ):
        self.source = source
        self.target_width = width
        self.target_height = height
        self.fps_limit = fps_limit
        self.use_directshow = use_directshow

        self.cap: Optional[cv2.VideoCapture] = None
        self.is_opened = False
        self.is_synthetic_mode = (source == -1 or source == "-1")
        self.is_video_file = isinstance(source, str) and os.path.isfile(source)

        # Video File Metadata
        self.total_frames = 0
        self.video_fps = 30.0
        self.duration_seconds = 0.0

        # FPS & Timing Tracking
        self.prev_time = time.time()
        self.fps = 0.0
        self.frame_count = 0
        self.current_frame_idx = 0
        self.start_time = time.time()
        self.actual_width = width
        self.actual_height = height

        self._initialize_capture()

    def _initialize_capture(self) -> bool:
        """Initializes the OpenCV VideoCapture backend."""
        # 1. Explicit Synthetic Demo Mode
        if self.is_synthetic_mode:
            self.is_opened = True
            self.actual_width = self.target_width
            self.actual_height = self.target_height
            print("[VideoStream] Initialized in SYNTHETIC SIMULATION MODE.")
            return True

        # 2. Real Video File Source
        if isinstance(self.source, str):
            if not os.path.exists(self.source):
                print(f"[VideoStream] Error: Video file '{self.source}' not found.")
                self.is_opened = False
                return False
            self.cap = cv2.VideoCapture(self.source)
            if self.cap.isOpened():
                self.is_opened = True
                self.actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps_val = self.cap.get(cv2.CAP_PROP_FPS)
                self.video_fps = fps_val if (fps_val and fps_val > 0) else 30.0
                self.duration_seconds = self.total_frames / self.video_fps if self.total_frames > 0 else 0.0
                print(f"[VideoStream] Loaded real video file: {self.source} ({self.actual_width}x{self.actual_height}, {self.total_frames} frames, {self.duration_seconds:.1f}s)")
                return True
            else:
                self.is_opened = False
                return False

        # 3. Real Hardware Webcam Source
        camera_idx = int(self.source)
        print(f"[VideoStream] Attempting to open real hardware webcam index {camera_idx}...")

        # Default backend
        self.cap = cv2.VideoCapture(camera_idx)

        # Fallback to DirectShow on Windows if initial open fails
        if not self.cap.isOpened() and self.use_directshow and os.name == "nt":
            print(f"[VideoStream] Retrying webcam index {camera_idx} with DirectShow backend...")
            self.cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)

        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
            self.actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.is_opened = True
            print(f"[VideoStream] Webcam initialized successfully ({self.actual_width}x{self.actual_height})")
            return True
        else:
            print(f"[VideoStream] Error: Unable to open hardware camera index {camera_idx}.")
            self.is_opened = False
            return False

    def seek_frame(self, frame_idx: int) -> bool:
        """Seeks to a specific frame number in video file mode."""
        if not self.is_video_file or self.cap is None:
            return False
        frame_idx = max(0, min(self.total_frames - 1, frame_idx))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        self.current_frame_idx = frame_idx
        return True

    def get_current_frame_idx(self) -> int:
        """Returns current frame index."""
        if self.is_video_file and self.cap is not None:
            return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        return self.frame_count

    def get_current_time_str(self) -> str:
        """Returns current playback timestamp as MM:SS."""
        if self.is_video_file:
            curr_sec = self.get_current_frame_idx() / max(1.0, self.video_fps)
            total_sec = self.duration_seconds
            curr_m, curr_s = int(curr_sec // 60), int(curr_sec % 60)
            tot_m, tot_s = int(total_sec // 60), int(total_sec % 60)
            return f"{curr_m:02d}:{curr_s:02d} / {tot_m:02d}:{tot_s:02d}"
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        return f"LIVE {now_str}"

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Reads a frame from the stream.
        Returns (success, frame).
        """
        # Explicit synthetic mode ONLY
        if self.is_synthetic_mode:
            frame = self._generate_synthetic_frame()
            self._update_fps()
            return True, frame

        # Real hardware webcam or real video file
        if not self.is_opened or self.cap is None:
            return False, None

        ret, frame = self.cap.read()

        # Loop video file if reached end
        if not ret and self.is_video_file:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        if ret and frame is not None:
            self.frame_count += 1
            self.current_frame_idx = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) if self.is_video_file else self.frame_count
            self._update_fps()
            return True, frame
        else:
            return False, None

    def _update_fps(self):
        """Calculates smoothed real-time frames per second."""
        curr_time = time.time()
        dt = curr_time - self.prev_time
        if dt > 0:
            instant_fps = 1.0 / dt
            self.fps = 0.9 * self.fps + 0.1 * instant_fps if self.fps > 0 else instant_fps
        self.prev_time = curr_time

    def _generate_synthetic_frame(self) -> np.ndarray:
        """Generates a synthetic holographic test pattern strictly for Demo mode."""
        h, w = self.target_height, self.target_width
        frame = np.zeros((h, w, 3), dtype=np.uint8)

        # Deep space dark backdrop with subtle grid
        frame[:] = (12, 16, 24)
        grid_color = (24, 32, 48)
        for x in range(0, w, 40):
            cv2.line(frame, (x, 0), (x, h), grid_color, 1)
        for y in range(0, h, 40):
            cv2.line(frame, (0, y), (w, y), grid_color, 1)

        # Animated synthetic target entity
        t = time.time() - self.start_time
        target_x = int(w // 2 + (w * 0.30) * np.sin(t * 0.8))
        target_y = int(h // 2 + 40 + 20 * np.cos(t * 1.6))

        # Avatar silhouette
        cv2.circle(frame, (target_x, target_y - 65), 16, (0, 240, 255), 2)
        cv2.circle(frame, (target_x, target_y - 65), 4, (0, 240, 255), -1)
        cv2.line(frame, (target_x, target_y - 49), (target_x, target_y), (0, 240, 255), 2)
        cv2.line(frame, (target_x, target_y - 40), (target_x - 20, target_y - 15), (0, 200, 255), 2)
        cv2.line(frame, (target_x, target_y - 40), (target_x + 20, target_y - 15), (0, 200, 255), 2)
        cv2.line(frame, (target_x, target_y), (target_x - 15, target_y + 60), (0, 200, 255), 2)
        cv2.line(frame, (target_x, target_y), (target_x + 15, target_y + 60), (0, 200, 255), 2)

        # Header badge
        cv2.putText(
            frame,
            "Scenario Simulator - Controlled Test Environment",
            (25, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (148, 163, 184),
            1,
            cv2.LINE_AA,
        )
        return frame

    def draw_hud(self, frame: np.ndarray, title: str = "Live Perception", subtitle: Optional[str] = None) -> np.ndarray:
        """
        Draws top status banner overlay with video timestamp, resolution, and FPS.
        """
        h, w, _ = frame.shape
        overlay = frame.copy()

        bar_height = 36
        cv2.rectangle(overlay, (0, 0), (w, bar_height), (15, 23, 42), -1)
        cv2.line(overlay, (0, bar_height), (w, bar_height), (30, 41, 59), 1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

        # Status Indicator
        cv2.circle(frame, (16, 18), 4, (16, 185, 129), -1)

        # Title
        cv2.putText(
            frame,
            title,
            (28, 23),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (248, 250, 252),
            1,
            cv2.LINE_AA,
        )

        # Timecode & Stats Right Aligned
        time_text = f"{self.get_current_time_str()}  |  {self.fps:.1f} FPS"
        (tw, _), _ = cv2.getTextSize(time_text, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
        cv2.putText(
            frame,
            time_text,
            (w - tw - 12, 23),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            (148, 163, 184),
            1,
            cv2.LINE_AA,
        )

        return frame

    def release(self):
        """Releases the video capture device."""
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
            print("[VideoStream] Video capture released.")
