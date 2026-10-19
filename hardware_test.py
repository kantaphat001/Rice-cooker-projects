"""
hardware_test.py - Windows Helper to run hardware tests on Pi (Button-Free 2026 Edition)
"""

import sys
import os
import time
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import paramiko
except ImportError:
    print("[!] Error: paramiko is required. Run: pip install paramiko")
    sys.exit(1)

import re
from pc_audio import play_cached_file

PI_IP = "192.168.88.74"
PI_USER = "pi"
PI_PASS = "1234"

def run_remote_python(ssh, code: str):
    transport = ssh.get_transport()
    channel = transport.open_session()
    channel.get_pty()
    channel.exec_command(f"python3 -c \"{code}\"")
    captured = []
    while True:
        if channel.recv_ready():
            out = channel.recv(4096).decode('utf-8', errors='replace')
            sys.stdout.write(out)
            sys.stdout.flush()
            captured.append(out)
        if channel.recv_stderr_ready():
            err = channel.recv_stderr(4096).decode('utf-8', errors='replace')
            sys.stderr.write(err)
            sys.stderr.flush()
        if channel.exit_status_ready():
            break
        time.sleep(0.05)
    channel.close()
    return "".join(captured)

def pause_service_if_active(ssh):
    stdin, stdout, stderr = ssh.exec_command("systemctl is-active smart-cooker.service")
    status = stdout.read().decode('utf-8', errors='replace').strip()
    if status == "active":
        print("[*] กำลังหยุด smart-cooker.service ชั่วคราวเพื่อปลดล็อก GPIO & อุปกรณ์ฮาร์ดแวร์...")
        ssh.exec_command("sudo systemctl stop smart-cooker.service")
        time.sleep(1.0)
        return True
    return False

def resume_service(ssh):
    print("[*] กำลังเปิด smart-cooker.service คืนค่าเดิม...")
    ssh.exec_command("sudo systemctl start smart-cooker.service")

