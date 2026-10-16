@echo off
chcp 65001 >nul
title System Health Telemetry - Raspberry Pi 4 Suite
color 0F

echo ================================================================================
echo    RASPBERRY PI 4 - SYSTEM HEALTH AND TELEMETRY CHECK
echo ================================================================================
echo  เลือกเครื่องที่ต้องการตรวจเช็กสุขภาพ:
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
echo [*] กำลังดึงข้อมูลสุขภาพระบบจาก pi@%TARGET_IP%...
echo.
ssh -o StrictHostKeyChecking=no pi@%TARGET_IP% "echo '=== [1] HOSTNAME AND NETWORK ==='; hostname; hostname -I; echo ''; echo '=== [2] CPU TEMPERATURE ==='; (vcgencmd measure_temp 2>/dev/null || cat /sys/class/thermal/thermal_zone0/temp | awk '{print \$1/1000 \" deg C\"}'); echo ''; echo '=== [3] MEMORY AND ZRAM USAGE ==='; free -h; swapon --show; echo ''; echo '=== [4] MICROSD STORAGE ==='; df -h /; echo ''; echo '=== [5] CPU LOAD AND UPTIME ==='; uptime; echo ''; echo '=== [6] POWER / THROTTLING STATUS ==='; (vcgencmd get_throttled 2>/dev/null || echo 'Normal (0x0)')"

echo.
echo ================================================================================
pause
