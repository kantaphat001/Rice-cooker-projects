"""
led_controller.py - 3-Color Indicator LED Controller (Red, Yellow, Green)
Implements precise UX states:
- Red: Standby / Idle (still, ready)
- Yellow: Face Detection in progress
- Green Solid: Announcing active medication
- Green Pulse/Blink: Friendly greeting / already taken / outside meal times
"""

import time
import logging
import threading

logger = logging.getLogger(__name__)

try:
    from gpiozero import LED
    GPIOZERO_AVAILABLE = True
except (ImportError, Exception):
    GPIOZERO_AVAILABLE = False
    logger.warning("[LED] gpiozero not available. Running in MOCK LED mode.")

class LEDController:
    def __init__(self, pin_red: int, pin_yellow: int, pin_green: int):
        self.pin_red = pin_red
        self.pin_yellow = pin_yellow
        self.pin_green = pin_green
        self._is_mock = not GPIOZERO_AVAILABLE
        self._lock = threading.Lock()

        if not self._is_mock:
            try:
                self.red = LED(pin_red)
                self.yellow = LED(pin_yellow)
                self.green = LED(pin_green)
                logger.info(f"[LED] Initialized hardware LEDs on pins: R={pin_red}, Y={pin_yellow}, G={pin_green}")
            except Exception as e:
                logger.warning(f"[LED] Failed to initialize hardware LEDs: {e}. Falling back to mock.")
                self._is_mock = True

        if self._is_mock:
            self.red = None
            self.yellow = None
            self.green = None

        # Start in Standby (Red ON)
        self.set_standby()

    def all_off(self):
        with self._lock:
            if not self._is_mock:
                for led in (self.red, self.yellow, self.green):
                    try:
                        if led:
                            led.off()
                    except Exception:
                        pass
            else:
                logger.debug("[LED MOCK] All LEDs OFF")

    def set_standby(self):
        """Red ON, Yellow/Green OFF."""
        with self._lock:
            if not self._is_mock:
                self.yellow.off()
                self.green.off()
                self.red.on()
            logger.info("[LED] State: 🔴 STANDBY (Red ON)")

    def set_detecting(self):
        """Yellow ON, Red/Green OFF."""
        with self._lock:
            self.red.off() if not self._is_mock else None
            self.green.off() if not self._is_mock else None
            self.yellow.on() if not self._is_mock else None
            logger.info("[LED] State: 🟡 DETECTING (Yellow ON)")

    def set_announcing(self, has_meds: bool = True):
        """Green ON (Solid if has_meds, Pulse if friendly greeting)."""
        if has_meds:
            with self._lock:
                self.red.off() if not self._is_mock else None
                self.yellow.off() if not self._is_mock else None
                self.green.on() if not self._is_mock else None
                logger.info("[LED] State: 🟢 ANNOUNCING MEDS (Green Solid ON)")
        else:
            # Non-blocking pulse for greeting
            threading.Thread(target=self._pulse_green, daemon=True).start()

    def _pulse_green(self):
        logger.info("[LED] State: 🟢 GREETING PULSE (Green Blink x2)")
        with self._lock:
            self.red.off() if not self._is_mock else None
            self.yellow.off() if not self._is_mock else None

        for _ in range(2):
            if not self._is_mock:
                self.green.on()
            time.sleep(0.3)
            if not self._is_mock:
                self.green.off()
            time.sleep(0.2)

        self.set_standby()

    def close(self):
        try:
            self.all_off()
        except Exception:
            pass
        if not self._is_mock:
            for led in (self.red, self.yellow, self.green):
                try:
                    if led:
                        led.close()
                except Exception:
                    pass
