"""
Face dataset and AI recognition service for Smart Rice Cooker.
Manages local face photos, gallery listing, upload, deletion, and AI model rebuild on Raspberry Pi.
"""
import time
import base64
import threading
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
    """Delete face photo locally and remotely on Raspberry Pi, then trigger AI rebuild."""
    matched_dir = _find_member_dir(member_id)
    if matched_dir and matched_dir.exists():
        local_file = matched_dir / filename
        if local_file.is_file():
            try:
                local_file.unlink()
                print(f"[+] Deleted local face: {local_file}")
            except Exception as e:
                print(f"[!] Error deleting local face: {e}")

    def _remote_delete_and_rebuild():
        if not PARAMIKO_AVAILABLE:
            return
        pi_ip = get_pi_ip()
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(pi_ip, username=PI_USER, password=PI_PASS, timeout=8)
            ssh.exec_command(f"rm -f /home/{PI_USER}/dataset/{member_id}/{filename}")
            ssh.exec_command(f"rm -f /home/{PI_USER}/dataset/{member_id.lower()}/{filename}")
            ssh.exec_command(f"rm -f /home/{PI_USER}/dataset/{member_id.capitalize()}/{filename}")
            ssh.exec_command("sudo systemctl stop smart-cooker.service")
            ssh.exec_command("python3 -m smart_rice_cooker.main --rebuild-faces")
            ssh.exec_command("sudo systemctl start smart-cooker.service")
            ssh.close()
            print(f"[+] Deleted {member_id}/{filename} on Pi and rebuilt AI model")
        except Exception as e:
            print(f"[!] Error deleting remote face on Pi: {e}")

    threading.Thread(target=_remote_delete_and_rebuild, daemon=True).start()
    return True


def delete_member_dataset(member_id: str) -> bool:
    """Delete all local face photos for member, delete remotely on Pi, and rebuild AI model."""
    import shutil
    # 1. Local deletion
    matched_dir = _find_member_dir(member_id)
    if matched_dir and matched_dir.exists():
        try:
            shutil.rmtree(matched_dir)
            print(f"[+] Deleted local dataset directory: {matched_dir}")
        except Exception as e:
            print(f"[!] Error deleting local dataset directory: {e}")

    exact_dir = DATASET_DIR / member_id
    if exact_dir.exists():
        try:
            shutil.rmtree(exact_dir)
        except Exception:
            pass

    # 2. Remote deletion and AI rebuild on Raspberry Pi
    def _remote_purge_and_rebuild():
        if not PARAMIKO_AVAILABLE:
            return
        pi_ip = get_pi_ip()
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(pi_ip, username=PI_USER, password=PI_PASS, timeout=8)

            cmd_rm = f"rm -rf /home/{PI_USER}/dataset/{member_id} /home/{PI_USER}/dataset/{member_id.lower()} /home/{PI_USER}/dataset/{member_id.capitalize()}"
            ssh.exec_command(cmd_rm)

            ssh.exec_command("sudo systemctl stop smart-cooker.service")
            time.sleep(0.5)
            stdin, stdout, stderr = ssh.exec_command("python3 -m smart_rice_cooker.main --rebuild-faces")
            exit_status = stdout.channel.recv_exit_status()
            out = stdout.read().decode('utf-8', errors='replace')
            print(f"[+] Purged member '{member_id}' dataset on Pi and rebuilt AI faces (exit={exit_status}):\n{out}")

            ssh.exec_command("sudo systemctl start smart-cooker.service")
            ssh.close()
        except Exception as e:
            print(f"[!] Error purging remote member dataset on Pi: {e}")

    threading.Thread(target=_remote_purge_and_rebuild, daemon=True).start()
    return True


def save_uploaded_face(member_id: str, img_bytes: bytes) -> Optional[Path]:
    """Save uploaded face photo locally and trigger sync to Raspberry Pi."""
    mem_dir = DATASET_DIR / member_id
    mem_dir.mkdir(parents=True, exist_ok=True)
    filename = f"face_{int(time.time()*1000)}.jpg"
    save_file = mem_dir / filename

    with open(save_file, "wb") as f:
        f.write(img_bytes)

    threading.Thread(target=_sync_photo_and_rebuild_pi, args=(member_id, save_file), daemon=True).start()
    return save_file


def _sync_photo_and_rebuild_pi(member_id: str, local_path: Path) -> None:
    """Sync single photo to Raspberry Pi and run AI face rebuild."""
    if not PARAMIKO_AVAILABLE:
        return
    pi_ip = get_pi_ip()
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(pi_ip, username=PI_USER, password=PI_PASS, timeout=8)

        ssh.exec_command("sudo systemctl stop smart-cooker.service")
        time.sleep(0.5)

        sftp = ssh.open_sftp()
        remote_member_dir = f"/home/{PI_USER}/dataset/{member_id}"
        try:
            sftp.stat(remote_member_dir)
        except IOError:
            ssh.exec_command(f"mkdir -p {remote_member_dir}")
            time.sleep(0.3)

        remote_file = f"{remote_member_dir}/{local_path.name}"
        sftp.put(str(local_path), remote_file)
        sftp.close()

        print(f"[*] Rebuilding AI face model on Pi for '{member_id}'...")
        stdin, stdout, stderr = ssh.exec_command("python3 -m smart_rice_cooker.main --rebuild-faces")
        out = stdout.read().decode('utf-8', errors='replace')
        print(f"[+] Rebuild completed:\n{out}")

        ssh.exec_command("sudo systemctl start smart-cooker.service")
        ssh.close()
    except Exception as e:
        print(f"[!] Sync photo to Pi error: {e}")


def capture_face_from_pi(member_id: str) -> Optional[str]:
    """Trigger Raspberry Pi camera to capture a photo with auto-probing, then download to local dataset."""
    if not PARAMIKO_AVAILABLE:
        return None
    pi_ip = get_pi_ip()
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(pi_ip, username=PI_USER, password=PI_PASS, timeout=8)
        
        # Stop background service to free camera hardware
        ssh.exec_command("sudo systemctl stop smart-cooker.service")
        time.sleep(1.0)

        py_script = f"""
import cv2
import time
from pathlib import Path

p = Path('/home/pi/dataset/{member_id}')
p.mkdir(parents=True, exist_ok=True)

cap = None
for idx in (1, 0, 2):
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
            sftp.get(f"/home/pi/dataset/{member_id}/{captured_name}", str(local_dest))
            sftp.close()

            # Rebuild AI model
            _, rb_out, _ = ssh.exec_command("python3 -m smart_rice_cooker.main --rebuild-faces")
            rb_out.channel.recv_exit_status()

            ssh.exec_command("sudo systemctl start smart-cooker.service")
            ssh.close()
            return captured_name

        ssh.exec_command("sudo systemctl start smart-cooker.service")
        ssh.close()
    except Exception as e:
        print(f"[!] Pi camera capture error: {e}")
    return None
