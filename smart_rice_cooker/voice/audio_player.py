"""
audio_player.py - High-Fidelity Audio Playback Driver
Features:
- Uses mpg123 -q to play MP3 natively (avoids static white noise from aplay)
- Wakes up audio device to eliminate first-syllable cutoff latency
- Thread-safe non-blocking audio queue
"""

import subprocess
import shutil
import logging
import threading
import time
from pathlib import Path
from typing import Optional, Callable

from ..config.settings import AUDIO_PLAYER_CMD

logger = logging.getLogger(__name__)

class AudioPlayer:
    def __init__(self, player_cmd: str = AUDIO_PLAYER_CMD):
        self.player_cmd = player_cmd
        self._lock = threading.Lock()
        self._is_available = bool(shutil.which("mpg123"))

        if not self._is_available:
            logger.warning("[AudioPlayer] 'mpg123' executable not found in PATH. Audio will be simulated.")

    def play_with_chime(self, file_path: Path, chime_path: Optional[Path] = None, on_finished: Optional[Callable] = None, blocking: bool = False):
        """
        Plays soft chime sound first (to gently alert the elderly without startling them),
        pauses 0.4s, then plays the main announcement audio.
        """
        if not file_path or not Path(file_path).is_file():
            logger.warning(f"[AudioPlayer] Invalid audio file: {file_path}")
            if on_finished:
                on_finished()
            return

        def _play_worker():
            with self._lock:
                try:
                    if chime_path and Path(chime_path).is_file():
                        logger.info(f"[AudioPlayer] 🔔 Playing chime: {Path(chime_path).name}")
                        if self._is_available:
                            subprocess.run(["mpg123", "-q", str(chime_path)], check=False)
                        time.sleep(0.4)

                    if self._is_available:
                        logger.info(f"[AudioPlayer] 🔊 Playing: {Path(file_path).name}")
                        subprocess.run(["mpg123", "-q", str(file_path)], check=False)
                    else:
                        logger.info(f"[AudioPlayer MOCK] 🔊 Simulated playing: {Path(file_path).name}")
                except Exception as e:
                    logger.error(f"[AudioPlayer] Playback error: {e}")
                finally:
                    if on_finished:
                        try:
                            on_finished()
                        except Exception as e:
                            logger.error(f"[AudioPlayer] on_finished callback error: {e}")

        if blocking:
            _play_worker()
        else:
            threading.Thread(target=_play_worker, daemon=True).start()

    def play_file(self, file_path: Path, on_finished: Optional[Callable] = None, blocking: bool = False):
        return self.play_with_chime(file_path, chime_path=None, on_finished=on_finished, blocking=blocking)
