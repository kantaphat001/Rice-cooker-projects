@echo off
chcp 65001 >nul
title Smart Rice Cooker Companion Box - Controller
color 0A

set "TARGET_IP=192.168.88.74"
set "PI_USER=pi"

echo ================================================================================
echo    SMART RICE COOKER COMPANION BOX (2026 EDITION) - SYSTEM RUNNER
echo ================================================================================
echo  Target Box IP: %TARGET_IP%
echo.
echo  [*] กำลังซิงค์ไฟล์โปรแกรมไปยังบอร์ด Raspberry Pi...
scp -o StrictHostKeyChecking=no -r "%~dp0smart_rice_cooker" "%~dp0med_config.json" %PI_USER%@%TARGET_IP%:~/

echo.
echo  [*] กำลังสั่งรัน Smart Rice Cooker Service บน %TARGET_IP%...
echo  --------------------------------------------------------------------------------
echo  กด Ctrl+C เพื่อหยุดการทำงานของระบบ
echo  --------------------------------------------------------------------------------
ssh -o StrictHostKeyChecking=no -t %PI_USER%@%TARGET_IP% "cd ~ && python3 -m smart_rice_cooker.main --headless"

pause
