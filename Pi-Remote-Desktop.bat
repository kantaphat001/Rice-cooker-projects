@echo off
chcp 65001 >nul
title Remote Desktop Client - Raspberry Pi 4 Suite
color 0E

set "TARGET_IP=172.20.1.21"
if exist "%~dp0config_ip.txt" (
    set /p TARGET_IP=<"%~dp0config_ip.txt"
)

echo ================================================================================
echo    RASPBERRY PI 4 - REMOTE DESKTOP CONNECTION (1024x600)
echo ================================================================================
echo  เลือกเครื่องที่ต้องการเปิดหน้าจอ Remote Desktop:
echo.
echo   [1] เครื่องหลัก (IP: %TARGET_IP%) [กด Enter ได้ทันที]
echo   [2] ระบุหมายเลข IP อื่นด้วยตนเอง
echo.
set TARGET_CHOICE=1
set /p TARGET_CHOICE="เลือกหมายเลข (1, 2, เริ่มต้น 1): "

if "%TARGET_CHOICE%"=="2" (
    set /p TARGET_IP="ระบุหมายเลข IP ของ Raspberry Pi: "
)

echo.
echo [*] กำลังเปิดหน้าต่าง Remote Desktop ไปยัง %TARGET_IP%...
echo     (Username: pi ^| Password: 1234)
start mstsc.exe /v:%TARGET_IP% /w:1024 /h:600
exit
