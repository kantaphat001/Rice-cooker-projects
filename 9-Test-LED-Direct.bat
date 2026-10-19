@echo off
chcp 65001 >nul
title Direct LED Hardware Test
color 0E
python "%~dp0test_led_direct.py"
pause
