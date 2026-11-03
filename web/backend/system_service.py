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


def sync_system_time(iso_time_str: str) -> Tuple[bool, str]:
    """
    Synchronizes Raspberry Pi system clock to browser/PC time without NTP dependency.
    Format: 'YYYY-MM-DD HH:MM:SS'
    """
    try:
        clean_time = iso_time_str.replace("T", " ")[:19]
        cmd = f"sudo timedatectl set-ntp false 2>/dev/null; sudo date -s '{clean_time}'"
        ok, out = _exec_pi_cmd(cmd, timeout=8)
        if ok:
            return (True, f"ซิงค์เวลาบอร์ดเป็น {clean_time} เรียบร้อยแล้ว")
        return (False, f"ไม่สามารถตั้งเวลาได้: {out}")
    except Exception as e:
        return (False, f"ข้อผิดพลาด: {str(e)}")


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
    cmd = (
        f"amixer -c Headphones sset PCM {val}% unmute 2>/dev/null; "
        f"amixer -c 2 sset PCM {val}% unmute 2>/dev/null; "
        f"amixer sset PCM {val}% unmute 2>/dev/null; "
        f"sudo alsactl store 2>/dev/null"
    )
    ok, out = _exec_pi_cmd(cmd, timeout=5)
    return (ok, f"ตั้งค่าระดับเสียงเป็น {val}% เรียบร้อย")


def play_test_sound() -> Tuple[bool, str]:
    """Plays pleasant test tone or speech through the Pi speaker."""
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
    Falls back to local simulation on PC if Pi is offline.
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
        # Remote PC: attempt write via SSH
        if PARAMIKO_AVAILABLE:
            try:
                ip = get_pi_ip()
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username=PI_USER, password=PI_PASS, timeout=4)
                sftp = ssh.open_sftp()
                with sftp.open("/dev/shm/demo_trigger.json", "w") as f:
                    f.write(payload)
                sftp.close()
                ssh.close()
                return (True, f"เริ่มจำลองสถานการณ์ '{scenario}' บนกล่องแล้ว")
            except Exception:
                pass

        # Standalone fallback on PC when Pi is offline
        try:
            from smart_rice_cooker.medicine.adherence_tracker import AdherenceTracker
            from smart_rice_cooker.config import settings
            from smart_rice_cooker.vision.snapshot_manager import save_adherence_snapshot
            from smart_rice_cooker.voice.phrase_builder import ThaiPhraseBuilder
            from web.backend.config_service import load_config
            import cv2

            cfg = load_config()
            member_info = cfg.get("members", {}).get(member_id, {})
            display_name = member_info.get("display_name", member_id)
            greeting = member_info.get("voice_greeting", f"สวัสดีค่ะ{display_name}")
            schedules = member_info.get("schedules", {})
            slot_key = "morning" if "morning" in schedules else (list(schedules.keys())[0] if schedules else "morning")
            slot_data = schedules.get(slot_key, {})
            slot_label = slot_data.get("label", "มื้อเช้า")
            before_meds = slot_data.get("before_meal", [])
            after_meds = slot_data.get("after_meal", [])

            msg = ThaiPhraseBuilder.build_full_meal_announcement(greeting, slot_label, before_meds, after_meds)

            demo_snapshot = None
            dataset_member_dir = settings.DATASET_DIR / member_id
            if dataset_member_dir.is_dir():
                photos = list(dataset_member_dir.glob("*.jpg"))
                if photos:
                    frame = cv2.imread(str(photos[0]))
                    demo_snapshot = save_adherence_snapshot(frame, None, member_id, slot_key, settings.SNAPSHOTS_DIR)

            tracker = AdherenceTracker()
            tracker.record_acknowledgement(member_id, slot_key, spoken_message=msg, snapshot_file=demo_snapshot)
            return (True, f"จำลองสถานการณ์ '{scenario}' สำเร็จ (บันทึกภาพ WebP และเสียงเตือนแล้ว)")
        except Exception as ex:
            return (False, f"การจำลองสถานการณ์ล้มเหลว: {ex}")


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


def get_sensor_distance() -> Dict[str, Any]:
    """
    Returns current ultrasonic threshold and live distance measurement.
    Reads from /dev/shm/ultrasonic_distance.json or med_config.json.
    """
    threshold_cm = 45.0
    live_dist = 150.0
    is_present = False
    fault = False

    # 1. Read configured threshold from med_config.json
    try:
        from web.backend.config_service import load_config
        cfg = load_config()
        sys_cfg = cfg.get("system_settings", {})
        threshold_cm = float(sys_cfg.get("distance_trigger_cm", 45.0))
    except Exception:
        pass

    # 2. Try to read live distance state from /dev/shm/ultrasonic_distance.json
    shm_data = None
    if is_running_on_pi():
        shm_file = Path("/dev/shm/ultrasonic_distance.json")
        if shm_file.is_file():
            try:
                shm_data = json.loads(shm_file.read_text(encoding="utf-8"))
            except Exception:
                pass
    else:
        # Remote PC: read via SSH/SFTP
        if PARAMIKO_AVAILABLE:
            try:
                ip = get_pi_ip()
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username=PI_USER, password=PI_PASS, timeout=3)
                sftp = ssh.open_sftp()
                try:
                    with sftp.open("/dev/shm/ultrasonic_distance.json", "r") as f:
                        shm_data = json.load(f)
                except Exception:
                    pass
                sftp.close()
                ssh.close()
            except Exception:
                pass

    if shm_data and isinstance(shm_data, dict):
        live_dist = shm_data.get("distance_cm", live_dist)
        threshold_cm = shm_data.get("threshold_cm", threshold_cm)
        is_present = shm_data.get("is_person_present", is_present)
        fault = shm_data.get("hardware_fault", fault)

    return {
        "success": True,
        "threshold_cm": round(threshold_cm, 1),
        "live_distance_cm": round(live_dist, 1),
        "is_person_present": is_present,
        "hardware_fault": fault
    }


def set_sensor_distance(distance_cm: float) -> Tuple[bool, str]:
    """
    Sets ultrasonic detection threshold in cm (20-150 cm).
    Persists to med_config.json and sends dynamic update to /dev/shm/ultrasonic_config.json.
    """
    try:
        val = max(20.0, min(150.0, float(distance_cm)))
        from web.backend.config_service import load_config, save_config
        cfg = load_config()
        if "system_settings" not in cfg:
            cfg["system_settings"] = {}
        cfg["system_settings"]["distance_trigger_cm"] = val
        save_config(cfg)

        # Notify running service immediately via /dev/shm/ultrasonic_config.json
        payload = json.dumps({"distance_trigger_cm": val})
        if is_running_on_pi():
            try:
                Path("/dev/shm/ultrasonic_config.json").write_text(payload, encoding="utf-8")
            except Exception:
                pass
        else:
            if PARAMIKO_AVAILABLE:
                try:
                    ip = get_pi_ip()
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(ip, username=PI_USER, password=PI_PASS, timeout=4)
                    sftp = ssh.open_sftp()
                    with sftp.open("/dev/shm/ultrasonic_config.json", "w") as f:
                        f.write(payload)
                    sftp.close()
                    ssh.close()
                except Exception:
                    pass

        return (True, f"ตั้งค่าระยะตรวจจับอัลตราโซนิกเป็น {val:.0f} ซม. เรียบร้อย")
    except Exception as e:
        return (False, f"เกิดข้อผิดพลาด: {str(e)}")
