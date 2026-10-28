"""
sync_offline_assets.py
Synchronizes med_config.json, code fixes, and all precompiled audio files to Raspberry Pi.
"""

import os
import sys
import time
from pathlib import Path
import paramiko

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from smart_rice_cooker.utils import get_pi_ip

PI_HOST = get_pi_ip()
PI_USER = "pi"
PI_PASS = "1234"

def sync():
    print(f"[*] Connecting to Raspberry Pi at {PI_HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(PI_HOST, port=22, username=PI_USER, password=PI_PASS, timeout=5)
    sftp = ssh.open_sftp()
    
    # 1. Upload med_config.json
    local_cfg = ROOT_DIR / "med_config.json"
    remote_cfg = "/home/pi/med_config.json"
    print(f"[*] Uploading {local_cfg.name} -> {remote_cfg}...")
    sftp.put(str(local_cfg), remote_cfg)
    
    # 2. Upload modules
    files_to_sync = [
        ("smart_rice_cooker/config/settings.py", "/home/pi/smart_rice_cooker/config/settings.py"),
        ("smart_rice_cooker/service.py", "/home/pi/smart_rice_cooker/service.py"),
        ("smart_rice_cooker/hardware/camera_manager.py", "/home/pi/smart_rice_cooker/hardware/camera_manager.py"),
        ("smart_rice_cooker/hardware/ultrasonic_sensor.py", "/home/pi/smart_rice_cooker/hardware/ultrasonic_sensor.py"),
        ("smart_rice_cooker/voice/tts_engine.py", "/home/pi/smart_rice_cooker/voice/tts_engine.py"),
        ("smart_rice_cooker/voice/phrase_builder.py", "/home/pi/smart_rice_cooker/voice/phrase_builder.py"),
        ("smart_rice_cooker/voice/audio_player.py", "/home/pi/smart_rice_cooker/voice/audio_player.py"),
        ("smart_rice_cooker/voice/tts_precompiler.py", "/home/pi/smart_rice_cooker/voice/tts_precompiler.py"),
    ]
    for rel_local, remote_p in files_to_sync:
        local_p = ROOT_DIR / rel_local
        print(f"[*] Uploading {rel_local}...")
        sftp.put(str(local_p), remote_p)
    
    # 3. Upload all audio_cache files
    local_cache = ROOT_DIR / "audio_cache"
    print(f"[*] Uploading audio_cache files...")
    count = 0
    for mp3_path in local_cache.glob("*.mp3"):
        remote_path = f"/home/pi/audio_cache/{mp3_path.name}"
        sftp.put(str(mp3_path), remote_path)
        count += 1
    print(f"[+] Synced {count} audio files to /home/pi/audio_cache/")

    sftp.close()
    
    # 4. Restart smart-cooker service
    print("[*] Restarting smart-cooker.service on Pi...")
    stdin, stdout, stderr = ssh.exec_command("echo 1234 | sudo -S systemctl restart smart-cooker.service")
    stdout.channel.recv_exit_status()
    time.sleep(2)
    
    # 5. Check status
    stdin, stdout, stderr = ssh.exec_command("systemctl is-active smart-cooker.service")
    status = stdout.read().decode().strip()
    print(f"[+] smart-cooker.service status: {status}")
    
    ssh.close()
    print("[SUCCESS] All offline assets successfully synchronized!")

if __name__ == "__main__":
    sync()
