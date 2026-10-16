"""
hardware_test.py - Windows Helper to run hardware tests on Pi
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

PI_IP = "192.168.88.74"
PI_USER = "pi"
PI_PASS = "1234"

def run_remote_python(ssh, code: str):
    transport = ssh.get_transport()
    channel = transport.open_session()
    channel.get_pty()
    channel.exec_command(f"python3 -c \"{code}\"")
    while True:
        if channel.recv_ready():
            out = channel.recv(4096).decode('utf-8', errors='replace')
            sys.stdout.write(out)
            sys.stdout.flush()
        if channel.recv_stderr_ready():
            err = channel.recv_stderr(4096).decode('utf-8', errors='replace')
            sys.stderr.write(err)
            sys.stderr.flush()
        if channel.exit_status_ready():
            break
        time.sleep(0.05)
    channel.close()

def main():
    print("=" * 70)
    print("   HARDWARE DIAGNOSTIC SUITE (ทดสอบอุปกรณ์กล่องข้างหม้อหุงข้าว)")
    print("=" * 70)
    print(f" Target Box: {PI_USER}@{PI_IP}")
    print()
    print("  [1] ทดสอบไฟ LED 3 สี (แดง GPIO 17 -> เหลือง GPIO 27 -> เขียว GPIO 22)")
    print("  [2] ทดสอบปุ่มกด Acknowledge Button (GPIO 25)")
    print("  [3] ทดสอบเซนเซอร์ Ultrasonic HC-SR04 (วัดระยะทางสด)")
    print("  [4] ทดสอบเสียงพูดภาษาไทยผ่านลำโพง (mpg123)")
    print("  [5] ถ่ายภาพจากกล้อง USB และเปิดรูปบนหน้าจอ Windows ทันที")
    print("  [6] เปิดสตรีมกล้องสดแบบเรียลไทม์ (Live Video Stream ใน Browser)")
    print("  [0] ออกจากโปรแกรม")
    print("=" * 70)

    try:
        choice = input("เลือกหมายเลขการทดสอบ (1, 2, 3, 4, 5, 6, 0): ").strip()
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

    if choice == "1":
        print("\n[*] กำลังทดสอบไฟ LED 3 สี...")
        code = """
import time
from smart_rice_cooker.hardware.led_controller import LEDController
from smart_rice_cooker.config import settings

leds = LEDController(settings.PIN_LED_RED, settings.PIN_LED_YELLOW, settings.PIN_LED_GREEN)
print('🔴 1. เปิดไฟสีแดง (Standby)...')
leds.set_standby()
time.sleep(2)

print('🟡 2. เปิดไฟสีเหลือง (Detecting)...')
leds.set_detecting()
time.sleep(2)

print('🟢 3. เปิดไฟสีเขียว (Announcing)...')
leds.set_announcing(has_meds=True)
time.sleep(2)

leds.all_off()
print('[+] ทดสอบไฟ LED ครบทุกสถานะเรียบร้อย!')
"""
        run_remote_python(ssh, code)

    elif choice == "2":
        print("\n[*] กำลังรอการกดปุ่ม GPIO 25 (ระบบรอ 15 วินาที)...")
        code = """
import time
from smart_rice_cooker.hardware.button_manager import ButtonManager
from smart_rice_cooker.config import settings

pressed = False
def on_press():
    global pressed
    pressed = True
    print('🔘 [SUCCESS] ตรวจพบการกดปุ่มยืนยัน GPIO 25 แล้ว!')

btn = ButtonManager(settings.PIN_BUTTON_ACK, on_pressed=on_press)
start = time.time()
while time.time() - start < 15 and not pressed:
    time.sleep(0.1)

if not pressed:
    print('[-] หมดเวลา ไม่พบสัญญาณกดปุ่ม')
btn.close()
"""
        run_remote_python(ssh, code)

    elif choice == "3":
        print("\n[*] กำลังวัดระยะทาง Ultrasonic (นำมือเข้า-ออกหน้ารูเซนเซอร์)...")
        code = """
import time
from smart_rice_cooker.hardware.ultrasonic_sensor import UltrasonicSensor
from smart_rice_cooker.config import settings

sensor = UltrasonicSensor(settings.PIN_ULTRASONIC_TRIG, settings.PIN_ULTRASONIC_ECHO)
for _ in range(20):
    dist = sensor.get_distance_cm()
    print(f'📡 ระยะทางที่ตรวจจับได้: {dist:.1f} ซม.')
    time.sleep(0.3)
"""
        run_remote_python(ssh, code)

    elif choice == "4":
        print("\n[*] กำลังทดสอบส่งเสียงพูดภาษาไทยออกลำโพง...")
        code = """
from smart_rice_cooker.voice.tts_engine import TTSEngine
from smart_rice_cooker.voice.audio_player import AudioPlayer
from smart_rice_cooker.config import settings

tts = TTSEngine(settings.AUDIO_CACHE_DIR, settings.VOICE_NAME)
player = AudioPlayer(settings.AUDIO_PLAYER_CMD)

test_phrase = 'ทดสอบระบบเสียงภาษาไทย หม้อหุงข้าวอัจฉริยะพร้อมใช้งานแล้วค่ะ'
print(f'[*] กำลังพูด: {test_phrase}')
path = tts.synthesize(test_phrase)
if path:
    player.play_file(path, blocking=True)
print('[+] ทดสอบเสียงเสร็จสมบูรณ์!')
"""
        run_remote_python(ssh, code)

    elif choice == "5":
        print("\n[*] กำลังถ่ายภาพจากกล้อง USB บน Pi และดึงภาพมาแสดงบนหน้าจอ Windows...")
        code = """
import cv2
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

    elif choice == "6":
        ssh.close()
        import subprocess
        runner = os.path.join(os.path.dirname(os.path.abspath(__file__)), "view_live_camera.py")
        subprocess.run([sys.executable, runner])
        return

    ssh.close()
    print("\n[+] สิ้นสุดการทดสอบ")

if __name__ == "__main__":
    main()
