@echo off
chcp 65001 >nul
title Raspberry Pi 4 - Live Resource and Temperature Dashboard
color 0E
python "%~dp0deploy\system_monitor.py"
pause
