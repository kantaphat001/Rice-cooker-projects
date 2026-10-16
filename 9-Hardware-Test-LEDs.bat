@echo off
chcp 65001 >nul
title Hardware Diagnostic Suite - Smart Rice Cooker
color 0B

set "TARGET_IP=192.168.88.74"
set "PI_USER=pi"

echo ================================================================================
echo    HARDWARE DIAGNOSTIC SUITE (ทดสอบอุปกรณ์กล่องข้างหม้อหุงข้าว)
echo ================================================================================
echo  Target Box: %PI_USER%@%TARGET_IP%
echo.
echo  [1] ทดสอบไฟ LED 3 สี (แดง GPIO 17 -> เหลือง GPIO 27 -> เขียว GPIO 22)
echo  [2] ทดสอบปุ่มกด Acknowledge Button (GPIO 25)
echo  [3] ทดสอบเซนเซอร์ Ultrasonic HC-SR04 (วัดระยะทางสด)
echo  [4] ทดสอบเสียงพูดภาษาไทยผ่านลำโพง (mpg123)
echo  [0] ออกจากโปรแกรม
echo.
set /p TEST_CHOICE="เลือกหมายเลขการทดสอบ (1, 2, 3, 4, 0): "

if "%TEST_CHOICE%"=="1" (
    echo.
    echo [*] กำลังทดสอบไฟ LED 3 สี (แดง -> เหลือง -> เขียว)...
    ssh -o StrictHostKeyChecking=no %PI_USER%@%TARGET_IP% "python3 -c \"
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

print('🟢 4. ทดสอบกะพริบไฟสีเขียว (Greeting)...')
leds.set_announcing(has_meds=False)
time.sleep(2)

leds.all_off()
print('[+] ทดสอบไฟ LED ครบทุกสถานะเรียบร้อย!')
\""
    pause
)

if "%TEST_CHOICE%"=="2" (
    echo.
    echo [*] กรุณากดปุ่มจริง (GPIO 25) บนกล่องอุปกรณ์ (ระบบกำลังรอรับสัญญาณ 15 วินาที)...
    ssh -o StrictHostKeyChecking=no %PI_USER%@%TARGET_IP% "python3 -c \"
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
\""
    pause
)

if "%TEST_CHOICE%"=="3" (
    echo.
    echo [*] กำลังวัดระยะทาง Ultrasonic (นำมือเข้า-ออกหน้ารูเซนเซอร์)...
    echo     (กด Ctrl+C เพื่อหยุด)
    ssh -o StrictHostKeyChecking=no %PI_USER%@%TARGET_IP% "python3 -c \"
import time
from smart_rice_cooker.hardware.ultrasonic_sensor import UltrasonicSensor
from smart_rice_cooker.config import settings

sensor = UltrasonicSensor(settings.PIN_ULTRASONIC_TRIG, settings.PIN_ULTRASONIC_ECHO)
for _ in range(30):
    dist = sensor.get_distance_cm()
    print(f'📡 ระยะทางที่ตรวจจับได้: {dist:.1f} ซม.')
    time.sleep(0.3)
\""
    pause
)

if "%TEST_CHOICE%"=="4" (
    echo.
    echo [*] กำลังทดสอบส่งเสียงพูดภาษาไทยออกลำโพง...
    ssh -o StrictHostKeyChecking=no %PI_USER%@%TARGET_IP% "python3 -c \"
from smart_rice_cooker.voice.tts_engine import TTSEngine
from smart_rice_cooker.voice.audio_player import AudioPlayer
from smart_rice_cooker.config import settings

tts = TTSEngine(settings.AUDIO_CACHE_DIR, settings.VOICE_NAME)
player = AudioPlayer(settings.AUDIO_PLAYER_CMD)

test_phrase = 'ทดสอบระบบเสียงภาษาไทย หม้อหุงข้าวอัจฉริยะพร้อมใช้งานแล้วครับ'
print(f'[*] กำลังพูด: {test_phrase}')
path = tts.synthesize(test_phrase)
if path:
    player.play_file(path, blocking=True)
print('[+] ทดสอบเสียงเสร็จสมบูรณ์!')
\""
    pause
)

if "%TEST_CHOICE%"=="0" exit
