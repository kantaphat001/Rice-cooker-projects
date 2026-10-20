"""
pc_audio.py - Native Windows Audio Player for Remote Companion Box Relay
Plays MP3 audio files directly through Windows PC speakers without requiring
external media players (uses built-in Windows PresentationCore MediaPlayer).
"""

import os
import subprocess
import threading
from pathlib import Path

LOCAL_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_cache")

def _powershell_play(abs_path: str):
    safe_path = abs_path.replace("'", "''")
    ps_cmd = (
        f"Add-Type -AssemblyName presentationCore; "
        f"$player = New-Object System.Windows.Media.MediaPlayer; "
        f"$player.Open('{safe_path}'); "
        f"$player.Play(); "
        f"Start-Sleep -Milliseconds 600; "
        f"$elapsed = 0; "
        f"while (-not $player.NaturalDuration.HasTimeSpan -and $elapsed -lt 3000) {{ "
        f"  Start-Sleep -Milliseconds 100; $elapsed += 100 "
        f"}}; "
        f"if ($player.NaturalDuration.HasTimeSpan) {{ "
        f"  $duration = [math]::Ceiling($player.NaturalDuration.TimeSpan.TotalSeconds); "
        f"  Start-Sleep -Seconds $duration "
        f"}} else {{ "
        f"  Start-Sleep -Seconds 4 "
        f"}}; "
        f"$player.Close(); "
        f"exit 0"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            capture_output=True,
            check=False
        )
    except Exception as e:
        print(f"[PC Audio Error] Failed to play: {e}")

def play_audio(mp3_path: str, blocking: bool = False):
    """Play an MP3 audio file through Windows PC speakers."""
    if not os.path.exists(mp3_path):
        return False
    
    abs_path = os.path.abspath(mp3_path)
    if blocking:
        _powershell_play(abs_path)
    else:
        t = threading.Thread(target=_powershell_play, args=(abs_path,), daemon=True)
        t.start()
    return True

def play_cached_file(filename: str, sftp=None, blocking: bool = False):
    """
    Play a cached MP3 file. If not found locally, fetch from Pi via SFTP.
    """
    os.makedirs(LOCAL_CACHE_DIR, exist_ok=True)
    clean_name = os.path.basename(filename.strip().replace("'", "").replace('"', ""))
    if not clean_name.endswith(".mp3"):
        clean_name += ".mp3"
        
    local_path = os.path.join(LOCAL_CACHE_DIR, clean_name)
    
    if not os.path.exists(local_path) and sftp is not None:
        try:
            remote_path = f"/home/pi/audio_cache/{clean_name}"
            sftp.get(remote_path, local_path)
        except Exception:
            pass
            
    if os.path.exists(local_path):
        return play_audio(local_path, blocking=blocking)
    return False

if __name__ == "__main__":
    print("[*] Testing Windows PC audio playback...")
    ok = play_cached_file("test.mp3", blocking=True)
    print(f"[+] Audio playback result: {ok}")
