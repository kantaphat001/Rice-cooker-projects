@echo off
chcp 65001 >nul
title 1-Click Automated Setup - Raspberry Pi 4 Suite
color 0B

echo ================================================================================
echo    RASPBERRY PI 4 - AUTOMATED 1-CLICK PROVISIONING AND SETUP SUITE
echo ================================================================================
echo  เป้าหมายการติดตั้ง:
echo.
echo   [1] เครื่องหลัก (IP: 192.168.88.74) [กด Enter ได้ทันที]
echo   [2] ระบุหมายเลข IP อื่นด้วยตนเอง
echo.
set TARGET_CHOICE=1
set /p TARGET_CHOICE="เลือกหมายเลข (1, 2, เริ่มต้น 1): "

if "%TARGET_CHOICE%"=="2" (
    set /p TARGET_IP="ระบุหมายเลข IP ของ Raspberry Pi: "
) else (
    set "TARGET_IP=192.168.88.74"
)

echo.
echo [*] กำลังตรวจสอบการเชื่อมต่อกับ pi@%TARGET_IP%...
ping -n 1 -w 1000 %TARGET_IP% >nul
if errorlevel 1 (
    echo [!] ข้อผิดพลาด: ไม่สามารถติดต่อ %TARGET_IP% ได้ กรุณาตรวจสอบการเชื่อมต่อ Wi-Fi หรือสาย LAN
    pause
    exit /b 1
)

echo.
echo [*] กำลังส่งโฟลเดอร์ pi_setup_scripts ขึ้นไปยังบอร์ด Raspberry Pi...
scp -o StrictHostKeyChecking=no -r "%~dp0pi_setup_scripts" pi@%TARGET_IP%:~/

echo.
echo [*] กำลังแปลงบรรทัด CRLF -^> LF, กำหนดสิทธิ์ และเริ่มการติดตั้งอัตโนมัติ...
ssh -o StrictHostKeyChecking=no -t pi@%TARGET_IP% "sed -i 's/\r$//' ~/pi_setup_scripts/*.sh && chmod +x ~/pi_setup_scripts/*.sh && sudo bash ~/pi_setup_scripts/master_setup.sh"

echo.
echo ================================================================================
echo  [+] ติดตั้งและปรับแต่งระบบบน %TARGET_IP% เสร็จสมบูรณ์แล้ว!
echo ================================================================================
pause
