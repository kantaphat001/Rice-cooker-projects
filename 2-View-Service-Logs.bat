@echo off
chcp 65001 >nul
title View Live Service Logs - Raspberry Pi
color 0B
python "%~dp0deploy\view_logs.py"
pause
