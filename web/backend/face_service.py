"""
Face dataset and AI recognition service for Smart Rice Cooker.
Manages local face photos, gallery listing, upload, deletion, and AI model rebuild.
Supports Dual-Mode operation:
- Native execution when running on Raspberry Pi (Direct OpenCV & systemctl)
- Remote execution when running on PC (Paramiko SSH & SFTP)
"""
import os
import time
import base64
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from web.backend.network_utils import get_pi_ip
from web.backend.config_service import load_config, PI_USER, PI_PASS, PARAMIKO_AVAILABLE

if PARAMIKO_AVAILABLE:
    import paramiko

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_DIR = ROOT_DIR / "dataset"
DATASET_DIR.mkdir(parents=True, exist_ok=True)

THAI_MONTHS = ['', 'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']


def is_running_on_pi() -> bool:
    """Check if web manager is executing natively on Raspberry Pi."""
    try:
        return Path(f"/home/{PI_USER}").is_dir() and ROOT_DIR.resolve() == Path(f"/home/{PI_USER}").resolve()
    except Exception:
        return False


def _exec_local(cmd: str) -> tuple:
    """Execute command natively on the Raspberry Pi."""
    try:
        full_cmd = f"echo {PI_PASS} | sudo -S {cmd}" if cmd.startswith("sudo ") else cmd
        p = subprocess.run(["sudo", "bash", "-c", full_cmd], capture_output=True, text=True, timeout=30)
        out = (p.stdout + "\n" + p.stderr).strip()
        return p.returncode, out
    except Exception as e:
        return 1, str(e)


