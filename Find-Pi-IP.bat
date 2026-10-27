@echo off
chcp 65001 >nul
title 🔍 ค้นหา IP และเชื่อมต่อ Raspberry Pi (Smart Rice Cooker Companion)
cls
echo ======================================================================
echo    🔍 ระบบค้นหาหมายเลข IP และจัดการเครือข่าย RASPBERRY PI
echo    สำหรับระบบกล่องแจ้งเตือนการทานยาอัจฉริยะ (Smart Rice Cooker Companion)
echo ======================================================================
echo.

python "%~dp0tools\find_pi.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] เกิดข้อผิดพลาดในการรัน tools\find_pi.py
    pause
)
