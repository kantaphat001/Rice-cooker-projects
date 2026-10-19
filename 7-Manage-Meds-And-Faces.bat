@echo off
chcp 65001 >nul
title Smart Rice Cooker - Medication and Face Management Portal
color 0A
echo ======================================================================
echo    SMART RICE COOKER - MEDICATION and FACE MANAGEMENT PORTAL
echo    ระบบจัดการตารางยา (เพิ่ม/ลบยาได้ใน 1 คลิก) และเพิ่มรูปหน้าสมาชิก
echo ======================================================================
echo.
echo กำลังเปิดระบบจัดการยาและรูปหน้าในเบราว์เซอร์...
echo.
python "%~dp0web_manager.py"
pause
