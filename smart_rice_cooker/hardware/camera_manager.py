"""
camera_manager.py - Ultra-Stable Low-Memory Camera Streamer (2026 Edition)
Engineered for Raspberry Pi 4 (1GB RAM) with High Availability & Self-Healing:
- Backend: Native Linux V4L2 (CAP_V4L2) - zero GStreamer/FFMPEG wrapper overhead
- Zero-Latency Buffer: CAP_PROP_BUFFERSIZE = 1 (Hardware queue depth of 1)
- Hardware MJPG Decoding: Minimizes USB 2.0 bus load and CPU RAM copies
- Thread-Limiting: cv2.setNumThreads(1) to cap glibc memory arenas on ARM64
- Watchdog Auto-Recovery: Automatically re-initializes camera if frame drops > 5
- Dynamic FPS: 1 FPS in Standby, 15 FPS when person present
- Hardware Eco-Sleep / Suspend: Releases V4L2 device descriptor so CMOS sensor powers down completely
- Auto-Exposure Warm-Up: Discards 8 frames on cold-start to eliminate black/blown-out frames
"""

import threading
import time
import logging
import gc

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
    try:
        cv2.setNumThreads(1)
    except Exception:
        pass
except ImportError:
    cv2 = None
    np = None
    OPENCV_AVAILABLE = False
    logger.warning("[Camera] OpenCV/NumPy not available. Running in MOCK mode.")

class CameraManager:
    def __init__(self, camera_index: int = 0, standby_fps: float = 1.0, active_fps: float = 15.0, warmup_frames: int = 8):
        self.camera_index = camera_index
        self.standby_fps = standby_fps
        self.active_fps = active_fps
        self.warmup_frames = warmup_frames

        self._cap = None
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self._latest_frame = None
        self._is_active_mode = False
        self._is_suspended = False
        self._is_mock = False
        self._consecutive_failures = 0
        self._max_consecutive_failures = 5

    def _open_camera(self) -> bool:
        """Attempts to open V4L2 device with auto-probing across candidate indices."""
        if not OPENCV_AVAILABLE:
            self._is_mock = True
            return False

        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

        candidate_indices = [self.camera_index]
        for alt in (0, 1, 2, 4):
            if alt not in candidate_indices:
                candidate_indices.append(alt)

        for idx in candidate_indices:
            try:
                cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
                if not cap or not cap.isOpened():
                    cap = cv2.VideoCapture(idx)

                if cap and cap.isOpened():
                    # Validate real capture with a test frame
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None and test_frame.size > 0:
                        self._cap = cap
                        self.camera_index = idx
                        break
                    else:
                        cap.release()
            except Exception:
                pass

        if not self._cap or not self._cap.isOpened():
            logger.warning(f"[Camera] Cannot open any camera from {candidate_indices}. Fallback to mock.")
            self._is_mock = True
            return False

        try:
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
        logger.info("[Camera] Continuous capture loop started.")

    def suspend(self):
        """Safely powers down camera hardware during Eco-Sleep (prevents sensor heat)."""
        if self._is_suspended:
            return
        logger.info("[Camera] Suspending camera hardware for Eco-Sleep (releasing V4L2 device)...")
        with self._lock:
            self._is_suspended = True
            if self._cap:
                try:
                    self._cap.release()
                except Exception:
                    pass
                self._cap = None
            self._latest_frame = None
        gc.collect()
        logger.info("[Camera] Camera suspended. CMOS sensor powered down.")

    def resume(self):
        """Wakes up camera hardware and performs Auto-Exposure warm-up frames."""
        if not self._is_suspended and self._cap and self._cap.isOpened():
            return
        logger.info("[Camera] Resuming camera hardware from Eco-Sleep...")
        with self._lock:
            self._open_camera()
            if self._cap and self._cap.isOpened():
                # Auto-Exposure / AWB Warm-up: discard initial dark/blown-out frames
                logger.info(f"[Camera] Performing Auto-Exposure warm-up ({self.warmup_frames} frames)...")
                for _ in range(self.warmup_frames):
                    self._cap.read()
                    time.sleep(0.02)
                logger.info("[Camera] Auto-Exposure stabilized.")
            self._is_suspended = False

    def set_active_mode(self, active: bool):
        """Switches between 1 FPS (standby) and 15 FPS (active detection)."""
        self._is_active_mode = active
        fps = self.active_fps if active else self.standby_fps
        logger.debug(f"[Camera] Mode switched to {'ACTIVE' if active else 'STANDBY'} ({fps} FPS)")

    def get_latest_frame(self):
        """Returns the most recent BGR frame immediately."""
        with self._lock:
            if self._latest_frame is not None:
                return self._latest_frame.copy()

        if np is None or cv2 is None:
            return None

        dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        status = "Camera In Eco-Sleep" if self._is_suspended else "Camera Warming Up..."
        cv2.putText(dummy, status, (150, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        return dummy

    def _capture_loop(self):
        while self._running:
            if self._is_suspended:
                time.sleep(0.2)
                continue

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
                # Generate synthetic test frame if numpy/cv2 available
                if np is not None and cv2 is not None:
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
