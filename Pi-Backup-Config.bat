@echo off
chcp 65001 >nul
title Backup Pi Config - Raspberry Pi 4 Suite
color 03

set "TARGET_IP=172.20.1.21"
if exist "%~dp0config_ip.txt" (
    set /p TARGET_IP=<"%~dp0config_ip.txt"
)

echo ================================================================================
echo    RASPBERRY PI 4 - CONFIGURATION BACKUP UTILITY
echo ================================================================================
echo  เลือกเครื่องที่ต้องการสำรองข้อมูลการตั้งค่า:
echo.
echo   [1] เครื่องหลัก (IP: %TARGET_IP%) [กด Enter ได้ทันที]
echo   [2] ระบุหมายเลข IP อื่นด้วยตนเอง
echo.
set TARGET_CHOICE=1
set /p TARGET_CHOICE="เลือกหมายเลข (1, 2, เริ่มต้น 1): "

if "%TARGET_CHOICE%"=="2" (
    set /p TARGET_IP="ระบุหมายเลข IP ของ Raspberry Pi: "
)

set "BACKUP_DIR=%~dp0backups\%TARGET_IP%"
mkdir "%BACKUP_DIR%" 2>nul

echo.
echo [*] กำลังสำรองไฟล์คอนฟิกจาก pi@%TARGET_IP% มายัง %BACKUP_DIR%...
ssh -o StrictHostKeyChecking=no pi@%TARGET_IP% "tar -czf /tmp/pi_config_backup.tar.gz /etc/lightdm /etc/xrdp /etc/sysctl.d /etc/default /etc/udev/rules.d /boot/firmware/config.txt 2>/dev/null"
scp -o StrictHostKeyChecking=no pi@%TARGET_IP%:/tmp/pi_config_backup.tar.gz "%BACKUP_DIR%\pi_config_backup_%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%.tar.gz"
ssh -o StrictHostKeyChecking=no pi@%TARGET_IP% "rm -f /tmp/pi_config_backup.tar.gz"

echo.
echo ================================================================================
echo  [+] สำรองข้อมูลเรียบร้อยแล้ว ที่โฟลเดอร์: %BACKUP_DIR%
echo ================================================================================
pause
