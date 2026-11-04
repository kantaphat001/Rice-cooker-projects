import os
import sys
from pathlib import Path
import paramiko

PI_HOST = "10.50.49.17"
PI_USER = "pi"
PI_PASS = "1234"
REMOTE_BASE = "/home/pi"

def main():
    print(f"Connecting to {PI_HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(PI_HOST, username=PI_USER, password=PI_PASS, timeout=10)
    sftp = ssh.open_sftp()
    print("Connected via SFTP.")

    # 1. Sync code files
    files_to_sync = [
        "smart_rice_cooker/config/settings.py",
        "smart_rice_cooker/hardware/fan_controller.py",
        "smart_rice_cooker/voice/tts_engine.py",
        "smart_rice_cooker/service.py",
        "web/frontend/js/components/schedule_board.js",
        "web/backend/server.py",
        "deploy/precompile_all_female.py",
    ]

    for rel_path in files_to_sync:
        local_file = Path(rel_path)
        remote_file = f"{REMOTE_BASE}/{rel_path.replace(os.sep, '/')}"
        print(f"Uploading {local_file} -> {remote_file}")
        sftp.put(str(local_file), remote_file)

    # 2. Sync audio_cache files
    local_cache = Path("audio_cache")
    remote_cache = f"{REMOTE_BASE}/audio_cache"
    try:
        sftp.mkdir(remote_cache)
    except Exception:
        pass

    # List existing files on Pi
    remote_files = set(sftp.listdir(remote_cache))
    mp3_files = list(local_cache.glob("*.mp3"))
    print(f"Syncing {len(mp3_files)} audio files to {remote_cache}...")

    uploaded = 0
    for mp3 in mp3_files:
        if mp3.stat().st_size == 0:
            continue
        # If not on remote or size differs, upload
        needs_upload = False
        if mp3.name not in remote_files:
            needs_upload = True
        else:
            try:
                r_stat = sftp.stat(f"{remote_cache}/{mp3.name}")
                if r_stat.st_size != mp3.stat().st_size:
                    needs_upload = True
            except Exception:
                needs_upload = True

        if needs_upload:
            sftp.put(str(mp3), f"{remote_cache}/{mp3.name}")
            uploaded += 1
            if uploaded % 10 == 0:
                print(f"Uploaded {uploaded} files...")

    print(f"Audio cache sync complete. Uploaded {uploaded} updated files.")

    # 3. Restart systemd services
    print("Restarting system services on Pi...")
    stdin, stdout, stderr = ssh.exec_command("sudo systemctl restart smart-cooker.service smart-cooker-web.service")
    out = stdout.read().decode()
    err = stderr.read().decode()
    if err:
        print("Service restart note:", err)

    # Check status
    stdin, stdout, stderr = ssh.exec_command("systemctl is-active smart-cooker.service smart-cooker-web.service")
    status = stdout.read().decode().strip()
    print("Services status:\n" + status)

    sftp.close()
    ssh.close()
    print("[+] Deployment to Pi finished successfully!")

if __name__ == "__main__":
    main()
