@echo off
chcp 65001 >nul
title Enroll Family Face - Smart Rice Cooker
color 0E

set "TARGET_IP=192.168.88.74"
set "PI_USER=pi"

echo ================================================================================
echo    ENROLL FAMILY MEMBER FACE (ระบบบันทึกและสแกนใบหน้าคนในครอบครัว)
echo ================================================================================
echo.
echo  ตัวอย่าง ID สมาชิก:
echo    grandpa (คุณตา)
echo    grandma (คุณยาย)
echo    dad     (คุณพ่อ)
echo    mom     (คุณแม่)
echo.
set /p MEMBER_ID="กรุณาระบุ ID สมาชิกที่ต้องการบันทึกใบหน้า: "

if "%MEMBER_ID%"=="" (
    echo [!] ไม่ได้ระบุ ID ยกเลิกการทำงาน
    pause
    exit /b 1
)

echo.
echo [*] กำลังสั่งกล้องบน Raspberry Pi ถ่ายภาพใบหน้า 10 ช็อตสำหรับ '%MEMBER_ID%'...
echo     กรุณาให้สมาชิกยืนหน้ากล้อง หันหน้าตรง และเอียงหน้าเล็กน้อย...
echo.

ssh -o StrictHostKeyChecking=no %PI_USER%@%TARGET_IP% "python3 -c \"
import cv2, os, time
from pathlib import Path

member_dir = Path('dataset') / '%MEMBER_ID%'
member_dir.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print('[-] ไม่สามารถเปิดกล้องได้')
    exit(1)

print('[+] กำลังจับภาพใบหน้า 10 ภาพ...')
count = 0
while count < 10:
    ret, frame = cap.read()
    if ret and frame is not None:
        save_path = member_dir / f'face_{int(time.time()*1000)}.jpg'
        cv2.imwrite(str(save_path), frame)
        count += 1
        print(f'  [✓] บันทึกภาพที่ {count}/10 สำเร็จ')
        time.sleep(0.4)

cap.release()
print('[+] ถ่ายภาพเสร็จสมบูรณ์!')
\""

echo.
echo [*] กำลังประมวลผลสกัด Feature Vector เวกเตอร์ใบหน้าด้วย YuNet + SFace...
ssh -o StrictHostKeyChecking=no %PI_USER%@%TARGET_IP% "python3 -m smart_rice_cooker.main --rebuild-faces"

echo.
echo ================================================================================
echo  [+] ลงทะเบียนใบหน้าของ '%MEMBER_ID%' เข้าสู่ระบบเรียบร้อยแล้ว!
echo ================================================================================
pause
