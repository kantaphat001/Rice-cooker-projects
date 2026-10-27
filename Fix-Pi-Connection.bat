@echo off
chcp 65001 >nul
title 🔧 ระบบซ่อมแซมและเชื่อมต่อ Raspberry Pi อัตโนมัติ (One-Click Auto-Fix)
color 0B
cls
echo ======================================================================
echo    🔧 ระบบซ่อมแซมและเชื่อมต่อ RASPBERRY PI อัตโนมัติ (ONE-CLICK AUTO-FIX)
echo    Smart Rice Cooker Companion Box - 2026 Production Edition
echo ======================================================================
echo.

python "%~dp0tools\auto_fix_connection.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] หากพบปัญหา ให้ลองรัน Enable-LAN-Internet.bat
    pause
)
