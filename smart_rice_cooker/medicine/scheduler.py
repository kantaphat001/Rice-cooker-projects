"""
scheduler.py - Medication Timing & Schedule Matcher
Evaluates the current meal window and validates NTP synchronization.
"""

from datetime import datetime
import subprocess
import logging
from typing import Tuple, Optional, Dict, Any

from .repository import MedicationRepository

logger = logging.getLogger(__name__)

class MedicationScheduler:
    def __init__(self, repository: MedicationRepository):
        self.repository = repository

    def is_clock_synchronized(self) -> bool:
        """Checks if Raspberry Pi clock is valid (NTP synced or modern year)."""
        now = datetime.now()
        if now.year < 2026:
            logger.warning(f"[Scheduler] Clock year {now.year} indicates unsynchronized system clock!")
            return False

        try:
            res = subprocess.run(["timedatectl", "show", "-p", "NTPSynchronized"],
                                 capture_output=True, text=True, timeout=1.0)
            if "NTPSynchronized=yes" in res.stdout:
                return True
        except Exception:
            pass

        # If timedatectl not present, year check >= 2026 is safe
        return now.year >= 2026

    def get_current_slot_for_member(self, member_id: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Finds the matching schedule slot for member_id at the current time.
        Returns:
            (slot_key, slot_data) or (None, None)
        """
        member = self.repository.get_member(member_id)
        if not member:
            return None, None

        schedules = member.get("schedules", {})
        now_time = datetime.now().time()

        for slot_key, slot_info in schedules.items():
            try:
                start_str = slot_info.get("start_time", "00:00")
                end_str = slot_info.get("end_time", "23:59")
                start_t = datetime.strptime(start_str, "%H:%M").time()
                end_t = datetime.strptime(end_str, "%H:%M").time()

                if start_t <= now_time <= end_t:
                    return slot_key, slot_info
            except Exception as e:
                logger.error(f"[Scheduler] Time comparison error for slot {slot_key}: {e}")

        return None, None