def main():
    print("=" * 70)
    print("   HARDWARE DIAGNOSTIC SUITE (ทดสอบอุปกรณ์กล่องข้างหม้อหุงข้าว)")
    print("   [โหมด Hands-Free / ไร้สัมผัส 100% - ไม่ใช้ปุ่มกด]")
    print("=" * 70)
    print(f" Target Box: {PI_USER}@{PI_IP}")
    print()
    print("  [1] ทดสอบไฟ LED 3 สี (แดง GPIO 17 -> เหลือง GPIO 27 -> เขียว GPIO 22)")
    print("  [2] ทดสอบเซนเซอร์ Ultrasonic HC-SR04 (วัดระยะทางสด TRIG 23, ECHO 24)")
    print("  [3] ทดสอบเสียงพูดภาษาไทย (เล่นออกลำโพงคอมพิวเตอร์ Windows และ Pi)")
    print("  [4] ถ่ายภาพจากกล้อง USB และเปิดรูปบนหน้าจอ Windows ทันที")
    print("  [5] เปิดสตรีมกล้องสดแบบเรียลไทม์ (Live Video Stream ใน Browser)")
    print("  [0] ออกจากโปรแกรม")
    print("=" * 70)

    try:
        choice = input("เลือกหมายเลขการทดสอบ (1, 2, 3, 4, 5, 0): ").strip()
    except EOFError:
        choice = "0"

    if choice == "0" or not choice:
        return

    print(f"\n[*] กำลังเชื่อมต่อ {PI_IP}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=8)
    except Exception as e:
        print(f"[!] เชื่อมต่อไม่สำเร็จ: {e}")
        return

    was_paused = False
    try:
        if choice == "1":
            was_paused = pause_service_if_active(ssh)
            print("\n[*] กำลังทดสอบไฟ LED 3 สี...")
            code = """
import time
from smart_rice_cooker.hardware.led_controller import LEDController
from smart_rice_cooker.config import settings

leds = LEDController(settings.PIN_LED_RED, settings.PIN_LED_YELLOW, settings.PIN_LED_GREEN)
if leds._is_mock:
    print('[-] คำเตือน: ระบบเข้าสู่โหมด MOCK ไม่สามารถส่งกระแสไฟไปที่ขาจริงได้')
else:
    print('[+] ตรวจพบฮาร์ดแวร์ GPIO สมบูรณ์ 100%! กำลังส่งไฟ 3.3V ออกขาพินจริง...')

print('🔴 1. เปิดไฟสีแดง (Pin 11 / GPIO 17) ค้างไว้ 4 วินาที...')
leds.set_standby()
time.sleep(4)

print('🟡 2. เปิดไฟสีเหลือง (Pin 13 / GPIO 27) ค้างไว้ 4 วินาที...')
leds.set_detecting()
time.sleep(4)

print('🟢 3. เปิดไฟสีเขียว (Pin 15 / GPIO 22) ค้างไว้ 4 วินาที...')
leds.set_announcing(has_meds=True)
time.sleep(4)

print('💡 4. เปิดไฟทั้ง 3 สีพร้อมกัน ค้างไว้ 4 วินาที...')
if not leds._is_mock:
    leds.red.on()
    leds.yellow.on()
    leds.green.on()
time.sleep(4)

leds.all_off()
print('[+] ทดสอบไฟ LED ครบทุกสถานะเรียบร้อย!')
"""
            run_remote_python(ssh, code)

        elif choice == "2":
            was_paused = pause_service_if_active(ssh)
            print("\n[*] กำลังเริ่มอ่านค่าจากเซนเซอร์ Ultrasonic HC-SR04 จริงบนบอร์ด Pi...")
            print("[*] นำมือขยับเข้าใกล้และถอยออกจากหน้ารูเซนเซอร์เพื่อดูค่าระยะทางสด...")
            code = """
import time
from smart_rice_cooker.hardware.ultrasonic_sensor import UltrasonicSensor
from smart_rice_cooker.config import settings

sensor = UltrasonicSensor(
    trig_pin=settings.PIN_ULTRASONIC_TRIG,
    echo_pin=settings.PIN_ULTRASONIC_ECHO,
    out_pin=settings.PIN_ULTRASONIC_OUT,
    model=settings.ULTRASONIC_MODEL
)
print(f'[*] เซนเซอร์ที่ใช้งาน: {sensor.model}')
print('----------------------------------------------------------------------')
for i in range(35):
    dist = sensor.get_distance_cm()
    present = (dist < settings.DISTANCE_TRIGGER_CM)
    status = '🚶 [ตรวจพบคนเข้าใกล้!]' if present else '🟢 [ระยะปกติ / นอกระยะ]'
    bar = '█' * int(min(max(dist, 0), 100) / 4)
    print(f'📡 วัดระยะได้: {dist:5.1f} ซม. |{bar:<25}| {status}')
    time.sleep(0.3)

sensor.stop_monitoring()
print('[+] จบการทดสอบ Ultrasonic')
"""
            run_remote_python(ssh, code)

        elif choice == "3":
            print("\n[*] กำลังทดสอบส่งเสียงพูดภาษาไทยสไตล์ลูกหลาน (ช้า ชัด นุ่มนวล พร้อมเสียงกระดิ่งนำร่อง)...")
            print("[*] (ระบบจะเล่นออกทั้งลำโพงของ Raspberry Pi และลำโพงของคอมพิวเตอร์ Windows)")
            code = """
from smart_rice_cooker.voice.tts_engine import TTSEngine
from smart_rice_cooker.voice.audio_player import AudioPlayer
from smart_rice_cooker.config import settings

tts = TTSEngine(settings.AUDIO_CACHE_DIR, settings.VOICE_NAME, rate=settings.VOICE_RATE)
player = AudioPlayer(settings.AUDIO_PLAYER_CMD)

test_phrase = 'สวัสดีค่ะคุณยาย ตอนนี้ถึงเวลาข้าวเที่ยงแล้วนะคะ มื้อนี้มียาลดความดัน ซองสีเขียว 1 เม็ด ทานหลังอาหารค่ะ ขอให้ทานข้าวให้อร่อย ทานให้อิ่มนะคะ และอย่าลืมดื่มน้ำตามเยอะๆ ค่ะ'
print(f'[*] กำลังพูด: {test_phrase}')
path = tts.synthesize(test_phrase)
if path:
    print('PLAYING_CHIME:chime.mp3')
    print(f'PLAYING_AUDIO_FILE:{path.name}')
    player.play_with_chime(path, chime_path=settings.CHIME_FILE, blocking=False)
print('[+] ประมวลผลและทดสอบเสียงบน Pi เสร็จสมบูรณ์!')
"""
            out = run_remote_python(ssh, code)
            import re
            m_chime = re.search(r'PLAYING_CHIME:([a-zA-Z0-9_\-\.]+?\.mp3)', out)
            m_audio = re.search(r'PLAYING_AUDIO_FILE:([a-zA-Z0-9_\-\.]+?\.mp3)', out)
            try:
                sftp = ssh.open_sftp()
                if m_chime:
                    chime_file = m_chime.group(1)
                    print(f"\n[+] 🔔 กำลังเล่นเสียงกระดิ่งนำร่อง '{chime_file}' ผ่านลำโพงคอมพิวเตอร์...")
                    play_cached_file(chime_file, sftp=sftp, blocking=True)
                    time.sleep(0.3)
                if m_audio:
                    audio_file = m_audio.group(1)
                    print(f"[+] 🔊 กำลังเล่นเสียงพูดภาษาไทย (สปีด -10%) '{audio_file}' ผ่านลำโพงคอมพิวเตอร์...")
                    play_cached_file(audio_file, sftp=sftp, blocking=True)
                sftp.close()
                print("[+] 🔊 เล่นเสียงสไตล์ลูกหลานผ่านลำโพงของคอมพิวเตอร์เสร็จสิ้นเรียบร้อยแล้ว!")
            except Exception as e:
                print(f"[!] เล่นเสียงบนคอมพิวเตอร์ขัดข้อง: {e}")

        elif choice == "4":
            was_paused = pause_service_if_active(ssh)
            print("\n[*] กำลังถ่ายภาพจากกล้อง USB บน Pi และดึงภาพมาแสดงบนหน้าจอ Windows...")
            code = """
import cv2
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print('[-] ไม่สามารถเปิดกล้องได้')
else:
    ret, frame = cap.read()
    if ret and frame is not None:
        cv2.imwrite('/tmp/hardware_test_snapshot.jpg', frame)
        print(f'[+] กล้องทำงานสมบูรณ์! บันทึกภาพขนาด {frame.shape[1]}x{frame.shape[0]} เรียบร้อย')
    else:
        print('[-] อ่านภาพจากกล้องไม่สำเร็จ')
    cap.release()
"""
            run_remote_python(ssh, code)
            
            # Download snapshot to Windows and open it
            try:
                sftp = ssh.open_sftp()
                local_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "camera_test.jpg")
                sftp.get('/tmp/hardware_test_snapshot.jpg', local_img)
                sftp.close()
                print(f"[+] บันทึกภาพลงคอมพิวเตอร์สำเร็จ: {local_img}")
                print("[*] กำลังเปิดหน้าต่างรูปภาพบน Windows...")
                os.startfile(local_img)
            except Exception as e:
                print(f"[!] ไม่สามารถดึงภาพมาเปิดได้: {e}")

        elif choice == "5":
            ssh.close()
            import subprocess
            runner = os.path.join(os.path.dirname(os.path.abspath(__file__)), "view_live_camera.py")
            subprocess.run([sys.executable, runner])
            return

    finally:
        if was_paused:
            resume_service(ssh)
        ssh.close()

    print("\n[+] สิ้นสุดการทดสอบ")

if __name__ == "__main__":
    main()
