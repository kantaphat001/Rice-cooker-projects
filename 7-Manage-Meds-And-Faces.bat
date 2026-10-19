@echo off
title Smart Rice Cooker - Medication & Face Management Portal
color 0A
echo ======================================================================
echo    SMART RICE COOKER - MEDICATION & FACE MANAGEMENT PORTAL
echo    ระบบจัดการตารางยา (เพิ่ม/ลบยาได้ใน 1 คลิก) และเพิ่มรูปหน้าสมาชิก
echo ======================================================================
echo.
echo กำลังเปิดระบบจัดการยาและรูปหน้าในเบราว์เซอร์...
echo.
python "%~dp0web_manager.py"
pause
