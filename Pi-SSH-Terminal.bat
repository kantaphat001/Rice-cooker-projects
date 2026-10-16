@echo off
chcp 65001 >nul
title SSH Console Terminal - Raspberry Pi 4 Suite
color 0A

echo ================================================================================
echo    RASPBERRY PI 4 - SSH CONSOLE TERMINAL
echo ================================================================================
echo  เลือกเครื่องที่ต้องการเชื่อมต่อ SSH:
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
echo [*] กำลังเชื่อมต่อไปยัง pi@%TARGET_IP%...
echo     (รหัสผ่านเริ่มต้น: 1234)
ssh -o StrictHostKeyChecking=no pi@%TARGET_IP%
pause
