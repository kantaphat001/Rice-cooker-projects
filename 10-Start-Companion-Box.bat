@echo off
chcp 65001 >nul
title Smart Rice Cooker Companion Box - Full Mode
color 0A
python "%~dp0run_companion_box.py" --full-hardware
pause
