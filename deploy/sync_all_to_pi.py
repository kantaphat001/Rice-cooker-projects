import os
import sys
from pathlib import Path
import paramiko

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from web.backend.network_utils import get_pi_ip

PI_USER = "pi"
PI_PASS = "1234"
REMOTE_BASE = "/home/pi"

def main():
    pi_host = get_pi_ip()
    print(f"Connecting to Raspberry Pi at {pi_host}...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(pi_host, username=PI_USER, password=PI_PASS, timeout=8)
    except Exception as e:
        print(f"[!] Could not connect to {pi_host}: {e}")
        return

    sftp = ssh.open_sftp()
    print("[+] Connected via SSH & SFTP.")

    # 1. Sync whole project folders
    folders_to_sync = ["smart_rice_cooker", "web", "deploy", "tools"]
    ignore_dirs = {"__pycache__", ".git", "dataset", "audio_cache", "snapshots", ".system_generated"}

    for folder in folders_to_sync:
        local_dir = ROOT_DIR / folder
        if not local_dir.is_dir():
            continue
        for root, dirs, files in os.walk(local_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            rel_dir = Path(root).relative_to(ROOT_DIR).as_posix()
            remote_dir = f"{REMOTE_BASE}/{rel_dir}"
            try:
                sftp.stat(remote_dir)
            except IOError:
                ssh.exec_command(f"mkdir -p {remote_dir}")

            for f in files:
                if f.endswith((".py", ".js", ".html", ".css", ".json", ".svg", ".png", ".jpg", ".sh", ".service")):
                    local_f = Path(root) / f
                    remote_f = f"{remote_dir}/{f}"
                    try:
                        r_stat = sftp.stat(remote_f)
                        if r_stat.st_mtime >= local_f.stat().st_mtime and r_stat.st_size == local_f.stat().st_size:
                            continue
                    except IOError:
                        pass
                    print(f"Uploading {rel_dir}/{f} -> {remote_f}")
                    sftp.put(str(local_f), remote_f)

    # 2. Sync root script files
    root_files = ["web_manager.py", "run_companion_box.py", "config_ip.txt"]
    for rf in root_files:
        rf_path = ROOT_DIR / rf
        if rf_path.exists():
            remote_f = f"{REMOTE_BASE}/{rf}"
            print(f"Uploading {rf} -> {remote_f}")
            sftp.put(str(rf_path), remote_f)

    # 3. Restart systemd services safely with sudo password
    print("\n[*] Restarting system services on Pi...")
    restart_cmd = f"echo {PI_PASS} | sudo -S systemctl restart smart-cooker.service smart-cooker-web.service"
    stdin, stdout, stderr = ssh.exec_command(restart_cmd)
    stdout.channel.recv_exit_status()

    # Check status
    stdin, stdout, stderr = ssh.exec_command("systemctl is-active smart-cooker.service smart-cooker-web.service")
    status = stdout.read().decode().strip()
    print("Services status:\n" + status)

    sftp.close()
    ssh.close()
    print("\n[+] Full sync to Raspberry Pi completed successfully!")

if __name__ == "__main__":
    main()
