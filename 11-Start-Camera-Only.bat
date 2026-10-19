@echo off
chcp 65001 >nul
title Smart Rice Cooker Companion Box - Camera-Only Mode
color 0B
python "%~dp0run_companion_box.py" --camera-only
pause
