"""
tts_engine.py - Edge-TTS Speech Generator with Offline File Caching
Converts Thai text to MP3 files via Microsoft Neural Voices.
Saves cache to disk so audio plays instantaneously offline.
"""

import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Optional

from ..config.settings import AUDIO_CACHE_DIR, VOICE_NAME, VOICE_RATE

logger = logging.getLogger(__name__)

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("[TTS] edge-tts not available. Voice synthesis will use cache only.")

class TTSEngine:
    def __init__(self, cache_dir: Path = AUDIO_CACHE_DIR, voice: str = VOICE_NAME, rate: str = VOICE_RATE):
        self.cache_dir = Path(cache_dir)
        self.voice = voice
        self.rate = rate
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_audio_path_for_text(self, text: str) -> Path:
        """Computes deterministic cache filename based on text, voice, and rate MD5."""
        text_hash = hashlib.md5(f"{self.voice}:{self.rate}:{text}".encode("utf-8")).hexdigest()
        return self.cache_dir / f"{text_hash}.mp3"

    async def _generate_async(self, text: str, output_path: Path):
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
        await communicate.save(str(output_path))

    def synthesize(self, text: str) -> Optional[Path]:
        """
        Returns path to .mp3 file. Uses cache if available,
        otherwise synthesizes online and saves to cache.
        """
        output_path = self.get_audio_path_for_text(text)

        if output_path.is_file() and output_path.stat().st_size > 0:
            logger.debug(f"[TTS] Using cached audio for: '{text[:25]}...'")
            return output_path

        if not EDGE_TTS_AVAILABLE:
            logger.warning(f"[TTS] Cannot synthesize new text offline without edge-tts: '{text}'")
            return None

        try:
            logger.info(f"[TTS] Generating speech online for: '{text[:30]}...'")
            asyncio.run(self._generate_async(text, output_path))
            return output_path
        except Exception as e:
            logger.error(f"[TTS] Synthesis failed: {e}")
            return None
