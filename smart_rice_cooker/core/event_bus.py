"""
event_bus.py - Thread-Safe Decoupled Event System
Ensures background threads (Camera, GPIO, Timers) communicate safely
with Main Loop and Tkinter GUI via queue.Queue without thread collisions.
"""

import queue
from typing import Callable, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class Event:
    def __init__(self, event_type: str, data: Any = None):
        self.event_type = event_type
        self.data = data or {}

    def __repr__(self):
        return f"<Event {self.event_type} data={self.data}>"

class EventBus:
    def __init__(self):
        self._queue = queue.Queue()
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, data: Any = None):
        """Called from any thread safely."""
        event = Event(event_type, data)
        self._queue.put(event)

    def process_events(self, max_events: int = 20):
        """Called periodically from the Main Thread (e.g. Tkinter root.after)."""
        count = 0
        while not self._queue.empty() and count < max_events:
            try:
                event = self._queue.get_nowait()
                callbacks = self._subscribers.get(event.event_type, [])
                for cb in callbacks:
                    try:
                        cb(event.data)
                    except Exception as e:
                        logger.error(f"[EventBus] Error executing subscriber for {event.event_type}: {e}")
                self._queue.task_done()
                count += 1
            except queue.Empty:
                break
