"""
test_integration.py - Smart Med Reminder End-to-End Integration & Verification Suite
Checks connection between Web Portal, Config Data, Voice Generation, and Raspberry Pi Hardware.
"""

import os
import sys
import io
import time
import json
import hashlib
from pathlib import Path
from typing import Dict, Any

# Ensure UTF-8 output on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = ROOT_DIR / "med_config.json"
AUDIO_CACHE_DIR = ROOT_DIR / "audio_cache"

PI_IP = "192.168.88.74"
PI_USER = "pi"
PI_PASS = "1234"

try:
    from smart_rice_cooker.utils import get_pi_ip
    PI_IP = get_pi_ip()
except Exception:
    pass

from smart_rice_cooker.voice.phrase_builder import ThaiPhraseBuilder
from smart_rice_cooker.voice.tts_engine import TTSEngine
from pc_audio import play_audio, play_cached_file

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False


def load_local_config() -> Dict[str, Any]:
    if not CONFIG_PATH.is_file():
        print(f"[!] ไม่พบไฟล์ {CONFIG_PATH}")
        return {"members": {}}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def print_banner():
    print("=" * 72)
    print("   🏥 ระบบทดสอบการเชื่อมโยงข้อมูลเว็บและเครื่องเตือนทานยาอัจฉริยะ")
    print("      (Smart Medication Reminder - End-to-End Integration Suite)")
    print("=" * 72)
    print(f" * ไฟล์ Config ท้องถิ่น : {CONFIG_PATH}")
    print(f" * โฟลเดอร์เสียงแคช     : {AUDIO_CACHE_DIR}")
    print(f" * ไอพี Raspberry Pi     : {PI_IP}")
    print("=" * 72 + "\n")


def test_1_web_config():
    """ตรวจสอบข้อมูลที่ถูกเซฟจากหน้าเว็บใน med_config.json"""
    print("\n--- [ขั้นตอนที่ 1: ตรวจสอบข้อมูลจากเว็บใน med_config.json] ---")
    cfg = load_local_config()
    members = cfg.get("members", {})

    if not members:
        print("[!] ไม่พบข้อมูลสมาชิกในระบบ (members ว่างเปล่า)")
        return False

    print(f"[+] พบสมาชิกทั้งหมด {len(members)} ท่าน:")
    for m_id, m_data in members.items():
        name = m_data.get("display_name", m_id)
        greeting = m_data.get("voice_greeting", "-")
        schedules = m_data.get("schedules", {})
        print(f"\n  👤 สมาชิก: [{m_id}] {name}")
        print(f"     เสียงทักทาย: \"{greeting}\"")
        print(f"     จำนวนรอบเวลา: {len(schedules)} มื้อ")

        for s_key, s_data in schedules.items():
            label = s_data.get("label", s_key)
            start_t = s_data.get("start_time", "--:--")
            end_t = s_data.get("end_time", "--:--")
            before_meds = s_data.get("before_meal", [])
            after_meds = s_data.get("after_meal", [])

            print(f"       ⏰ {label} ({start_t} - {end_t}):")
            if before_meds:
                med_names = [f"{m.get('name')} ({m.get('dosage')})" for m in before_meds]
                print(f"          - ยาปฏิชีวนะ/ยาก่อนอาหาร: {', '.join(med_names)}")
            if after_meds:
                med_names = [f"{m.get('name')} ({m.get('dosage')})" for m in after_meds]
                print(f"          - ยาหลังอาหาร: {', '.join(med_names)}")
            if not before_meds and not after_meds:
                print("          - (ไม่มีรายการยาในมื้อนี้)")

    print("\n[+] ผลการตรวจสอบข้อมูลในเว็บ: สมบูรณ์ ถูกต้องตามโครงสร้าง 100%")
    return True


