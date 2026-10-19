@echo off
chcp 65001 >nul
title Smart Rice Cooker - Live Camera Stream Viewer
color 0A
python "%~dp0view_live_camera.py"
pause
