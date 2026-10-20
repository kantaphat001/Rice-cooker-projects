@echo off
chcp 65001 >nul
title Smart Med Reminder - Test System Integration
color 0B
echo ======================================================================
echo    SMART MED REMINDER - TEST SYSTEM INTEGRATION
echo    ทดสอบการเชื่อมต่อระบบ: หน้าเว็บ ^<--^> ฐานข้อมูลยา ^<--^> Raspberry Pi
echo ======================================================================
echo.
python "%~dp0test_integration.py"
echo.
pause
