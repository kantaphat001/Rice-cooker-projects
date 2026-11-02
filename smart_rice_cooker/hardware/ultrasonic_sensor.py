"""
ultrasonic_sensor.py - High-Precision HC-SR04 Distance Driver (Hardened 2026 Edition)
- Direct C-level timing via lgpio on Raspberry Pi 4 / 5 (Debian Bookworm/Trixie)
- Clean fallback to gpiozero / mock mode on Windows development machines
- Strictly rejects false 0cm echoes, electrical glitches, and out-of-range spikes
- Publishes real-time telemetry to /dev/shm/ultrasonic_distance.json for Web Portal
"""

import time
import json
import logging
import threading
import statistics
from collections import deque
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Check for native Linux lgpio
try:
    import lgpio
    LGPIO_AVAILABLE = True
except (ImportError, Exception):
    LGPIO_AVAILABLE = False

# Fallback gpiozero
try:
    from gpiozero import DistanceSensor
    GPIOZERO_AVAILABLE = True
except (ImportError, Exception):
    GPIOZERO_AVAILABLE = False


class UltrasonicSensor:
    def __init__(self,
                 trig_pin: Optional[int] = 20,
                 echo_pin: Optional[int] = 21,
                 out_pin: int = 21,
                 model: str = "HC-SR04",
                 threshold_cm: float = 45.0,
                 hold_time_sec: float = 0.8,
                 sniffer_interval_sec: float = 1.0,
                 burst_samples: int = 3,
                 on_person_detected=None):
        self.model = model.upper()
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.out_pin = out_pin
        self.threshold_cm = threshold_cm
        self.hold_time_sec = hold_time_sec
        self.sniffer_interval_sec = sniffer_interval_sec
        self.burst_samples = burst_samples
        self.on_person_detected = on_person_detected

        self._readings = deque(maxlen=5)
        self._running = False
        self._thread = None
        self._presence_start = None
        self.eco_mode = False
        self.is_hardware_fault = False
        self._fail_count = 0

        # Hardware handles
        self._lgpio_handle = None
        self._gz_sensor = None
        self._is_mock = True

        self._init_hardware()

    def _init_hardware(self):
        # 1. Preferred Native Driver: lgpio (Zero overhead, no background thread PWM conflict)
        if LGPIO_AVAILABLE and self.trig_pin is not None and self.echo_pin is not None:
            try:
                self._lgpio_handle = lgpio.gpiochip_open(0)
                lgpio.gpio_claim_output(self._lgpio_handle, self.trig_pin, 0)
                lgpio.gpio_claim_input(self._lgpio_handle, self.echo_pin, lgpio.SET_PULL_DOWN)
                self._is_mock = False
                logger.info(f"[Ultrasonic] Native lgpio driver active (Trig=GPIO {self.trig_pin}, Echo=GPIO {self.echo_pin})")
                return
            except Exception as e:
                logger.warning(f"[Ultrasonic] lgpio init failed: {e}. Trying gpiozero fallback.")
                if self._lgpio_handle is not None:
                    try:
                        lgpio.gpiochip_close(self._lgpio_handle)
                    except Exception:
                        pass
                    self._lgpio_handle = None

        # 2. Secondary Driver: gpiozero DistanceSensor
        if GPIOZERO_AVAILABLE and self.trig_pin is not None and self.echo_pin is not None:
            try:
                self._gz_sensor = DistanceSensor(echo=self.echo_pin, trigger=self.trig_pin, max_distance=1.5, partial=True)
                self._is_mock = False
                logger.info(f"[Ultrasonic] gpiozero DistanceSensor active (Trig=GPIO {self.trig_pin}, Echo=GPIO {self.echo_pin})")
                return
            except Exception as e:
                logger.warning(f"[Ultrasonic] gpiozero init failed: {e}. Running in MOCK mode.")

        self._is_mock = True
        logger.info("[Ultrasonic] Running in MOCK mode (simulated distance).")

    def set_eco_mode(self, enabled: bool):
        self.eco_mode = enabled
        mode_str = "ECO SNIFFER (1.0s interval)" if enabled else "ACTIVE REAL-TIME (10Hz)"
        logger.info(f"[Ultrasonic] Mode changed -> {mode_str}")

    def _read_lgpio(self) -> Optional[float]:
        if self._lgpio_handle is None:
            return None
        try:
            h = self._lgpio_handle

            # If echo pin is already high, wait up to 5ms for it to drop low
            if lgpio.gpio_read(h, self.echo_pin) == 1:
                t_wait = time.perf_counter() + 0.005
                while lgpio.gpio_read(h, self.echo_pin) == 1:
                    if time.perf_counter() > t_wait:
                        return None

            # Trigger pulse (12-15 us)
            lgpio.gpio_write(h, self.trig_pin, 1)
            time.sleep(0.000015)
            lgpio.gpio_write(h, self.trig_pin, 0)

            # Wait for ECHO to rise (start of return pulse, max 15ms)
            t_start = time.perf_counter()
            t_timeout = t_start + 0.015
            while lgpio.gpio_read(h, self.echo_pin) == 0:
                t_start = time.perf_counter()
                if t_start > t_timeout:
                    return None

            # Wait for ECHO to fall (end of pulse, max 25ms ~4.3m)
            t_end = t_start
            t_max = t_start + 0.025
            while lgpio.gpio_read(h, self.echo_pin) == 1:
                t_end = time.perf_counter()
                if t_end > t_max:
                    return None

            duration = t_end - t_start
            dist_cm = (duration * 34300.0) / 2.0
            return dist_cm
        except Exception:
            return None

    def get_distance_cm(self) -> float:
        """Returns median distance in centimeters. Never returns 0cm on false triggers."""
        if self._is_mock:
            return 150.0

        # 1. Read via native lgpio
        if self._lgpio_handle is not None:
            d = self._read_lgpio()
            if d is not None and 4.0 <= d <= 150.0:
                self._readings.append(d)
                self._fail_count = 0
                self.is_hardware_fault = False
                return statistics.median(self._readings)
            return 150.0

        # 2. Read via gpiozero fallback
        if self._gz_sensor is not None:
            try:
                dist_cm = self._gz_sensor.distance * 100.0
                if 4.0 <= dist_cm <= 150.0:
                    self._readings.append(dist_cm)
                    self._fail_count = 0
                    self.is_hardware_fault = False
                    return statistics.median(self._readings)
                return 150.0
            except Exception:
                self._fail_count += 1
                if self._fail_count >= 5:
                    self.is_hardware_fault = True
                return 150.0

        return 150.0

    def is_person_present(self) -> bool:
        """Returns True only when confirmed distance is strictly within threshold."""
        dist = self.get_distance_cm()
        return 4.0 <= dist < self.threshold_cm

    def set_threshold_cm(self, cm: float):
        """Dynamically updates distance trigger threshold in cm."""
        val = max(15.0, min(150.0, float(cm)))
        self.threshold_cm = val
        logger.info(f"[Ultrasonic] 📏 Distance threshold updated to {val:.1f} cm")

    def _check_shm_config(self):
        """Checks if web manager sent a dynamic threshold update."""
        try:
            cfg_path = Path("/dev/shm/ultrasonic_config.json")
            if cfg_path.is_file():
                data = json.loads(cfg_path.read_text(encoding="utf-8"))
                try:
                    cfg_path.unlink(missing_ok=True)
                except Exception:
                    pass
                if "distance_trigger_cm" in data:
                    self.set_threshold_cm(data["distance_trigger_cm"])
        except Exception:
            pass

    def _publish_shm_state(self, dist: float, is_present: bool):
        """Publishes live distance and threshold to RAM disk for Web Manager."""
        try:
            shm_path = Path("/dev/shm/ultrasonic_distance.json")
            payload = json.dumps({
                "distance_cm": round(dist, 1),
                "threshold_cm": round(self.threshold_cm, 1),
                "is_person_present": bool(is_present),
                "hardware_fault": bool(self.is_hardware_fault),
                "timestamp": time.time()
            })
            shm_path.write_text(payload, encoding="utf-8")
        except Exception:
            pass

    def start_monitoring(self):
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="UltrasonicMonitor")
        self._thread.start()
        logger.info(f"[Ultrasonic] Background distance monitor started ({self.model}).")

    def stop_monitoring(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self._lgpio_handle is not None:
            try:
                lgpio.gpio_free(self._lgpio_handle, self.trig_pin)
                lgpio.gpio_free(self._lgpio_handle, self.echo_pin)
                lgpio.gpiochip_close(self._lgpio_handle)
            except Exception:
                pass
            self._lgpio_handle = None
        if self._gz_sensor is not None:
            try:
                self._gz_sensor.close()
            except Exception:
                pass
            self._gz_sensor = None

    def _monitor_loop(self):
        while self._running:
            self._check_shm_config()
            dist = self.get_distance_cm()
            # Valid person presence requires distance strictly between 4.0cm and threshold_cm
            is_present = (4.0 <= dist < self.threshold_cm)
            self._publish_shm_state(dist, is_present)

            interval = self.sniffer_interval_sec if self.eco_mode else 0.1

            if is_present:
                if self._presence_start is None:
                    self._presence_start = time.time()
                elif (time.time() - self._presence_start) >= self.hold_time_sec:
                    logger.info(f"[Ultrasonic] Sustained presence detected (~{dist:.1f} cm, held {self.hold_time_sec}s)")
                    if self.on_person_detected:
                        try:
                            self.on_person_detected(dist)
                        except Exception as e:
                            logger.error(f"[Ultrasonic] Callback error: {e}")
                    self._presence_start = None
                    # Hold-off cooldown so the system doesn't re-trigger while announcement or detection is in progress
                    time.sleep(2.0)
            else:
                self._presence_start = None

            time.sleep(interval)
