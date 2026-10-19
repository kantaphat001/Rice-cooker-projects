@echo off
chcp 65001 >nul
title Raspberry Pi Wi-Fi Network Manager
color 0B
echo ======================================================================
echo    RASPBERRY PI WI-FI NETWORK MANAGER (จัดการ Wi-Fi บอร์ด Pi)
echo    เพิ่ม Wi-Fi บ้านใหม่ หรือเพิ่ม Hotspot มือถือไว้ล่วงหน้าก่อนย้ายเครื่อง
echo ======================================================================
echo.
python "%~dp0deploy\wifi_manager.py"
echo.
pause
