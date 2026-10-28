"""
tts_engine.py - Edge-TTS Speech Generator with Offline File Caching & RAM Disk Protection
Converts Thai text to MP3 files via Microsoft Neural Voices.
Protects MicroSD Flash memory by routing runtime dynamic synthesis to RAM disk (/dev/shm or /tmp).
"""

import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Optional

from ..config.settings import AUDIO_CACHE_DIR, AUDIO_TEMP_DIR, VOICE_NAME, VOICE_RATE

logger = logging.getLogger(__name__)

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("[TTS] edge-tts not available.")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

class TTSEngine:
    def __init__(self,
                 cache_dir: Path = AUDIO_CACHE_DIR,
                 temp_dir: Path = AUDIO_TEMP_DIR,
                 voice: str = VOICE_NAME,
                 rate: str = VOICE_RATE):
        self.cache_dir = Path(cache_dir)
        self.temp_dir = Path(temp_dir)
        self.voice = voice
        self.rate = rate
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            self.temp_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def get_audio_path_for_text(self, text: str) -> Path:
        """Computes deterministic cache filename based on text, voice, and rate MD5."""
        text_hash = hashlib.md5(f"{self.voice}:{self.rate}:{text}".encode("utf-8")).hexdigest()
        # 1. Check permanent pre-compiled cache first
        perm_path = self.cache_dir / f"{text_hash}.mp3"
        if perm_path.is_file() and perm_path.stat().st_size > 0:
            return perm_path
        # 2. Return RAM disk path for dynamic generation (zero SD card wear)
        return self.temp_dir / f"{text_hash}.mp3"

    async def _generate_async(self, text: str, output_path: Path):
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
        # 45.0s timeout to allow long detailed meal and medication announcements
        await asyncio.wait_for(communicate.save(str(output_path)), timeout=45.0)

    def synthesize(self, text: str, permanent: bool = False) -> Optional[Path]:
        """
        Returns path to .mp3 file. Uses precompiled or RAM cache if available,
        otherwise synthesizes online directly into permanent cache or RAM disk (/dev/shm).
        """
        text_hash = hashlib.md5(f"{self.voice}:{self.rate}:{text}".encode("utf-8")).hexdigest()
        perm_path = self.cache_dir / f"{text_hash}.mp3"
        if perm_path.is_file() and perm_path.stat().st_size > 0:
            logger.debug(f"[TTS] Using cached audio for: '{text[:25]}...' ({perm_path})")
            return perm_path

        output_path = perm_path if permanent else self.get_audio_path_for_text(text)

        if output_path.is_file() and output_path.stat().st_size > 0:
            logger.debug(f"[TTS] Using cached audio for: '{text[:25]}...' ({output_path})")
            return output_path

        if not EDGE_TTS_AVAILABLE and not GTTS_AVAILABLE:
            logger.warning(f"[TTS] Cannot synthesize new text offline without edge-tts or gTTS: '{text}'")
            return None

        # 1. Try Edge-TTS (Neural Voice - Highest Quality) with retry & backup neural voice
        if EDGE_TTS_AVAILABLE:
            for voice_candidate in [self.voice, "th-TH-NiwatNeural"]:
                try:
                    logger.info(f"[TTS] Generating speech with Edge-TTS for: '{text[:30]}...' (Voice: {voice_candidate})")
                    communicate = edge_tts.Communicate(text, voice_candidate, rate=self.rate)
                    asyncio.run(asyncio.wait_for(communicate.save(str(output_path)), timeout=45.0))
                    if output_path.is_file() and output_path.stat().st_size > 0:
                        return output_path
                except Exception as e:
                    logger.warning(f"[TTS] Edge-TTS with {voice_candidate} failed: {e}")
                    if output_path.is_file() and output_path.stat().st_size == 0:
                        try:
                            output_path.unlink()
                        except Exception:
                            pass
                    import time
                    time.sleep(1.0)

        # 2. Fallback to gTTS if available
        if GTTS_AVAILABLE:
            try:
                logger.info(f"[TTS] Generating speech with gTTS fallback for: '{text[:30]}...'")
                tts_inst = gTTS(text=text, lang='th')
                tts_inst.save(str(output_path))
                if output_path.is_file() and output_path.stat().st_size > 0:
                    return output_path
            except Exception as e:
                logger.error(f"[TTS] gTTS fallback synthesis failed: {e}")
                if output_path.is_file() and output_path.stat().st_size == 0:
                    try:
                        output_path.unlink()
                    except Exception:
                        pass

        if output_path.is_file() and output_path.stat().st_size == 0:
            try:
                output_path.unlink()
            except Exception:
                pass

        return None
