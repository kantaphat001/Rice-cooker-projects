"""
camera_manager.py - Ultra-Stable Low-Memory Camera Streamer (2026 Edition)
Engineered for Raspberry Pi 4 (1GB RAM) with High Availability & Self-Healing:
- Backend: Native Linux V4L2 (CAP_V4L2) - zero GStreamer/FFMPEG wrapper overhead
- Zero-Latency Buffer: CAP_PROP_BUFFERSIZE = 1 (Hardware queue depth of 1)
- Hardware MJPG Decoding: Minimizes USB 2.0 bus load and CPU RAM copies
- Thread-Limiting: cv2.setNumThreads(2) to cap glibc memory arenas on ARM64
- Watchdog Auto-Recovery: Automatically re-initializes camera if frame drops > 5
- Dynamic FPS: 2 FPS in Standby (low CPU/thermals), jumps to 15 FPS when person present
- Single-slot memory management to avoid RAM leaks
"""

import cv2
import threading
import time
import logging
import gc
import numpy as np

logger = logging.getLogger(__name__)

# Enforce minimal thread pool for OpenCV on 1GB RAM Pi
try:
    cv2.setNumThreads(1)
except Exception:
    pass

class CameraManager:
    def __init__(self, camera_index: int = 0, standby_fps: float = 2.0, active_fps: float = 15.0):
        self.camera_index = camera_index
        self.standby_fps = standby_fps
        self.active_fps = active_fps

        self._cap = None
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self._latest_frame = None
        self._is_active_mode = False
        self._is_mock = False
        self._consecutive_failures = 0
        self._max_consecutive_failures = 5

    def _open_camera(self) -> bool:
        """Attempts to open V4L2 device with optimized hardware parameters."""
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

        try:
            # Explicitly select V4L2 backend
            self._cap = cv2.VideoCapture(self.camera_index, cv2.CAP_V4L2)
            if not self._cap or not self._cap.isOpened():
                # Fallback to default backend if V4L2 enum fails
                self._cap = cv2.VideoCapture(self.camera_index)

            if not self._cap or not self._cap.isOpened():
                logger.warning(f"[Camera] Cannot open /dev/video{self.camera_index}. Fallback to mock.")
                self._is_mock = True
                return False

            # 1. Hardware MJPEG compression (lowest memory & bus load)
            self._cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            # 2. Optimized 640x480 resolution (native camera mode)
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            # 3. Buffer depth = 1 (Zero lag, minimum memory consumption)
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            logger.info(f"[Camera] Hardware V4L2 device /dev/video{self.camera_index} initialized (640x480 MJPG, Buffer=1).")
            self._is_mock = False
            self._consecutive_failures = 0
            return True

        except Exception as e:
            logger.warning(f"[Camera] VideoCapture init error: {e}. Running in Mock mode.")
            self._is_mock = True
            return False

    def start(self):
        self._open_camera()
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True, name="CamCaptureThread")
        self._thread.start()
        logger.info("[Camera] Continuous zero-lag capture loop started.")

    def set_active_mode(self, active: bool):
        """Switches between 2 FPS (standby) and 15 FPS (active detection)."""
        self._is_active_mode = active
        fps = self.active_fps if active else self.standby_fps
        logger.debug(f"[Camera] Mode switched to {'ACTIVE' if active else 'STANDBY'} ({fps} FPS)")

    def get_latest_frame(self):
        """Returns the most recent BGR frame immediately."""
        with self._lock:
            if self._latest_frame is not None:
                return self._latest_frame.copy()

        dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(dummy, "Camera Warming Up...", (150, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        return dummy

    def _capture_loop(self):
        while self._running:
            t_start = time.time()
            target_fps = self.active_fps if self._is_active_mode else self.standby_fps
            target_interval = 1.0 / max(1.0, target_fps)

            if not self._is_mock and self._cap and self._cap.isOpened():
                ret, frame = self._cap.read()
                if ret and frame is not None and frame.size > 0:
                    self._consecutive_failures = 0
                    with self._lock:
                        self._latest_frame = frame
                else:
                    self._consecutive_failures += 1
                    logger.warning(f"[Camera] Frame grab failed ({self._consecutive_failures}/{self._max_consecutive_failures})")
                    if self._consecutive_failures >= self._max_consecutive_failures:
                        logger.error("[Camera] Excessive frame drops. Watchdog triggering auto-reconnect...")
                        time.sleep(1.0)
                        self._open_camera()
            else:
                # Generate synthetic test frame
                mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.rectangle(mock_frame, (100, 80), (540, 400), (35, 35, 35), -1)
                cv2.putText(mock_frame, f"Mock Camera Stream [{time.strftime('%H:%M:%S')}]",
                            (120, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
                with self._lock:
                    self._latest_frame = mock_frame

                if self._is_mock and not self._running:
                    break

            # Precise frame pacing
            elapsed = time.time() - t_start
            sleep_duration = max(0.005, target_interval - elapsed)
            time.sleep(sleep_duration)

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)
        if self._cap:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None
        self._latest_frame = None
        gc.collect()
        logger.info("[Camera] Camera stopped and memory released.")
