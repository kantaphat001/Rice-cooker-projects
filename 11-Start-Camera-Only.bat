@echo off
chcp 65001 >nul
title Smart Rice Cooker Companion Box - Camera-Only Mode
color 0B
cls
echo ================================================================================
echo    📷 SMART RICE COOKER COMPANION BOX - CAMERA-ONLY MODE
echo ================================================================================
echo.
python -m smart_rice_cooker.main --camera-only
pause
