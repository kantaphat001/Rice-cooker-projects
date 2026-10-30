"""
system_service.py - System & Hardware Controls for Smart Rice Cooker
Provides Time Synchronization, Volume Management, Speaker Testing,
Adherence History, and Demo Simulation triggers.
Supports Dual-Mode:
- Native execution on Raspberry Pi via subprocess / /dev/shm
- Remote execution from PC via SSH / SFTP
"""

import os
import json
import socket
import subprocess
import logging
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from web.backend.network_utils import is_running_on_pi, get_pi_ip

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PI_USER = "pi"
PI_PASS = "1234"

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False


def _exec_pi_cmd(cmd: str, timeout: int = 15) -> Tuple[bool, str]:
    """Execute command either locally on Pi or remotely via SSH."""
    if is_running_on_pi():
        try:
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate(input=f"{PI_PASS}\n", timeout=timeout)
            return (proc.returncode == 0, stdout.strip() or stderr.strip())
        except Exception as e:
            return (False, str(e))
    else:
        if not PARAMIKO_AVAILABLE:
            return (False, "Paramiko not available on PC")
        ssh = None
        try:
            ip = get_pi_ip()
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=PI_USER, password=PI_PASS, timeout=5)
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
            if "sudo -S" in cmd:
                stdin.write(f"{PI_PASS}\n")
                stdin.flush()
            out = stdout.read().decode('utf-8', errors='replace').strip()
            err = stderr.read().decode('utf-8', errors='replace').strip()
            return (True, out or err)
        except Exception as e:
            return (False, str(e))
        finally:
            if ssh:
                try:
                    ssh.close()
                except Exception:
                    pass


def sync_system_time(time_str: str) -> Tuple[bool, str]:
    """
    Syncs Raspberry Pi system clock to the given datetime string (YYYY-MM-DD HH:MM:SS).
    Works completely offline without NTP.
    """
    cmd = f'echo 1234 | sudo -S date -s "{time_str}"'
    ok, out = _exec_pi_cmd(cmd, timeout=10)
    if ok:
        # Also sync to hardware clock if available
        _exec_pi_cmd("echo 1234 | sudo -S hwclock -w", timeout=5)
        return (True, f"ซิงค์เวลาเป็น {time_str} สำเร็จ")
    return (False, out or "ไม่สามารถซิงค์เวลาได้")


def get_system_volume() -> int:
    """Gets current PCM volume percentage (0-100)."""
    ok, out = _exec_pi_cmd("amixer get PCM", timeout=5)
    if ok and out:
        import re
        m = re.search(r'\[(\d+)%\]', out)
        if m:
            return int(m.group(1))
    return 80


def set_system_volume(percent: int) -> Tuple[bool, str]:
    """Sets system PCM volume (0-100%)."""
    val = max(0, min(100, int(percent)))
    cmd = f"amixer set PCM {val}%"
    ok, out = _exec_pi_cmd(cmd, timeout=5)
    return (ok, f"ตั้งค่าระดับเสียงเป็น {val}% เรียบร้อย")


def play_test_sound() -> Tuple[bool, str]:
    """Plays pleasant test tone or speech through the Pi speaker."""
    # Try using mpg123 with existing speech/chime or python speaker ping
    script = (
        'python3 -c "'
        'import os;'
        'cmd = \'mpg123 -q /home/pi/audio_cache/*.mp3 2>/dev/null || aplay /usr/share/sounds/alsa/Front_Center.wav 2>/dev/null\';'
        'os.system(cmd)'
        '"'
    )
    ok, out = _exec_pi_cmd(script, timeout=8)
    return (True, "ส่งสัญญาณทดสอบเสียงเรียบร้อย")


def trigger_demo_simulation(scenario: str, member_id: str) -> Tuple[bool, str]:
    """
    Triggers simulated presentation scenario on Raspberry Pi hardware.
    Writes trigger payload to /dev/shm/demo_trigger.json
    """
    payload = json.dumps({"scenario": scenario, "member_id": member_id}, ensure_ascii=False)
    if is_running_on_pi():
        try:
            trigger_path = Path("/dev/shm/demo_trigger.json")
            trigger_path.write_text(payload, encoding="utf-8")
            return (True, f"เริ่มจำลองสถานการณ์ '{scenario}' บนกล่องแล้ว")
        except Exception as e:
            return (False, str(e))
    else:
        # Remote PC: write via SSH
        if not PARAMIKO_AVAILABLE:
            return (False, "Paramiko not available on PC")
        try:
            ip = get_pi_ip()
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=PI_USER, password=PI_PASS, timeout=5)
            sftp = ssh.open_sftp()
            with sftp.open("/dev/shm/demo_trigger.json", "w") as f:
                f.write(payload)
            sftp.close()
            ssh.close()
            return (True, f"เริ่มจำลองสถานการณ์ '{scenario}' บนกล่องแล้ว")
        except Exception as e:
            return (False, str(e))


def get_adherence_history() -> Dict[str, Any]:
    """Returns all adherence history records."""
    try:
        from smart_rice_cooker.medicine.adherence_tracker import AdherenceTracker
        tracker = AdherenceTracker()
        return tracker.get_all_records()
    except Exception as e:
        logger.error(f"[History] Error getting history: {e}")
        return {}


def clear_adherence_history() -> bool:
    """Clears all adherence history records for clean demo start."""
    try:
        from smart_rice_cooker.medicine.adherence_tracker import AdherenceTracker
        tracker = AdherenceTracker()
        tracker.clear_all_records()
        return True
    except Exception as e:
        logger.error(f"[History] Error clearing history: {e}")
        return False
