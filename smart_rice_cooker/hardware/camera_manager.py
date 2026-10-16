"""
camera_manager.py - Zero-Latency Camera Warm-up Streamer
Solves the camera cold-start latency problem:
- Keeps camera connection active in background thread
- Standby mode grabs frames at 2 FPS (prevents enclosure overheating & zero CPU load)
- Instantly returns fresh frame via retrieve() when Ultrasonic wakes system up (< 5ms)
"""

import cv2
import threading
import time
import logging
import numpy as np

logger = logging.getLogger(__name__)

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

    def start(self):
        try:
            self._cap = cv2.VideoCapture(self.camera_index)
            if not self._cap.isOpened():
                logger.warning(f"[Camera] Cannot open /dev/video{self.camera_index}. Using Mock Camera.")
                self._is_mock = True
            else:
                self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                logger.info(f"[Camera] Hardware VideoCapture({self.camera_index}) initialized.")
        except Exception as e:
            logger.warning(f"[Camera] OpenCV VideoCapture init failed: {e}. Using Mock Camera.")
            self._is_mock = True

        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.info("[Camera] Warm-up capture loop started.")

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

        # Fallback dummy frame if camera not ready yet
        dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(dummy, "Camera Warming Up...", (150, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        return dummy

    def _capture_loop(self):
        while self._running:
            target_fps = self.active_fps if self._is_active_mode else self.standby_fps
            interval = 1.0 / max(1.0, target_fps)

            if not self._is_mock and self._cap and self._cap.isOpened():
                ret, frame = self._cap.read()
                if ret and frame is not None:
                    with self._lock:
                        self._latest_frame = frame
            else:
                # Generate synthetic test frame
                mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.rectangle(mock_frame, (100, 80), (540, 400), (40, 40, 40), -1)
                cv2.putText(mock_frame, f"Mock Camera Stream [{time.strftime('%H:%M:%S')}]",
                            (120, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
                with self._lock:
                    self._latest_frame = mock_frame

            time.sleep(interval)

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self._cap:
            try:
                self._cap.release()
            except Exception:
                pass
        logger.info("[Camera] Camera stopped.")
