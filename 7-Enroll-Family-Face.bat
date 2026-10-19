@echo off
chcp 65001 >nul
title Enroll Face and Manage Meds - Smart Rice Cooker
color 0E
echo ======================================================================
echo    SMART RICE COOKER - FACE and MEDICATION PORTAL
echo ======================================================================
echo.
echo  [1] เปิดหน้าต่างเว็บจัดการยาและเพิ่มรูปหน้า (แนะนำ ใช้งานง่ายที่สุด)
echo  [2] ถ่ายรูปหน้าผ่าน Terminal Console (แบบเดิม)
echo.
set /p choice="เลือกหมายเลข (1 หรือ 2, ค่าเริ่มต้น 1): "
if "%choice%"=="2" (
    python "%~dp0enroll_member.py" %*
) else (
    python "%~dp0web_manager.py"
)
pause
