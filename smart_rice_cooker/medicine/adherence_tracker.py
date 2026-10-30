"""
adherence_tracker.py - Dual-Layer Medication Adherence Tracker
Combines ultra-fast RAM Disk (/dev/shm) cache with atomic persistent SD card storage.
Prevents accidental double-dosing across unexpected reboots or power flickers.
Cross-Process Live Synchronization enabled for Web Companion Portal.
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
        self._last_mtime: float = 0.0
        self._load_state()

    def _check_reload(self):
        """Reload state automatically if RAM disk or SD card file was modified by Web Companion or another process."""
        target = self.ram_path if self.ram_path.is_file() else self.disk_path
        if target.is_file():
            try:
                mtime = target.stat().st_mtime
                if mtime != self._last_mtime:
                    logger.debug(f"[Tracker] Detected external adherence update on {target.name}, reloading...")
                    self._load_state()
            except Exception:
                pass

    def _load_state(self):
        """Loads state from RAM disk if available, otherwise recovers from persistent disk."""
        target = self.ram_path if self.ram_path.is_file() else self.disk_path

        if target.is_file():
            try:
                self._last_mtime = target.stat().st_mtime
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
            self._last_mtime = self.ram_path.stat().st_mtime
        except Exception as e:
            logger.debug(f"[Tracker] RAM disk write fallback: {e}")

        # 2. Atomic write to persistent SD card
        if to_disk:
            try:
                temp_disk = self.disk_path.with_suffix(".tmp")
                with open(temp_disk, "w", encoding="utf-8") as f:
                    json.dump(self._state, f, ensure_ascii=False, indent=2)
                temp_disk.replace(self.disk_path)
                if not self.ram_path.is_file():
                    self._last_mtime = self.disk_path.stat().st_mtime
                logger.info("[Tracker] Persisted adherence state to SD card safely.")
            except Exception as e:
                logger.error(f"[Tracker] Failed to persist state to SD card: {e}")

        # 3. If running on PC (not on Pi), sync adherence_state.json to Pi via SFTP in background
        if to_disk and not Path("/home/pi").is_dir():
            import threading
            threading.Thread(target=self._sync_adherence_to_pi, daemon=True).start()

    def _sync_adherence_to_pi(self):
        """Synchronize adherence state from PC Web Manager to Raspberry Pi."""
        try:
            from ..utils import get_pi_ip
            import paramiko
            pi_ip = get_pi_ip()
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(pi_ip, username="pi", password="1234", timeout=4)
            sftp = ssh.open_sftp()
            sftp.put(str(self.disk_path), f"/home/pi/{self.disk_path.name}")
            try:
                sftp.put(str(self.disk_path), "/dev/shm/smart_cooker_state.json")
            except Exception:
                pass
            sftp.close()
            ssh.close()
            logger.info("[Tracker] Synced adherence state to Pi successfully.")
        except Exception as e:
            logger.debug(f"[Tracker] Failed to sync adherence to Pi: {e}")

    def record_reminder(self, member_id: str, slot_key: str):
        self._check_reload()
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
        self._check_reload()
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
        self._check_reload()
        slot_rec = self._state.get("records", {}).get(member_id, {}).get(slot_key, {})
        return bool(slot_rec.get("acknowledged", False))

    def is_in_cooldown(self, member_id: str, slot_key: str, cooldown_minutes: int = 20) -> bool:
        """Returns True if the person was reminded within the cooldown window."""
        self._check_reload()
        slot_rec = self._state.get("records", {}).get(member_id, {}).get(slot_key, {})
        last_time = slot_rec.get("last_reminded_at")
        if not last_time:
            return False

        elapsed_sec = time.time() - last_time
        return elapsed_sec < (cooldown_minutes * 60)

    def get_all_records(self) -> Dict[str, Any]:
        """Returns current day's adherence records for all members."""
        self._check_reload()
        return self._state

    def reset_slot(self, member_id: str, slot_key: str):
        """Resets adherence state for a specific slot."""
        self._check_reload()
        if member_id in self._state.get("records", {}):
            if slot_key in self._state["records"][member_id]:
                self._state["records"][member_id][slot_key] = {
                    "reminded_count": 0,
                    "last_reminded_at": None,
                    "acknowledged": False,
                    "acknowledged_at": None
                }
                self._save_state(to_disk=True)
                logger.info(f"[Tracker] Reset adherence state for {member_id} ({slot_key}).")
