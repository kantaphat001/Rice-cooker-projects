@echo off
chcp 65001 >nul
title Service Controller - Raspberry Pi
color 0E
python "%~dp0deploy\service_control.py"
pause
