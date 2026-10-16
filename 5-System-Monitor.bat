@echo off
title Raspberry Pi 4 - Live Resource & Temperature Dashboard
color 0E
python "%~dp0deploy\system_monitor.py"
pause
