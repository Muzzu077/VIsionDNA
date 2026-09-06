"""
Video ingestion service: open video from file / webcam / stream,
iterate frames, preprocess.
"""

import asyncio
import time
from pathlib import Path
from typing import AsyncIterator, Optional, Tuple

import cv2
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VideoSource:
    """Synchronous video capture wrapper around cv2.VideoCapture."""

    def __init__(
        self,
        source: str | int,
        target_fps: Optional[float] = None,
        resize: Optional[Tuple[int, int]] = None,
    ) -> None:
        """
        Parameters
        ----------
        source : str | int
            File path, RTSP/HTTP URL, or integer webcam index.
        target_fps : float, optional
            Limit output to this many frames per second.
            Defaults to settings.INFERENCE_FPS.
        resize : tuple[int, int], optional
            If provided, resize each frame to (width, height).
        """
        self.source = source
        self.target_fps = target_fps or settings.INFERENCE_FPS
        self.resize = resize
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        """Open the video source. Returns True on success."""
        if isinstance(self.source, int):
            self._cap = cv2.VideoCapture(self.source)
        else:
            self._cap = cv2.VideoCapture(str(self.source))
        opened = self._cap.isOpened()
        if opened:
            logger.info("video_source_opened", source=str(self.source))
        else:
            logger.error("video_source_failed", source=str(self.source))
        return opened

    def close(self) -> None:
        """Release the underlying capture."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            logger.info("video_source_closed", source=str(self.source))

    @property
    def native_fps(self) -> float:
        if self._cap is None:
            return 0.0
        return self._cap.get(cv2.CAP_PROP_FPS) or 30.0

    @property
    def frame_size(self) -> Tuple[int, int]:
        """Return (width, height) of the source."""
        if self._cap is None:
            return (0, 0)
        w = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (w, h)

    @property
    def total_frames(self) -> int:
        if self._cap is None:
            return 0
        return int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def read_frame(self) -> Optional[np.ndarray]:
        """Read a single frame. Returns None on failure / end of stream."""
        if self._cap is None or not self._cap.isOpened():
            return None
        ret, frame = self._cap.read()
        if not ret:
            return None
        if self.resize is not None:
            frame = cv2.resize(frame, self.resize, interpolation=cv2.INTER_LINEAR)
        return frame

    def __iter__(self):
        """Synchronous frame iterator respecting target_fps."""
        if self._cap is None:
            if not self.open():
                return

        interval = 1.0 / self.target_fps if self.target_fps > 0 else 0.0
        last_yield = 0.0

        while True:
            frame = self.read_frame()
            if frame is None:
                break

            now = time.monotonic()
            elapsed = now - last_yield
            if elapsed < interval:
                continue

            last_yield = now
            yield frame

        self.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


class AsyncVideoSource:
    """Async wrapper around VideoSource for use in async pipelines."""

    def __init__(
        self,
        source: str | int,
        target_fps: Optional[float] = None,
        resize: Optional[Tuple[int, int]] = None,
    ) -> None:
        self._sync = VideoSource(source, target_fps, resize)
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def open(self) -> bool:
        self._loop = asyncio.get_running_loop()
        return await self._loop.run_in_executor(None, self._sync.open)

    async def close(self) -> None:
        if self._loop is not None:
            await self._loop.run_in_executor(None, self._sync.close)

    async def read_frame(self) -> Optional[np.ndarray]:
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        return await self._loop.run_in_executor(None, self._sync.read_frame)

    async def __aiter__(self) -> AsyncIterator[np.ndarray]:
        """Async frame iterator."""
        opened = await self.open()
        if not opened:
            return

        interval = 1.0 / self._sync.target_fps if self._sync.target_fps > 0 else 0.0
        last_yield = 0.0

        try:
            while True:
                frame = await self.read_frame()
                if frame is None:
                    break

                now = time.monotonic()
                elapsed = now - last_yield
                if elapsed < interval:
                    sleep_time = interval - elapsed
                    await asyncio.sleep(sleep_time)

                last_yield = time.monotonic()
                yield frame
        finally:
            await self.close()

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return False


def preprocess_frame(
    frame: np.ndarray,
    target_size: Tuple[int, int] = (640, 640),
    normalize: bool = True,
) -> np.ndarray:
    """
    Preprocess a frame for model inference.

    - Resize to target_size (width, height)
    - Convert BGR -> RGB
    - Optionally normalize pixel values to [0, 1]
    """
    resized = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    if normalize:
        rgb = rgb.astype(np.float32) / 255.0
    return rgb
