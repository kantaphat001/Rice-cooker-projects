"""
ultrasonic_sensor.py - Multi-Sensor Ultrasonic Distance Driver
Supports:
1. US-016: Analog Ultrasonic Module
   - Direct GPIO Proximity Mode (Reads OUT pin via Pi GPIO, VCC=3.3V, Range=GND)
   - I2C ADC Mode (ADS1115 / PCF8591 if installed)
2. HC-SR04 / US-015: Digital Pulse Timing (TRIG / ECHO) via gpiozero DistanceSensor
Includes 2026 Production Hardening:
- Low-power Sniffer Mode (1.2s pulse, 0 heat/wear)
- 2-Stage Verification Debounce (rejects rice cooker steam, ghosts, and transient electrical spikes)
- Strict Echo Timeout to prevent while-loop CPU hanging
"""

import time
import threading
import logging
from collections import deque
import statistics
from typing import Optional

logger = logging.getLogger(__name__)

# Check gpiozero availability
try:
    from gpiozero import DistanceSensor, DigitalInputDevice
    GPIOZERO_AVAILABLE = True
except (ImportError, Exception):
    GPIOZERO_AVAILABLE = False
    logger.warning("[Ultrasonic] gpiozero not available. Running in MOCK mode.")

# Check optional ADS1115 ADC availability
ADS1115_AVAILABLE = False
try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    ADS1115_AVAILABLE = True
except Exception:
    pass