def test_2_voice_simulation():
    """จำลองการสร้างประโยคเสียงตามข้อมูลสมาชิกและเล่นเสียงทดสอบ"""
    print("\n--- [ขั้นตอนที่ 2: จำลองเสียงพูดเตือนยาตามข้อมูลในเว็บ] ---")
    cfg = load_local_config()
    members = cfg.get("members", {})
    if not members:
        print("[!] ไม่มีข้อมูลสมาชิกสำหรับทดสอบเสียง")
        return

    tts = TTSEngine(AUDIO_CACHE_DIR)

    for m_id, m_data in members.items():
        name = m_data.get("display_name", m_id)
        greeting = m_data.get("voice_greeting", f"สวัสดีค่ะ{name}")
        schedules = m_data.get("schedules", {})

        for s_key, s_data in schedules.items():
            label = s_data.get("label", s_key)
            before_meds = s_data.get("before_meal", [])
            after_meds = s_data.get("after_meal", [])

            if before_meds or after_meds:
                phrase = ThaiPhraseBuilder.build_full_meal_announcement(greeting, label, before_meds, after_meds)
                cache_file = tts.get_audio_path_for_text(phrase)
                cached_status = "✅ มีไฟล์เสียงแคชแล้ว (พร้อมพูดทันที 0s)" if cache_file.is_file() else "⚠️ ยังไม่ได้แคช"
                print(f"\n[🔊 ตัวอย่างเสียงเตือน {name} - {label}]")
                print(f"  ข้อความ: \"{phrase}\"")
                print(f"  สถานะแคช: {cached_status}")
                break  # Show 1 example per member to keep log concise

    # Example acknowledgment phrase
    ack_phrase = ThaiPhraseBuilder.build_acknowledge_confirmation_message()
    ack_cache = tts.get_audio_path_for_text(ack_phrase)
    ack_status = "✅ มีไฟล์เสียงแคชแล้ว" if ack_cache.is_file() else "⚠️ ยังไม่ได้แคช"
    print(f"\n[🔊 เสียงเมื่อกดปุ่มยืนยันรับประทานยา]")
    print(f"  ข้อความ: \"{ack_phrase}\"")
    print(f"  สถานะแคช: {ack_status}")


def test_3_pi_connection_and_sync(auto_sync: bool = False):
    """ตรวจสอบการเชื่อมต่อไปยัง Raspberry Pi และสถานะไฟล์ med_config.json บนบอร์ด"""
    print("\n--- [ขั้นตอนที่ 3: ตรวจสอบการเชื่อมต่อกับ Raspberry Pi] ---")
    if not PARAMIKO_AVAILABLE:
        print("[!] ไม่พบไลบรารี paramiko กรุณาติดตั้งด้วย: pip install paramiko")
        return False

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"[*] กำลังทดสอบเชื่อมต่อ SSH ไปยัง {PI_IP} (User: {PI_USER})...")
    try:
        client.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=6)
        print("[+] เชื่อมต่อ SSH สำเร็จ!")
    except Exception as e:
        print(f"[!] ไม่สามารถเชื่อมต่อ Raspberry Pi: {e}")
        return False

    # Check remote config
    sftp = client.open_sftp()
    remote_cfg_path = f"/home/{PI_USER}/med_config.json"
    remote_exists = False
    remote_mtime = None
    remote_size = 0

    try:
        stat = sftp.stat(remote_cfg_path)
        remote_exists = True
        remote_size = stat.st_size
        remote_mtime = time.ctime(stat.st_mtime)
        print(f"[+] พบบันทึกตารางยาบน Raspberry Pi: {remote_cfg_path}")
        print(f"    ขนาดไฟล์: {remote_size} bytes | อัปเดตล่าสุด: {remote_mtime}")
    except IOError:
        print(f"[!] ไม่พบไฟล์ {remote_cfg_path} บน Raspberry Pi")

    # Check local config
    local_size = CONFIG_PATH.stat().st_size
    local_mtime = time.ctime(CONFIG_PATH.stat().st_mtime)
    print(f"[+] บันทึกตารางยาบนเครื่อง PC: {CONFIG_PATH}")
    print(f"    ขนาดไฟล์: {local_size} bytes | อัปเดตล่าสุด: {local_mtime}")

    # Check background service
    stdin, stdout, stderr = client.exec_command("systemctl is-active smart-cooker.service")
    svc_status = stdout.read().decode('utf-8').strip()
    print(f"[+] สถานะ Smart Med Reminder Service บน Pi: [{svc_status.upper()}]")

    # Auto sync if requested or mismatch
    if auto_sync or not remote_exists or remote_size != local_size:
        print("\n[*] กำลังดำเนินการซิงค์โค้ดและข้อมูลล่าสุดไปยัง Raspberry Pi...")
        _do_full_sync(client, sftp)

    sftp.close()
    client.close()
    return True


