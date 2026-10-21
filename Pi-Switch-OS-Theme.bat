@echo off
chcp 65001 >nul
title Desktop OS and Theme Switcher - Raspberry Pi 4 Suite
color 0D

:SELECT_IP
cls
set "TARGET_IP=172.20.1.21"
if exist "%~dp0config_ip.txt" (
    set /p TARGET_IP=<"%~dp0config_ip.txt"
)

echo ================================================================================
echo    RASPBERRY PI 4 - DESKTOP OS AND THEME SWITCHER
echo ================================================================================
echo  เลือกเครื่องที่ต้องการสลับหน้าจอ:
echo.
echo   [1] เครื่องหลัก (IP: %TARGET_IP%) [กด Enter ได้ทันที]
echo   [2] ระบุหมายเลข IP อื่นด้วยตนเอง
echo.
set TARGET_CHOICE=1
set /p TARGET_CHOICE="เลือกหมายเลข (1, 2, เริ่มต้น 1): "

if "%TARGET_CHOICE%"=="2" (
    set /p TARGET_IP="ระบุหมายเลข IP ของ Raspberry Pi: "
)

:SELECT_THEME
cls
echo ================================================================================
echo    สลับสไตล์หน้าจอสำหรับ: pi@%TARGET_IP%
echo ================================================================================
echo  [1] สไตล์ XFCE Desktop (แนะนำสำหรับ RAM 1GB)
echo      - หน้าตาเหมือน Windows ดั้งเดิม
echo      - Start Menu มุมซ้ายล่าง, Taskbar ด้านล่าง, ตัวจัดการไฟล์ Thunar
echo      - กิน RAM ประมาณ ~140 MB (เสถียรสูง เหมาะกับบอร์ด 1GB)
echo.
echo  [2] สไตล์ PIXEL / LXDE (สไตล์ดั้งเดิม Raspberry Pi)
echo      - หน้าตาแบบออริจินัลของ Raspberry Pi
echo      - โลโก้ผลราสเบอร์รี่มุมซ้ายบน, แถบเมนูด้านบน, วอลเปเปอร์วิวภูเขาสีส้ม
echo      - กิน RAM ประมาณ ~100 MB (เบาหวิว กินแรมน้อยที่สุด)
echo.
echo  [0] ออกจากโปรแกรม
echo ================================================================================
set /p THEME_CHOICE="เลือกหมายเลข (1, 2, 0): "

if "%THEME_CHOICE%"=="1" (
    echo.
    echo [*] กำลังสลับไปใช้ XFCE Desktop (สไตล์ Windows)...
    ssh -o StrictHostKeyChecking=no pi@%TARGET_IP% "echo 'exec startxfce4' > /home/pi/.xsession; chmod +x /home/pi/.xsession; sudo update-alternatives --set x-session-manager /usr/bin/startxfce4 2>/dev/null || true; sudo systemctl restart lightdm; sudo systemctl restart xrdp"
    echo [+] สลับเป็น XFCE Desktop เรียบร้อยแล้ว!
    pause
    goto SELECT_IP
)
if "%THEME_CHOICE%"=="2" (
    echo.
    echo [*] กำลังติดตั้ง/สลับไปใช้ PIXEL / LXDE Desktop (สไตล์ Raspberry Pi)...
    ssh -o StrictHostKeyChecking=no pi@%TARGET_IP% "sudo apt-get install -y --no-install-recommends openbox lxpanel pcmanfm 2>/dev/null; echo 'exec openbox-session' > /home/pi/.xsession; chmod +x /home/pi/.xsession; sudo update-alternatives --set x-session-manager /usr/bin/openbox-session 2>/dev/null || true; sudo systemctl restart lightdm; sudo systemctl restart xrdp"
    echo [+] สลับเป็น PIXEL / LXDE Desktop เรียบร้อยแล้ว!
    pause
    goto SELECT_IP
)
if "%THEME_CHOICE%"=="0" exit
goto SELECT_THEME