class UltrasonicSensor:
    def __init__(self,
                 trig_pin: Optional[int] = 23,
                 echo_pin: Optional[int] = 24,
                 out_pin: int = 24,
                 model: str = "HC-SR04",
                 threshold_cm: float = 70.0,
                 hold_time_sec: float = 0.8,
                 sniffer_interval_sec: float = 1.2,
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
        self._is_mock = not GPIOZERO_AVAILABLE
        self._sensor = None
        self._digital_input = None
        self._adc_chan = None
        self._running = False
        self._thread = None
        self._presence_start = None
        self.eco_mode = False

        if not self._is_mock:
            self._init_hardware()

    def _init_hardware(self):
        # 1. Try US-016 Mode
        if "016" in self.model:
            if ADS1115_AVAILABLE:
                try:
                    i2c = busio.I2C(board.SCL, board.SDA)
                    ads = ADS.ADS1115(i2c)
                    self._adc_chan = AnalogIn(ads, ADS.P0)
                    logger.info("[Ultrasonic] US-016 Initialized via ADS1115 ADC (I2C) on Channel A0")
                    return
                except Exception as e:
                    logger.debug(f"[Ultrasonic] ADS1115 not detected: {e}. Falling back to Direct GPIO mode.")

            # US-016 Direct GPIO Proximity Mode
            try:
                self._digital_input = DigitalInputDevice(self.out_pin, pull_up=True)
                logger.info(f"[Ultrasonic] US-016 Direct GPIO Proximity Active on Pin GPIO {self.out_pin}")
                return
            except Exception as e:
                logger.error(f"[Ultrasonic] Failed to initialize DigitalInputDevice for US-016: {e}")

        # 2. HC-SR04 / Standard Pulse Mode via gpiozero DistanceSensor with strict timeout
        if self.echo_pin is not None and self.trig_pin is not None:
            try:
                # max_distance=2.0 caps measurement timeout at ~12ms, strictly preventing echo hangs
                self._sensor = DistanceSensor(echo=self.echo_pin, trigger=self.trig_pin, max_distance=2.0)
                logger.info(f"[Ultrasonic] HC-SR04 Active (Trig: GPIO {self.trig_pin}, Echo: GPIO {self.echo_pin})")
                return
            except Exception as e:
                logger.warning(f"[Ultrasonic] DistanceSensor init failed: {e}. Falling back to MOCK mode.")

        self._is_mock = True

    def set_eco_mode(self, enabled: bool):
        """Switches between Active Real-time Monitoring and Eco Sniffer mode."""
        self.eco_mode = enabled
        mode_str = "ECO SNIFFER (1.2s pulses, 0 heat)" if enabled else "ACTIVE REAL-TIME (10Hz)"
        logger.info(f"[Ultrasonic] Mode changed -> {mode_str}")

    def get_distance_cm(self) -> float:
        """Returns median distance in centimeters."""
        if self._is_mock:
            return 150.0

        # A. US-016 with ADC
        if self._adc_chan is not None:
            try:
                volts = self._adc_chan.voltage
                dist_cm = max(0.0, (volts / 3.3) * 100.0)
                self._readings.append(dist_cm)
                return statistics.median(self._readings)
            except Exception:
                return 150.0

        # B. US-016 Direct GPIO Proximity Mode
        if self._digital_input is not None:
            is_near = (self._digital_input.value == 0)
            return 35.0 if is_near else 150.0

        # C. HC-SR04 DistanceSensor with exception safety
        if self._sensor is not None:
            try:
                dist_cm = self._sensor.distance * 100.0
                if 2.0 <= dist_cm <= 250.0:
                    self._readings.append(dist_cm)
                    return statistics.median(self._readings)
                return 150.0
            except Exception:
                return 999.0

        return 150.0

    def is_person_present(self) -> bool:
        """Helper to quickly check presence regardless of sensor type."""
        dist = self.get_distance_cm()
        return dist < self.threshold_cm

    def _verify_presence_burst(self) -> bool:
        """
        2-Stage Verification: Fires 3 rapid checks spaced 40ms apart.
        Rejects steam clouds from the rice cooker, passing pets, or transient noise.
        """
        samples = []
        for _ in range(self.burst_samples):
            time.sleep(0.04)
            d = self.get_distance_cm()
            if d < 200.0:
                samples.append(d)

        if not samples:
            return False

        median_dist = statistics.median(samples)
        if median_dist < self.threshold_cm:
            logger.info(f"[Ultrasonic] 2-Stage Verification PASSED: {median_dist:.1f} cm (samples: {[round(s, 1) for s in samples]})")
            return True
        else:
            logger.debug(f"[Ultrasonic] 2-Stage Verification REJECTED: {median_dist:.1f} cm (Transient spike/steam ignored)")
            return False

    def start_monitoring(self):
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info(f"[Ultrasonic] Background distance monitor started ({self.model}).")

    def stop_monitoring(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self._sensor:
            try:
                self._sensor.close()
            except Exception:
                pass
        if self._digital_input:
            try:
                self._digital_input.close()
            except Exception:
                pass

    def _monitor_loop(self):
        while self._running:
            if self.eco_mode:
                # ECO SNIFFER MODE: Sleep 1.2s between pulses, zero wear and tear
                time.sleep(self.sniffer_interval_sec)
                if not self._running:
                    break

                if self.is_person_present():
                    # Initial ping triggered -> run 2-Stage Verification burst
                    if self._verify_presence_burst():
                        dist = self.get_distance_cm()
                        if self.on_person_detected:
                            try:
                                self.on_person_detected(dist)
                            except Exception as e:
                                logger.error(f"[Ultrasonic] Sniffer callback error: {e}")
                        time.sleep(2.0)
            else:
                # ACTIVE REAL-TIME MODE: 10 Hz polling with hold-time
                is_present = self.is_person_present()

                if is_present:
                    if self._presence_start is None:
                        self._presence_start = time.time()
                    elif (time.time() - self._presence_start) >= self.hold_time_sec:
                        dist = self.get_distance_cm()
                        logger.info(f"[Ultrasonic] Sustained presence detected (~{dist:.1f} cm, held {self.hold_time_sec}s)")
                        if self.on_person_detected:
                            try:
                                self.on_person_detected(dist)
                            except Exception as e:
                                logger.error(f"[Ultrasonic] Callback error: {e}")
                        self._presence_start = None
                        time.sleep(2.0)
                else:
                    self._presence_start = None

                time.sleep(0.1)