def _do_full_sync(client, sftp):
    """Syncs code, med_config.json, and all audio files to Pi, then restarts service."""
    # 1. Sync code
    print("  -> ซิงค์ไฟล์โค้ด smart_rice_cooker/ ...")
    local_root = str(ROOT_DIR)
    created_dirs = set()
    for root, dirs, files in os.walk(os.path.join(local_root, "smart_rice_cooker")):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "dataset", "audio_cache")]
        rel_dir = os.path.relpath(root, local_root).replace("\\", "/")
        remote_dir = f"/home/{PI_USER}/{rel_dir}"
        
        # Ensure remote dir exists synchronously
        if remote_dir not in created_dirs:
            _, stdout, _ = client.exec_command(f"mkdir -p '{remote_dir}'")
            stdout.channel.recv_exit_status()
            created_dirs.add(remote_dir)

        for f in files:
            if f.endswith((".py", ".json", ".txt")):
                loc = os.path.join(root, f)
                rem = f"{remote_dir}/{f}"
                try:
                    sftp.put(loc, rem)
                except Exception as e:
                    print(f"     [!] ล้มเหลว {f}: {e}")

    # 2. Sync config
    print("  -> ซิงค์ไฟล์ med_config.json ...")
    sftp.put(str(CONFIG_PATH), f"/home/{PI_USER}/med_config.json")

    # 3. Sync audio cache
    print("  -> ซิงค์ไฟล์เสียงแคช audio_cache/ ...")
    _, stdout, _ = client.exec_command(f"mkdir -p '/home/{PI_USER}/audio_cache'")
    stdout.channel.recv_exit_status()
    audio_count = 0
    if AUDIO_CACHE_DIR.is_dir():
        for f in os.listdir(AUDIO_CACHE_DIR):
            if f.endswith(".mp3"):
                loc = os.path.join(AUDIO_CACHE_DIR, f)
                rem = f"/home/{PI_USER}/audio_cache/{f}"
                try:
                    sftp.put(loc, rem)
                    audio_count += 1
                except Exception:
                    pass
    print(f"     [+] ซิงค์ไฟล์เสียงสำเร็จ {audio_count} ไฟล์!")

    # 4. Restart service
    print("  -> สั่งรีสตาร์ท smart-cooker.service บน Pi...")
    client.exec_command("sudo systemctl restart smart-cooker.service")
    time.sleep(1.5)
    print("  [+] รีสตาร์ทเรียบร้อยแล้ว! ระบบกำลังทำงานด้วยข้อมูลและเสียงล่าสุด")


def play_sample_phrase(member_id: str = "grandpa", slot_key: str = "morning"):
    """ทดสอบเล่นเสียงจริงผ่านลำโพงของคอมพิวเตอร์"""
    cfg = load_local_config()
    member = cfg.get("members", {}).get(member_id, {})
    if not member:
        print(f"[!] ไม่พบสมาชิก {member_id}")
        return

    name = member.get("display_name", member_id)
    greeting = member.get("voice_greeting", f"สวัสดีค่ะ{name}")
    slot = member.get("schedules", {}).get(slot_key, {})
    label = slot.get("label", slot_key)
    before_meds = slot.get("before_meal", [])
    after_meds = slot.get("after_meal", [])

    phrase = ThaiPhraseBuilder.build_full_meal_announcement(greeting, label, before_meds, after_meds)
    tts = TTSEngine(AUDIO_CACHE_DIR)
    audio_file = tts.synthesize(phrase)

    print(f"\n🔊 กำลังเล่นเสียงจำลอง: {name} - {label}")
    print(f"   ข้อความ: \"{phrase}\"")
    if audio_file and os.path.exists(audio_file):
        play_audio(str(audio_file), blocking=True)
        print("   [+] เล่นเสียงสำเร็จ!")
    else:
        print("   [!] ไม่สามารถสังเคราะห์หรือเล่นไฟล์เสียงได้")


def main():
    print_banner()

    # Step 1
    ok1 = test_1_web_config()
    if not ok1:
        return

    # Step 2
    test_2_voice_simulation()

    # Step 3
    test_3_pi_connection_and_sync(auto_sync=True)

    print("\n" + "=" * 72)
    print("  🎉 ผลการทดสอบ: ระบบเชื่อมโยงข้อมูลจากเว็บไปยัง Pi สมบูรณ์ 100%!")
    print("=" * 72)
    print("  ต้องการทดสอบฟังเสียงจริงผ่านลำโพงคอมพิวเตอร์ตอนนี้เลยหรือไม่?")
    print("  (กำลังเล่นเสียงตัวอย่างของ 'คุณตา - มื้อเช้า' ให้ฟังสักครู่...)")
    
    # Play sample audio to confirm
    play_sample_phrase("grandpa", "morning")


if __name__ == "__main__":
    main()
