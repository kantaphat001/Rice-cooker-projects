"""
scheduler.py - Medication Timing & Schedule Matcher
Evaluates current meal windows, next upcoming meals, and overdose safety cutoff windows.
"""

from datetime import datetime, timedelta
import subprocess
import logging
from typing import Tuple, Optional, Dict, Any, List

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

        return now.year >= 2026

    def get_current_slot_for_member(self, member_id: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Finds the matching schedule slot for member_id at current time.
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

    def get_next_slot_for_member(self, member_id: str) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[int]]:
        """
        Finds the next upcoming meal slot for member_id and calculates remaining minutes.
        Returns:
            (slot_key, slot_data, minutes_until_start) or (None, None, None)
        """
        member = self.repository.get_member(member_id)
        if not member:
            return None, None, None

        schedules = member.get("schedules", {})
        now = datetime.now()
        now_time = now.time()

        upcoming = []
        for slot_key, slot_info in schedules.items():
            try:
                start_str = slot_info.get("start_time", "00:00")
                start_t = datetime.strptime(start_str, "%H:%M").time()
                slot_datetime = datetime.combine(now.date(), start_t)

                if start_t > now_time:
                    diff_min = int((slot_datetime - now).total_seconds() / 60)
                    upcoming.append((diff_min, slot_key, slot_info))
                else:
                    # Slot tomorrow
                    diff_min = int(((slot_datetime + timedelta(days=1)) - now).total_seconds() / 60)
                    upcoming.append((diff_min, slot_key, slot_info))
            except Exception as e:
                logger.error(f"[Scheduler] Error calculating next slot {slot_key}: {e}")

        if not upcoming:
            return None, None, None

        upcoming.sort(key=lambda x: x[0])
        minutes_remaining, next_key, next_info = upcoming[0]
        return next_key, next_info, minutes_remaining

    def get_missed_earlier_slot(self, member_id: str, tracker) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Finds the most recent missed (unacknowledged) slot earlier today that had prescribed meds.
        Returns:
            (slot_key, slot_data) or None
        """
        member = self.repository.get_member(member_id)
        if not member:
            return None

        schedules = member.get("schedules", {})
        now_time = datetime.now().time()
        missed = []

        for slot_key, slot_info in schedules.items():
            try:
                end_str = slot_info.get("end_time", "23:59")
                end_t = datetime.strptime(end_str, "%H:%M").time()

                # If slot has already ended earlier today
                if end_t < now_time:
                    all_meds = slot_info.get("before_meal", []) + slot_info.get("after_meal", [])
                    if all_meds and not tracker.is_acknowledged(member_id, slot_key):
                        missed.append((end_t, slot_key, slot_info))
            except Exception as e:
                logger.error(f"[Scheduler] Error checking missed slot {slot_key}: {e}")

        if not missed:
            return None

        # Return the most recent missed meal
        missed.sort(key=lambda x: x[0], reverse=True)
        _, slot_key, slot_info = missed[0]
        return slot_key, slot_info

    def is_overdose_hazard(self, member_id: str, cutoff_minutes: int = 60) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Checks if the next meal starts in less than cutoff_minutes (preventing double dose).
        Returns:
            (is_hazard, minutes_remaining, next_slot_label)
        """
        next_key, next_info, minutes_remaining = self.get_next_slot_for_member(member_id)
        if next_info and minutes_remaining is not None and minutes_remaining < cutoff_minutes:
            label = next_info.get("label", next_key)
            return True, minutes_remaining, label
        return False, minutes_remaining, next_info.get("label") if next_info else None
