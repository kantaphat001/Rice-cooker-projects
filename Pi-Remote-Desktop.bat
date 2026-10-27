@echo off
chcp 65001 >nul
title Remote Desktop Client - Raspberry Pi 4 Suite
color 0E

set "TARGET_IP=raspberrypi.local"
if exist "%~dp0config_ip.txt" (
    set /p TARGET_IP=<"%~dp0config_ip.txt"
)

echo ================================================================================
echo    RASPBERRY PI 4 - REMOTE DESKTOP CONNECTION (1024x600)
echo ================================================================================
echo  เลือกเครื่องที่ต้องการเปิดหน้าจอ Remote Desktop:
echo.
echo   [1] ใช้ IP ล่าสุดในระบบ (IP: %TARGET_IP%) [กด Enter ได้ทันที]
echo   [2] เชื่อมต่อผ่านชื่อเครื่อง (raspberrypi.local)
echo   [3] ค้นหาและเชื่อมต่ออัตโนมัติ (Find & Connect Pi)
echo   [4] ระบุหมายเลข IP อื่นด้วยตนเอง
echo.
set TARGET_CHOICE=1
set /p TARGET_CHOICE="เลือกหมายเลข (1, 2, 3, 4 เริ่มต้น 1): "

if "%TARGET_CHOICE%"=="2" (
    set "TARGET_IP=raspberrypi.local"
)
if "%TARGET_CHOICE%"=="3" (
    call "%~dp0Find-Pi-IP.bat"
    exit /b
)
if "%TARGET_CHOICE%"=="4" (
    set /p TARGET_IP="ระบุหมายเลข IP ของ Raspberry Pi: "
)

echo.
echo [*] กำลังเปิดหน้าต่าง Remote Desktop ไปยัง %TARGET_IP%...
echo     (Username: pi ^| Password: 1234)
start mstsc.exe /v:%TARGET_IP% /w:1024 /h:600
exit
