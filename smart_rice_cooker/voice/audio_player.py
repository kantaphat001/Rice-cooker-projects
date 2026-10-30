"""
audio_player.py - High-Fidelity Audio Playback Driver
Features:
- Uses mpg123 -q on Linux to play MP3 natively
- Native Pygame audio playback fallback on Windows
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
        self._is_mpg123 = bool(shutil.which("mpg123"))

        # Test pygame availability
        self._is_pygame = False
        if not self._is_mpg123:
            try:
                import pygame
                pygame.mixer.init()
                self._is_pygame = True
                logger.info("[AudioPlayer] Using Pygame audio engine on Windows.")
            except Exception as e:
                logger.warning(f"[AudioPlayer] Pygame init failed: {e}. Audio will be simulated.")
        else:
            # Self-healing Linux ALSA: automatically unmute and set hardware headphone volume to 100% (+4dB)
            try:
                subprocess.run(["amixer", "-c", "Headphones", "sset", "PCM", "100%", "unmute"], capture_output=True, check=False)
                subprocess.run(["amixer", "-c", "2", "sset", "PCM", "100%", "unmute"], capture_output=True, check=False)
                subprocess.run(["amixer", "sset", "PCM", "100%", "unmute"], capture_output=True, check=False)
            except Exception as e:
                logger.debug(f"[AudioPlayer] ALSA hardware unmute warning: {e}")

    def _play_file_raw(self, path: str):
        if self._is_mpg123:
            # -b 2048: 2MB RAM read-ahead buffer prevents ALSA buffer underrun and eliminates audio stuttering
            # -o alsa -a default: directly route to ALSA without PulseAudio probe delay
            subprocess.run(["mpg123", "-b", "2048", "-o", "alsa", "-a", "default", "-q", path], check=False)
        elif self._is_pygame:
            try:
                import pygame
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.05)
            except Exception as e:
                logger.error(f"[AudioPlayer] Pygame playback error: {e}")

    def play_with_chime(self, file_path: Path, chime_path: Optional[Path] = None, on_finished: Optional[Callable] = None, blocking: bool = False):
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
                        self._play_file_raw(str(chime_path))
                        time.sleep(0.4)

                    logger.info(f"[AudioPlayer] 🔊 Playing: {Path(file_path).name}")
                    self._play_file_raw(str(file_path))

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
