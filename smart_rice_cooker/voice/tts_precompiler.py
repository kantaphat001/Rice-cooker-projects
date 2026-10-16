"""
tts_precompiler.py - Audio Offline Cache Precompiler
Reads med_config.json and pre-generates speech files on startup.
Eliminates API latency and ensures 100% offline operation.
"""

import logging
from typing import Dict, Any

from .tts_engine import TTSEngine
from .phrase_builder import ThaiPhraseBuilder
from ..medicine.repository import MedicationRepository

logger = logging.getLogger(__name__)

class TTSPrecompiler:
    def __init__(self, tts_engine: TTSEngine, repository: MedicationRepository):
        self.tts = tts_engine
        self.repo = repository

    def precompile_all(self):
        logger.info("[TTS Precompiler] Pre-compiling static phrases to offline cache...")
        members = self.repo.get_all_members()

        # 1. Precompile unknown visitor
        self.tts.synthesize(ThaiPhraseBuilder.build_unknown_visitor_message())

        # 2. Precompile member phrases
        for member_id, member_info in members.items():
            greeting = member_info.get("voice_greeting", "สวัสดีครับ")
            display_name = member_info.get("display_name", member_id)

            # Common responses
            self.tts.synthesize(ThaiPhraseBuilder.build_already_taken_message(display_name))
            self.tts.synthesize(ThaiPhraseBuilder.build_unacknowledged_followup(display_name))
            self.tts.synthesize(ThaiPhraseBuilder.build_no_meds_message(greeting))

            # Schedule announcements
            schedules = member_info.get("schedules", {})
            for slot_key, slot_data in schedules.items():
                label = slot_data.get("label", slot_key)
                before = slot_data.get("before_meal", [])
                after = slot_data.get("after_meal", [])
                full_text = ThaiPhraseBuilder.build_full_meal_announcement(greeting, label, before, after)
                self.tts.synthesize(full_text)

        logger.info("[TTS Precompiler] Pre-compilation completed successfully!")
