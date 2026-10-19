@echo off
chcp 65001 >nul
title Show Live Camera Window on Raspberry Pi Screen
color 0B
python "%~dp0show_camera_on_pi.py"
pause
