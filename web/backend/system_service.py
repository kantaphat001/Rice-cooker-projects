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
import threading
import time
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


def safe_shutdown_pi(reboot: bool = False) -> Tuple[bool, str]:
    """
    1-Click Safe Shutdown / Reboot for Raspberry Pi Companion Box.
    Properly stops services, turns off camera, turns off all LEDs,
    turns off cooling fan relay (GPIO 18), syncs disks, and powers off safely.
    Supports native execution on Pi or remote SSH execution from PC.
    """
    action_text = "รีสตาร์ตเครื่อง (Reboot)" if reboot else "ปิดเครื่องอย่างปลอดภัย (Safe Shutdown)"
    power_cmd = "systemctl reboot" if reboot else "systemctl poweroff"

    if is_running_on_pi():
        try:
            logger.info(f"[Power] Native execution on Pi: {action_text}")

            # 1. Hardware LEDs & Fan Relay Shutdown
            try:
                from smart_rice_cooker.config import settings
                led_pins = (settings.PIN_LED_RED, settings.PIN_LED_YELLOW, settings.PIN_LED_GREEN)
                fan_pin = settings.PIN_FAN_RELAY
                fan_active_low = settings.FAN_RELAY_ACTIVE_LOW
            except Exception:
                led_pins = (17, 27, 22)
                fan_pin = 18
                fan_active_low = False

            # Extinguish LEDs
            try:
                from gpiozero import LED
                for p in led_pins:
                    try:
                        LED(p).off()
                    except Exception:
                        pass
            except Exception:
                pass

            # Turn off Cooling Fan Relay
            try:
                from gpiozero import OutputDevice
                fan = OutputDevice(fan_pin, active_high=not fan_active_low)
                fan.off()
            except Exception:
                pass

            # Fast hardware level override via pinctrl (standard in Raspberry Pi OS Bookworm)
            try:
                pins_csv = ",".join(str(p) for p in led_pins)
                subprocess.run(f"echo {PI_PASS} | sudo -S pinctrl set {pins_csv} op dl 2>/dev/null", shell=True, timeout=2)
                fan_level = "dh" if fan_active_low else "dl"
                subprocess.run(f"echo {PI_PASS} | sudo -S pinctrl set {fan_pin} op {fan_level} 2>/dev/null", shell=True, timeout=2)
            except Exception:
                pass

            # 2. Stop smart-cooker service (releases camera /dev/video0 and terminates detection threads)
            subprocess.run(f"echo {PI_PASS} | sudo -S systemctl stop smart-cooker.service 2>/dev/null", shell=True, timeout=5)

            # 3. Flush disk writes
            subprocess.run(f"echo {PI_PASS} | sudo -S sync", shell=True, timeout=3)

            # 4. Schedule delayed poweroff/reboot so HTTP JSON response is cleanly delivered to browser first
            def _delayed_power():
                time.sleep(1.5)
                subprocess.run(f"echo {PI_PASS} | sudo -S {power_cmd}", shell=True)

            t = threading.Thread(target=_delayed_power, daemon=False)
            t.start()

            msg = (
                "ส่งคำสั่งรีบูต Raspberry Pi เรียบร้อยแล้ว ระบบจะเริ่มใหม่ใน 20-30 วินาที"
                if reboot else
                "ปิดเครื่องสำเร็จ! ระบบตัดไฟหน้ากล้อง ไฟ LED และพัดลมระบายความร้อนเรียบร้อยแล้ว บอร์ดจะดับลงใน 5 วินาที สามารถถอดปลั๊กได้อย่างปลอดภัย 100%"
            )
            return (True, msg)

        except Exception as e:
            logger.error(f"[Power] Native shutdown error: {e}")
            return (False, f"เกิดข้อผิดพลาดในการสั่งปิดเครื่องบนบอร์ด: {str(e)}")

    else:
        # Remote execution from PC via SSH
        if not PARAMIKO_AVAILABLE:
            return (False, "Paramiko ไม่พร้อมใช้งานบนคอมพิวเตอร์ ไม่สามารถเชื่อมต่อไปยังบอร์ดได้")

        # Discover candidate IPs
        target_ips = []
        primary_ip = get_pi_ip()
        if primary_ip and primary_ip not in target_ips:
            target_ips.append(primary_ip)

        cfg_file = ROOT_DIR / "config_ip.txt"
        if cfg_file.exists():
            try:
                cfg_ip = cfg_file.read_text(encoding="utf-8").strip()
                if cfg_ip and cfg_ip not in target_ips:
                    target_ips.append(cfg_ip)
            except Exception:
                pass

        for fallback_ip in ["10.57.215.17", "192.168.137.102", "172.20.3.37"]:
            if fallback_ip not in target_ips:
                target_ips.append(fallback_ip)

        client = None
        connected_ip = None
        last_error = ""

        for candidate_ip in target_ips:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(candidate_ip, port=22, username=PI_USER, password=PI_PASS, timeout=3, banner_timeout=5, auth_timeout=5)
                client = ssh
                connected_ip = candidate_ip
                break
            except Exception as e:
                last_error = str(e)

        if not client:
            cand_str = ", ".join(target_ips[:3])
            return (False, f"ไม่สามารถเชื่อมต่อไปยัง Raspberry Pi (ลอง IP: {cand_str}): {last_error or 'ไม่ตอบสนอง'}")

        try:
            # 1. Stop service
            client.exec_command(f"echo {PI_PASS} | sudo -S systemctl stop smart-cooker.service 2>/dev/null", timeout=6)
            # 2. Extinguish LEDs and turn off fan relay
            client.exec_command(
                f"echo {PI_PASS} | sudo -S python3 -c \""
                f"try:\n"
                f" from gpiozero import LED, OutputDevice\n"
                f" [LED(p).off() for p in (17, 27, 22)]\n"
                f" OutputDevice(18).off()\n"
                f"except Exception:\n"
                f" pass\n"
                f"\" 2>/dev/null; "
                f"echo {PI_PASS} | sudo -S pinctrl set 17,27,22,18 op dl 2>/dev/null",
                timeout=6
            )
            # 3. Sync disk
            client.exec_command(f"echo {PI_PASS} | sudo -S sync", timeout=4)
            # 4. Trigger delayed poweroff/reboot
            client.exec_command(f"nohup bash -c 'sleep 1.5 && echo {PI_PASS} | sudo -S {power_cmd}' >/dev/null 2>&1 &", timeout=3)
            time.sleep(0.5)
            client.close()

            msg = (
                f"ส่งคำสั่งรีบูตไปยังบอร์ด {connected_ip} เรียบร้อยแล้ว บอร์ดจะเริ่มใหม่ใน 20-30 วินาที"
                if reboot else
                f"ส่งคำสั่งปิดเครื่องไปยังบอร์ด {connected_ip} สำเร็จ! ตัดไฟหน้ากล้อง พัดลม และไฟ LED เรียบร้อยแล้ว บอร์ดจะดับลงใน 5 วินาที สามารถถอดปลั๊กได้อย่างปลอดภัย 100%"
            )
            return (True, msg)

        except Exception as e:
            if client:
                try:
                    client.close()
                except Exception:
                    pass
            return (False, f"เกิดข้อผิดพลาดขณะส่งคำสั่งปิดเครื่อง: {str(e)}")

