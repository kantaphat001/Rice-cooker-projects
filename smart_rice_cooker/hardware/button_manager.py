"""
button_manager.py - Physical Acknowledge Button Controller (GPIO 25)
Provides tactile, zero-ambiguity confirmation for elderly users.
Uses internal pull-up and hardware debouncing.
"""

import logging

logger = logging.getLogger(__name__)

try:
    from gpiozero import Button
    GPIOZERO_BUTTON_AVAILABLE = True
except (ImportError, Exception):
    GPIOZERO_BUTTON_AVAILABLE = False
    logger.warning("[Button] gpiozero Button not available. Running in MOCK mode.")

class ButtonManager:
    def __init__(self, pin: int = None, on_pressed=None, bounce_time: float = 0.2):
        self.pin = pin
        self.on_pressed = on_pressed
        self.bounce_time = bounce_time
        self._button = None
        self._is_mock = not GPIOZERO_BUTTON_AVAILABLE or pin is None

        if not self._is_mock and pin is not None:
            try:
                # pull_up=True means button connects GPIO pin to GND
                self._button = Button(self.pin, pull_up=True, bounce_time=self.bounce_time)
                self._button.when_pressed = self._handle_press
                logger.info(f"[Button] Initialized Physical Acknowledge Button on GPIO {self.pin} (Pull-Up)")
            except Exception as e:
                logger.warning(f"[Button] Failed to initialize hardware button: {e}. Falling back to mock.")
                self._is_mock = True
        elif pin is None:
            logger.info("[Button] Running in Zero-Touch / Hands-Free mode (No physical button).")

    def _handle_press(self):
        logger.info("[Button] 🔘 Physical Acknowledge Button Pressed!")
        if self.on_pressed:
            try:
                self.on_pressed()
            except Exception as e:
                logger.error(f"[Button] Error in on_pressed callback: {e}")

    def simulate_press(self):
        """Allows testing button presses from GUI or mock scripts."""
        logger.info("[Button MOCK] Simulating button press...")
        self._handle_press()

    def close(self):
        if self._button:
            try:
                self._button.close()
            except Exception:
                pass
