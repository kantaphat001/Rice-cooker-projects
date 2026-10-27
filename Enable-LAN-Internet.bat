@echo off
chcp 65001 >nul
title 🌐 เปิดระบบแชร์เน็ตให้ Raspberry Pi ผ่านสายแลน (Auto-ICS)
cls
echo ======================================================================
echo    🌐 ระบบแชร์เน็ตจากโน้ตบุ๊กไปยัง Raspberry Pi ผ่านสายแลน (Auto-ICS)
echo ======================================================================
echo.
echo กำลังเปิดระบบแชร์เน็ตอัตโนมัติ... (หากมีหน้าต่างขอสิทธิ์ ให้กด "Yes")
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\enable_ics.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [*] กำลังเปิดหน้าต่าง Network Connections แบบแมนนวลให้สำรอง...
    control.exe netconnections
)
