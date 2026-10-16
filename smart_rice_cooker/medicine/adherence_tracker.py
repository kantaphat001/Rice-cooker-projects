"""
adherence_tracker.py - Dual-Layer Medication Adherence Tracker
Combines ultra-fast RAM Disk (/dev/shm) cache with atomic persistent SD card storage.
Prevents accidental double-dosing across unexpected reboots or power flickers.
"""

import json
import os
import time
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any

from ..config.settings import RAM_STATE_FILE, PERSISTENT_STATE_FILE

logger = logging.getLogger(__name__)

class AdherenceTracker:
    def __init__(self, ram_path: Path = RAM_STATE_FILE, disk_path: Path = PERSISTENT_STATE_FILE):
        self.ram_path = Path(ram_path)
        self.disk_path = Path(disk_path)
        self._state: Dict[str, Any] = {}
        self._load_state()

    def _load_state(self):
        """Loads state from RAM disk if available, otherwise recovers from persistent disk."""
        target = self.ram_path if self.ram_path.is_file() else self.disk_path

        if target.is_file():
            try:
                with open(target, "r", encoding="utf-8") as f:
                    self._state = json.load(f)
            except Exception as e:
                logger.warning(f"[Tracker] Error reading state from {target}: {e}")
                self._state = {}

        today_str = str(date.today())
        if self._state.get("date") != today_str:
            logger.info(f"[Tracker] Resetting state for new day: {today_str}")
            self._state = {"date": today_str, "records": {}}
            self._save_state(to_disk=True)

    def _save_state(self, to_disk: bool = False):
        """Atomic write to RAM disk and conditionally to SD card."""
        today_str = str(date.today())
        self._state["date"] = today_str

        # 1. Write to RAM disk (/dev/shm) for speed
        try:
            temp_ram = self.ram_path.with_suffix(".tmp")
            with open(temp_ram, "w", encoding="utf-8") as f:
                json.dump(self._state, f, ensure_ascii=False, indent=2)
            temp_ram.replace(self.ram_path)
        except Exception as e:
            logger.debug(f"[Tracker] RAM disk write fallback: {e}")

        # 2. Atomic write to persistent SD card
        if to_disk:
            try:
                temp_disk = self.disk_path.with_suffix(".tmp")
                with open(temp_disk, "w", encoding="utf-8") as f:
                    json.dump(self._state, f, ensure_ascii=False, indent=2)
                temp_disk.replace(self.disk_path)
                logger.info("[Tracker] Persisted adherence state to SD card safely.")
            except Exception as e:
                logger.error(f"[Tracker] Failed to persist state to SD card: {e}")

    def record_reminder(self, member_id: str, slot_key: str):
        records = self._state.setdefault("records", {}).setdefault(member_id, {})
        slot_rec = records.setdefault(slot_key, {
            "reminded_count": 0,
            "last_reminded_at": None,
            "acknowledged": False,
            "acknowledged_at": None
        })

        slot_rec["reminded_count"] += 1
        slot_rec["last_reminded_at"] = time.time()
        self._save_state(to_disk=True)
        logger.info(f"[Tracker] Recorded reminder for {member_id} ({slot_key}). Count={slot_rec['reminded_count']}")

    def record_acknowledgement(self, member_id: str, slot_key: str):
        records = self._state.setdefault("records", {}).setdefault(member_id, {})
        slot_rec = records.setdefault(slot_key, {
            "reminded_count": 1,
            "last_reminded_at": time.time(),
            "acknowledged": True,
            "acknowledged_at": None
        })

        slot_rec["acknowledged"] = True
        slot_rec["acknowledged_at"] = time.time()
        self._save_state(to_disk=True)
        logger.info(f"[Tracker] ✅ Acknowledged medication taken: {member_id} ({slot_key})")

    def is_acknowledged(self, member_id: str, slot_key: str) -> bool:
        slot_rec = self._state.get("records", {}).get(member_id, {}).get(slot_key, {})
        return bool(slot_rec.get("acknowledged", False))

    def is_in_cooldown(self, member_id: str, slot_key: str, cooldown_minutes: int = 20) -> bool:
        """Returns True if the person was reminded within the cooldown window."""
        slot_rec = self._state.get("records", {}).get(member_id, {}).get(slot_key, {})
        last_time = slot_rec.get("last_reminded_at")
        if not last_time:
            return False

        elapsed_sec = time.time() - last_time
        return elapsed_sec < (cooldown_minutes * 60)
