"""
repository.py - Loads and Validates med_config.json
Provides safe fallback to med_config.example.json if configuration is missing.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from ..config.settings import CONFIG_FILE, EXAMPLE_CONFIG_FILE

logger = logging.getLogger(__name__)

class MedicationRepository:
    def __init__(self, config_path: Path = CONFIG_FILE, example_path: Path = EXAMPLE_CONFIG_FILE):
        self.config_path = Path(config_path)
        self.example_path = Path(example_path)
        self._data: Dict[str, Any] = {}
        self.reload()

    def reload(self):
        target = self.config_path if self.config_path.is_file() else self.example_path
        if not target.is_file():
            logger.error(f"[MedRepo] Neither {self.config_path} nor {self.example_path} exists!")
            self._data = {"members": {}}
            return

        try:
            with open(target, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            logger.info(f"[MedRepo] Successfully loaded medication config from {target.name}")
        except Exception as e:
            logger.error(f"[MedRepo] Failed to parse JSON configuration from {target}: {e}")
            self._data = {"members": {}}

    def get_member(self, member_id: str) -> Dict[str, Any]:
        return self._data.get("members", {}).get(member_id, {})

    def get_all_members(self) -> Dict[str, Any]:
        return self._data.get("members", {})
