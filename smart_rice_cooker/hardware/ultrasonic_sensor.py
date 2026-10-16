"""
ultrasonic_sensor.py - Multi-Sensor Ultrasonic Distance Driver
Supports:
1. US-016: Analog Ultrasonic Module
   - Direct GPIO Proximity Mode (Reads OUT pin via Pi GPIO, VCC=3.3V, Range=GND)
   - I2C ADC Mode (ADS1115 / PCF8591 if installed)
2. HC-SR04 / US-015: Digital Pulse Timing (TRIG / ECHO) via gpiozero DistanceSensor
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
                 model: str = "US-016",
                 threshold_cm: float = 70.0,
                 hold_time_sec: float = 0.8,
                 on_person_detected=None):
        self.model = model.upper()
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.out_pin = out_pin
        self.threshold_cm = threshold_cm
        self.hold_time_sec = hold_time_sec
        self.on_person_detected = on_person_detected

        self._readings = deque(maxlen=5)
        self._is_mock = not GPIOZERO_AVAILABLE
        self._sensor = None
        self._digital_input = None
        self._adc_chan = None
        self._running = False
        self._thread = None
        self._presence_start = None

        if not self._is_mock:
            self._init_hardware()

    def _init_hardware(self):
        # 1. Try US-016 Mode
        if "016" in self.model:
            # Check if ADS1115 is attached for analog voltage reading
            if ADS1115_AVAILABLE:
                try:
                    i2c = busio.I2C(board.SCL, board.SDA)
                    ads = ADS.ADS1115(i2c)
                    self._adc_chan = AnalogIn(ads, ADS.P0)
                    logger.info("[Ultrasonic] US-016 Initialized via ADS1115 ADC (I2C) on Channel A0")
                    return
                except Exception as e:
                    logger.debug(f"[Ultrasonic] ADS1115 not detected: {e}. Falling back to Direct GPIO mode.")

            # Direct GPIO Proximity Mode:
            # US-016 Range=GND (1m max), VCC=3.3V
            # Distance < 40-50cm produces Vout < 1.3V (Logic LOW)
            # Distance > 60cm produces Vout > 1.8V (Logic HIGH)
            try:
                self._digital_input = DigitalInputDevice(self.out_pin, pull_up=False)
                logger.info(f"[Ultrasonic] US-016 Initialized in Direct GPIO Proximity Mode on Pin {self.out_pin}")
            except Exception as e:
                logger.warning(f"[Ultrasonic] Failed to init GPIO {self.out_pin} for US-016: {e}. Falling back to mock.")
                self._is_mock = True

        # 2. HC-SR04 / US-015 Mode (Digital TRIG/ECHO)
        else:
            try:
                self._sensor = DistanceSensor(
                    echo=self.echo_pin,
                    trigger=self.trig_pin,
                    max_distance=3.0,
                    threshold_distance=self.threshold_cm / 100.0
                )
                logger.info(f"[Ultrasonic] HC-SR04/US-015 Initialized on TRIG={self.trig_pin}, ECHO={self.echo_pin}")
            except Exception as e:
                logger.warning(f"[Ultrasonic] HC-SR04 Hardware init failed: {e}. Falling back to mock.")
                self._is_mock = True

    def get_distance_cm(self) -> float:
        """Returns distance in centimeters (or proximity estimation for US-016 direct GPIO)."""
        if self._is_mock:
            return 150.0

        # A. US-016 with ADC
        if self._adc_chan is not None:
            try:
                volts = self._adc_chan.voltage
                # US-016: 0V - 3.3V corresponds to 0 - 100cm (when Range is grounded)
                dist_cm = max(0.0, (volts / 3.3) * 100.0)
                self._readings.append(dist_cm)
                return statistics.median(self._readings)
            except Exception:
                return 150.0

        # B. US-016 Direct GPIO Proximity Mode
        if self._digital_input is not None:
            # Active presence: Pin is LOW (<1.3V, person near <50cm)
            # No presence: Pin is HIGH (>1.8V, clear >60cm)
            is_near = (self._digital_input.value == 0)
            return 35.0 if is_near else 150.0

        # C. HC-SR04 DistanceSensor
        if self._sensor is not None:
            try:
                dist_cm = self._sensor.distance * 100.0
                self._readings.append(dist_cm)
                return statistics.median(self._readings)
            except Exception:
                return 999.0

        return 150.0

    def is_person_present(self) -> bool:
        """Helper to quickly check presence regardless of sensor type."""
        dist = self.get_distance_cm()
        return dist < self.threshold_cm

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
            is_present = self.is_person_present()

            if is_present:
                if self._presence_start is None:
                    self._presence_start = time.time()
                elif (time.time() - self._presence_start) >= self.hold_time_sec:
                    # Sustained presence detected!
                    dist = self.get_distance_cm()
                    logger.info(f"[Ultrasonic] Sustained presence detected (~{dist:.1f} cm, held {self.hold_time_sec}s)")
                    if self.on_person_detected:
                        try:
                            self.on_person_detected(dist)
                        except Exception as e:
                            logger.error(f"[Ultrasonic] Callback error: {e}")
                    # Reset counter to avoid rapid duplicate firings
                    self._presence_start = None
                    time.sleep(2.0)
            else:
                self._presence_start = None

            time.sleep(0.1)
