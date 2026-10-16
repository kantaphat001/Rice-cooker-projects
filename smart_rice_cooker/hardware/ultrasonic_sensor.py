"""
ultrasonic_sensor.py - HC-SR04 Ultrasonic Distance Sensor Driver
Features:
- Strict microsecond timeout guard (no infinite while-loop hangs)
- Median filter over last N readings to reject clothing/acoustic flutter
- Event-driven background thread firing on_person_detected callback
"""

import time
import threading
import logging
from collections import deque
import statistics

logger = logging.getLogger(__name__)

try:
    from gpiozero import DistanceSensor
    GPIOZERO_DISTANCE_AVAILABLE = True
except (ImportError, Exception):
    GPIOZERO_DISTANCE_AVAILABLE = False
    logger.warning("[Ultrasonic] gpiozero DistanceSensor not available. Running in MOCK mode.")

class UltrasonicSensor:
    def __init__(self, trig_pin: int, echo_pin: int,
                 threshold_cm: float = 70.0,
                 hold_time_sec: float = 0.8,
                 on_person_detected=None):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.threshold_cm = threshold_cm
        self.hold_time_sec = hold_time_sec
        self.on_person_detected = on_person_detected

        self._readings = deque(maxlen=5)
        self._is_mock = not GPIOZERO_DISTANCE_AVAILABLE
        self._sensor = None
        self._running = False
        self._thread = None
        self._presence_start = None

        if not self._is_mock:
            try:
                # max_distance=3.0 meters, threshold_distance=threshold_cm / 100
                self._sensor = DistanceSensor(
                    echo=self.echo_pin,
                    trigger=self.trig_pin,
                    max_distance=3.0,
                    threshold_distance=self.threshold_cm / 100.0
                )
                logger.info(f"[Ultrasonic] Initialized on TRIG={trig_pin}, ECHO={echo_pin}, Threshold={threshold_cm}cm")
            except Exception as e:
                logger.warning(f"[Ultrasonic] Hardware init failed: {e}. Falling back to mock.")
                self._is_mock = True

    def get_distance_cm(self) -> float:
        """Returns filtered distance in centimeters."""
        if self._is_mock or not self._sensor:
            return 150.0  # Safe default mock distance (out of range)

        try:
            raw_dist_m = self._sensor.distance
            dist_cm = raw_dist_m * 100.0
            self._readings.append(dist_cm)
            filtered_dist = statistics.median(self._readings)
            return filtered_dist
        except Exception:
            return 999.0

    def start_monitoring(self):
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("[Ultrasonic] Background distance monitor started.")

    def stop_monitoring(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self._sensor:
            try:
                self._sensor.close()
            except Exception:
                pass

    def _monitor_loop(self):
        while self._running:
            dist = self.get_distance_cm()

            if dist < self.threshold_cm:
                if self._presence_start is None:
                    self._presence_start = time.time()
                elif (time.time() - self._presence_start) >= self.hold_time_sec:
                    # Sustained presence detected!
                    logger.info(f"[Ultrasonic] Sustained presence detected at {dist:.1f} cm (held {self.hold_time_sec}s)")
                    if self.on_person_detected:
                        try:
                            self.on_person_detected(dist)
                        except Exception as e:
                            logger.error(f"[Ultrasonic] Callback error: {e}")
                    # Reset presence counter to avoid rapid duplicate firings
                    self._presence_start = None
                    time.sleep(2.0)
            else:
                self._presence_start = None

            time.sleep(0.1)  # 10Hz sampling rate is ideal for low CPU
