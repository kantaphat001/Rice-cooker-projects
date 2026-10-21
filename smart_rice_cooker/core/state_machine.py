"""
state_machine.py - Finite State Machine (FSM) for Companion Box
Orchestrates transitions between STANDBY (Red LED), DETECTING (Yellow LED),
ANNOUNCING (Green LED), and ECO_SLEEP (All LEDs off, hardware sleeping).
"""

from enum import Enum, auto
import time
import logging

logger = logging.getLogger(__name__)

class SystemState(Enum):
    STANDBY = auto()    # Red LED: Idle, waiting for presence
    DETECTING = auto()  # Yellow LED: Scanning face, identifying person
    ANNOUNCING = auto() # Green LED: Announcing medication details & UI update
    COOLDOWN = auto()   # Short pause to prevent re-triggering
    ECO_SLEEP = auto()  # All LEDs off, camera suspended, ultrasonic in sniffer mode

class CompanionStateMachine:
    def __init__(self, on_state_change=None):
        self._current_state = SystemState.STANDBY
        self._state_entered_time = time.time()
        self._on_state_change = on_state_change

    @property
    def current_state(self) -> SystemState:
        return self._current_state

    @property
    def time_in_state(self) -> float:
        return time.time() - self._state_entered_time

    def transition_to(self, new_state: SystemState, context: dict = None):
        if self._current_state == new_state:
            return

        old_state = self._current_state
        self._current_state = new_state
        self._state_entered_time = time.time()
        logger.info(f"[FSM] State transition: {old_state.name} -> {new_state.name}")

        if self._on_state_change:
            try:
                self._on_state_change(old_state, new_state, context or {})
            except Exception as e:
                logger.error(f"[FSM] Error in state change callback: {e}")
