@echo off
chcp 65001 >nul
title Raspberry Pi 4 - Command and Control Center
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Control-Center.ps1"
if %errorlevel% neq 0 pause