def _exec_remote(ssh, cmd: str) -> tuple:
    """Executes a command on Pi over SSH with sudo password support and waits for clean exit status."""
    full_cmd = f"echo {PI_PASS} | sudo -S {cmd}" if cmd.startswith("sudo ") else cmd
    stdin, stdout, stderr = ssh.exec_command(full_cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    return exit_status, out


def _find_member_dir(member_id: str) -> Optional[Path]:
    """Find member directory with case-insensitive fallback."""
    if not member_id:
        return None
    matched = DATASET_DIR / member_id
    if matched.exists():
        return matched
    for d in DATASET_DIR.iterdir():
        if d.is_dir() and d.name.lower() == member_id.lower():
            return d
    return None


def get_member_faces(member_id: str) -> List[Dict[str, Any]]:
    """Return sorted list of registered face photos for a member."""
    matched_dir = _find_member_dir(member_id)
    if not matched_dir or not matched_dir.exists():
        return []

    files = [f for f in matched_dir.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')]
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    result = []
    for f in files:
        dt = datetime.fromtimestamp(f.stat().st_mtime)
        time_str = f"{dt.day} {THAI_MONTHS[dt.month]} {dt.hour:02d}:{dt.minute:02d} น."
        result.append({
            'filename': f.name,
            'url': f'/dataset/{matched_dir.name}/{f.name}',
            'size_kb': round(f.stat().st_size / 1024, 1),
            'time_str': time_str
        })
    return result


def get_face_summary() -> Dict[str, Dict[str, Any]]:
    """Return photo count and latest avatar url for all configured members."""
    summary = {}
    cfg = load_config()
    for mem_id in cfg.get('members', {}).keys():
        faces = get_member_faces(mem_id)
        summary[mem_id] = {
            'count': len(faces),
            'latest_url': faces[0]['url'] if faces else None
        }
    return summary


def delete_member_face(member_id: str, filename: str) -> bool:
    """Delete face photo locally, on Pi if needed, then trigger AI rebuild and service refresh."""
    matched_dir = _find_member_dir(member_id)
    if matched_dir and matched_dir.exists():
        local_file = matched_dir / filename
        if local_file.is_file():
            try:
                local_file.unlink()
                print(f"[+] Deleted face photo: {local_file}")
            except Exception as e:
                print(f"[!] Error deleting face photo: {e}")

    def _delete_and_rebuild():
        if is_running_on_pi():
            print(f"[*] Rebuilding AI face model locally on Pi after deleting {filename}...")
            st, out = _exec_local("python3 -m smart_rice_cooker.main --rebuild-faces")
            print(f"[+] Local rebuild completed (exit={st}):\n{out}")
            _exec_local("sudo systemctl restart smart-cooker.service")
            print(f"[+] Successfully refreshed smart-cooker.service (Red Standby LED ON)")
            return

        if not PARAMIKO_AVAILABLE:
            return
        pi_ip = get_pi_ip()
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(pi_ip, username=PI_USER, password=PI_PASS, timeout=8)

            _exec_remote(ssh, f"rm -f /home/{PI_USER}/dataset/{member_id}/{filename}")
            _exec_remote(ssh, f"rm -f /home/{PI_USER}/dataset/{member_id.lower()}/{filename}")
            _exec_remote(ssh, f"rm -f /home/{PI_USER}/dataset/{member_id.capitalize()}/{filename}")

            print(f"[*] Rebuilding AI face model on Pi after deleting {filename}...")
            st, out = _exec_remote(ssh, "python3 -m smart_rice_cooker.main --rebuild-faces")
            print(f"[+] Rebuild completed (exit={st}):\n{out}")

            _exec_remote(ssh, "sudo systemctl restart smart-cooker.service")
            ssh.close()
            print(f"[+] Successfully refreshed smart-cooker.service (Red Standby LED ON)")
        except Exception as e:
            print(f"[!] Error deleting remote face on Pi: {e}")

    threading.Thread(target=_delete_and_rebuild, daemon=True).start()
    return True


def delete_member_dataset(member_id: str) -> bool:
    """Delete all local face photos for member, delete on Pi if needed, and rebuild AI model."""
    import shutil
    matched_dir = _find_member_dir(member_id)
    if matched_dir and matched_dir.exists():
        try:
            shutil.rmtree(matched_dir)
            print(f"[+] Deleted dataset directory: {matched_dir}")
        except Exception as e:
            print(f"[!] Error deleting dataset directory: {e}")

    exact_dir = DATASET_DIR / member_id
    if exact_dir.exists():
        try:
            shutil.rmtree(exact_dir)
        except Exception:
            pass

    def _purge_and_rebuild():
        if is_running_on_pi():
            print(f"[*] Rebuilding AI face model locally on Pi after purging {member_id}...")
            st, out = _exec_local("python3 -m smart_rice_cooker.main --rebuild-faces")
            _exec_local("sudo systemctl restart smart-cooker.service")
            print(f"[+] Purged member '{member_id}' dataset locally on Pi and refreshed service (exit={st})")
            return

        if not PARAMIKO_AVAILABLE:
            return
        pi_ip = get_pi_ip()
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(pi_ip, username=PI_USER, password=PI_PASS, timeout=8)

            cmd_rm = f"rm -rf /home/{PI_USER}/dataset/{member_id} /home/{PI_USER}/dataset/{member_id.lower()} /home/{PI_USER}/dataset/{member_id.capitalize()}"
            _exec_remote(ssh, cmd_rm)

            print(f"[*] Rebuilding AI face model on Pi after purging {member_id}...")
            st, out = _exec_remote(ssh, "python3 -m smart_rice_cooker.main --rebuild-faces")
            print(f"[+] Purged member '{member_id}' dataset on Pi and rebuilt AI faces (exit={st}):\n{out}")

            _exec_remote(ssh, "sudo systemctl restart smart-cooker.service")
            ssh.close()
            print(f"[+] Successfully refreshed smart-cooker.service (Red Standby LED ON)")
        except Exception as e:
            print(f"[!] Error purging remote member dataset on Pi: {e}")

    threading.Thread(target=_purge_and_rebuild, daemon=True).start()
    return True


def save_uploaded_face(member_id: str, img_bytes: bytes) -> Optional[Path]:
    """Save uploaded face photo and trigger AI face rebuild."""
    mem_dir = DATASET_DIR / member_id
    mem_dir.mkdir(parents=True, exist_ok=True)
    filename = f"face_{int(time.time()*1000)}.jpg"
    save_file = mem_dir / filename

    with open(save_file, "wb") as f:
        f.write(img_bytes)

    print(f"[+] Saved face image locally: {save_file}")
    threading.Thread(target=_sync_and_rebuild_after_upload, args=(member_id, save_file), daemon=True).start()
    return save_file


def _sync_and_rebuild_after_upload(member_id: str, local_path: Path) -> None:
    """Sync photo to Raspberry Pi if needed and run AI face rebuild."""
    if is_running_on_pi():
        print(f"[*] Running on Pi natively: Rebuilding AI face model for '{member_id}'...")
        st, out = _exec_local("python3 -m smart_rice_cooker.main --rebuild-faces")
        print(f"[+] Local rebuild completed (exit={st}):\n{out}")
        _exec_local("sudo systemctl restart smart-cooker.service")
        print(f"[+] Successfully refreshed smart-cooker.service (Red Standby LED ON)")
        return

    if not PARAMIKO_AVAILABLE:
        return
    pi_ip = get_pi_ip()
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(pi_ip, username=PI_USER, password=PI_PASS, timeout=8)

        sftp = ssh.open_sftp()
        remote_member_dir = f"/home/{PI_USER}/dataset/{member_id}"
        try:
            sftp.stat(remote_member_dir)
        except IOError:
            _exec_remote(ssh, f"mkdir -p {remote_member_dir}")
            time.sleep(0.3)

        remote_file = f"{remote_member_dir}/{local_path.name}"
        sftp.put(str(local_path), remote_file)
        sftp.close()

        print(f"[*] Rebuilding AI face model on Pi for '{member_id}'...")
        st, out = _exec_remote(ssh, "python3 -m smart_rice_cooker.main --rebuild-faces")
        print(f"[+] Rebuild completed (exit={st}):\n{out}")

        _exec_remote(ssh, "sudo systemctl restart smart-cooker.service")
        ssh.close()
        print(f"[+] Successfully refreshed smart-cooker.service (Red Standby LED ON)")
    except Exception as e:
        print(f"[!] Sync photo to Pi error: {e}")


def capture_face_from_pi(member_id: str) -> Optional[str]:
    """Trigger Raspberry Pi camera to capture a photo, save into dataset, and rebuild AI model."""
    if is_running_on_pi():
        # Native Pi execution (e.g. accessed from Mobile Web Browser)
        try:
            print("[*] Local Pi Camera Capture: Stopping smart-cooker.service to free camera...")
            _exec_local("sudo systemctl stop smart-cooker.service")
            time.sleep(1.2)

            p = DATASET_DIR / member_id
            p.mkdir(parents=True, exist_ok=True)

            try:
                import cv2
            except ImportError:
                print("[!] OpenCV cv2 not available")
                _exec_local("sudo systemctl restart smart-cooker.service")
                return None

            cap = None
            for idx in (0, 1, 2):
                try:
                    c = cv2.VideoCapture(idx, cv2.CAP_V4L2)
                    if not c.isOpened():
                        c = cv2.VideoCapture(idx)
                    if c.isOpened():
                        for _ in range(4):
                            ret, frame = c.read()
                        if ret and frame is not None and frame.size > 0:
                            cap = c
                            break
                        c.release()
                except Exception:
                    pass

            captured_name = None
            if cap and cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    captured_name = f"face_{int(time.time()*1000)}.jpg"
                    dest_file = p / captured_name
                    cv2.imwrite(str(dest_file), frame)
                    print(f"[+] Locally captured photo saved: {dest_file}")
                cap.release()

            if captured_name:
                print(f"[*] Rebuilding AI face model locally after camera capture for '{member_id}'...")
                st, out = _exec_local("python3 -m smart_rice_cooker.main --rebuild-faces")
                print(f"[+] Rebuild completed (exit={st}):\n{out}")

            _exec_local("sudo systemctl restart smart-cooker.service")
            print(f"[+] Successfully restarted smart-cooker.service")
            return captured_name
        except Exception as e:
            print(f"[!] Local Pi camera capture error: {e}")
            _exec_local("sudo systemctl restart smart-cooker.service")
            return None

    # Remote PC execution via SSH/SFTP
    if not PARAMIKO_AVAILABLE:
        return None
    pi_ip = get_pi_ip()
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(pi_ip, username=PI_USER, password=PI_PASS, timeout=8)

        # Stop background service with proper sudo password to free camera hardware
        _exec_remote(ssh, "sudo systemctl stop smart-cooker.service")
        time.sleep(1.2)

        py_script = f"""
import cv2
import time
from pathlib import Path

p = Path('/home/{PI_USER}/dataset/{member_id}')
p.mkdir(parents=True, exist_ok=True)

cap = None
for idx in (0, 1, 2):
    try:
        c = cv2.VideoCapture(idx, cv2.CAP_V4L2)
        if not c.isOpened():
            c = cv2.VideoCapture(idx)
        if c.isOpened():
            for _ in range(4):
                ret, frame = c.read()
            if ret and frame is not None and frame.size > 0:
                cap = c
                break
            c.release()
    except Exception:
        pass

if cap and cap.isOpened():
    ret, frame = cap.read()
    if ret and frame is not None:
        filename = f'face_{{int(time.time()*1000)}}.jpg'
        cv2.imwrite(str(p / filename), frame)
        print('CAPTURED_OK:' + filename)
    cap.release()
else:
    print('CAPTURE_FAILED')
"""
        b64 = base64.b64encode(py_script.encode('utf-8')).decode('ascii')
        remote_cmd = f"python3 -c \"import base64; exec(base64.b64decode('{b64}').decode('utf-8'))\""

        stdin, stdout, stderr = ssh.exec_command(remote_cmd)
        out = stdout.read().decode('utf-8', errors='replace')

        if 'CAPTURED_OK:' in out:
            captured_name = out.split('CAPTURED_OK:')[1].strip().split('\n')[0].strip()
            local_mem_dir = DATASET_DIR / member_id
            local_mem_dir.mkdir(parents=True, exist_ok=True)
            local_dest = local_mem_dir / captured_name

            sftp = ssh.open_sftp()
            sftp.get(f"/home/{PI_USER}/dataset/{member_id}/{captured_name}", str(local_dest))
            sftp.close()

            # Rebuild AI model
            print(f"[*] Rebuilding AI face model on Pi after camera capture for '{member_id}'...")
            _exec_remote(ssh, "python3 -m smart_rice_cooker.main --rebuild-faces")

            _exec_remote(ssh, "sudo systemctl restart smart-cooker.service")
            ssh.close()
            return captured_name

        _exec_remote(ssh, "sudo systemctl restart smart-cooker.service")
        ssh.close()
    except Exception as e:
        print(f"[!] Pi camera capture error: {e}")
    return None
