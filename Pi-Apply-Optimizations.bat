@echo off
chcp 65001 >nul
title System Optimization Suite - Raspberry Pi 4 Suite
color 0B

set "TARGET_IP=172.20.1.21"
if exist "%~dp0config_ip.txt" (
    set /p TARGET_IP=<"%~dp0config_ip.txt"
)

echo ================================================================================
echo    RASPBERRY PI 4 - SYSTEM OPTIMIZATION (ZRAM, CPU, KERNEL)
echo ================================================================================
echo  เลือกเครื่องที่ต้องการสั่งปรับจูนประสิทธิภาพ:
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
echo [*] กำลังส่งคำสั่งปรับจูน ZRAM และเคอร์เนลไปยัง pi@%TARGET_IP%...
ssh -o StrictHostKeyChecking=no pi@%TARGET_IP% "sudo bash -c 'systemctl stop dphys-swapfile 2>/dev/null || true; systemctl disable dphys-swapfile 2>/dev/null || true; dphys-swapfile swapoff 2>/dev/null || true; rm -f /var/swap 2>/dev/null || true; apt-get update -y >/dev/null 2>&1; apt-get install -y --no-install-recommends zram-tools; echo -e \"ALGO=lz4\nPERCENT=100\nPRIORITY=100\" > /etc/default/zramswap; systemctl enable zramswap 2>/dev/null; systemctl restart zramswap; echo -e \"vm.swappiness=100\nvm.page-cluster=0\nvm.vfs_cache_pressure=50\" > /etc/sysctl.d/99-zram-optimizations.conf; sysctl -p /etc/sysctl.d/99-zram-optimizations.conf; apt-get clean'"

echo.
echo ================================================================================
echo  [+] ปรับจูนระบบบน %TARGET_IP% สำเร็จแล้ว!
echo  - ปิด Swap บน MicroSD Card ถาวร (ถนอมการ์ด)
echo  - เปิดใช้ ZRAM 100%% บีบอัดหน่วยความจำ LZ4 ความเร็วสูง
echo  - เคอร์เนล vm.swappiness=100 และ page-cluster=0
echo ================================================================================
pause
