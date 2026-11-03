"""
fan_controller.py - Cooling Fan Relay Controller for Smart Rice Cooker
Controls 5V Relay module (e.g. Tongling JQC-3FF-S-Z) connected to Raspberry Pi GPIO.

Operational Behavior:
1. Boot / Power-on: Fan turns ON immediately and stays running continuously.
2. Active States (Standby, Detecting, Announcing): Fan stays ON.
3. Eco-Sleep State: Fan turns OFF to conserve energy and eliminate noise.
4. Wake-up from Eco-Sleep: Fan turns back ON automatically.
"""

import logging
import threading

logger = logging.getLogger(__name__)

try:
    from gpiozero import OutputDevice
    GPIOZERO_AVAILABLE = True
except (ImportError, Exception):
    GPIOZERO_AVAILABLE = False
    logger.warning("[Fan] gpiozero not available. Running in MOCK Fan mode.")


class FanController:
    """Controls 5V Relay module for cooling fan."""

    def __init__(self, pin: int = 18, active_low: bool = True, enabled: bool = True):
        self.pin = pin
        self.active_low = active_low
        self.enabled = enabled
        self._is_mock = not GPIOZERO_AVAILABLE
        self._lock = threading.Lock()
        self._is_running = False
        self._device = None

        if not self.enabled:
            logger.info("[Fan] Cooling fan control is disabled in settings.")
            return

        if not self._is_mock:
            try:
                # In gpiozero OutputDevice:
                # If active_low=True (standard 5V relay module):
                #   active_high=False means calling .on() pulls pin LOW (0V) to energize relay coil.
                #   initial_value=True means the fan starts running immediately on boot!
                self._device = OutputDevice(
                    pin=pin,
                    active_high=not active_low,
                    initial_value=True
                )
                self._is_running = True
                logger.info(f"[Fan] Hardware cooling fan relay initialized on GPIO {pin} (Active-Low={active_low}, State=ON)")
            except Exception as e:
                logger.warning(f"[Fan] Failed to initialize hardware relay on GPIO {pin}: {e}. Falling back to mock.")
                self._is_mock = True
                self._device = None
                self._is_running = True
        else:
            self._is_running = True
            logger.info(f"[Fan] Initialized Mock Fan Controller on GPIO {pin} (State=ON)")

    def start(self):
        """Turns ON the cooling fan."""
        if not self.enabled:
            return
        with self._lock:
            if not self._is_running or (self._device and not self._device.is_active):
                if not self._is_mock and self._device:
                    try:
                        self._device.on()
                    except Exception as e:
                        logger.error(f"[Fan] Error starting fan: {e}")
                self._is_running = True
                logger.info("[Fan] 🌀 Cooling Fan started (Running)")

    def stop(self):
        """Turns OFF the cooling fan (Eco-Sleep mode)."""
        if not self.enabled:
            return
        with self._lock:
            if self._is_running or (self._device and self._device.is_active):
                if not self._is_mock and self._device:
                    try:
                        self._device.off()
                    except Exception as e:
                        logger.error(f"[Fan] Error stopping fan: {e}")
                self._is_running = False
                logger.info("[Fan] ⏸️ Cooling Fan stopped (Eco-Sleep power saving)")

    @property
    def is_running(self) -> bool:
        return self._is_running

    def cleanup(self):
        """Safely shuts down relay device."""
        with self._lock:
            if not self._is_mock and self._device:
                try:
                    self._device.off()
                    self._device.close()
                except Exception:
                    pass
            self._is_running = False
