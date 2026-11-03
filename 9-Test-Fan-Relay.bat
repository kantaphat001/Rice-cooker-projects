@echo off
chcp 65001 >nul
title Cooling Fan Relay Diagnostic Test
color 0B
python -c "import paramiko" 2>nul
if errorlevel 1 (
    echo [*] Installing required library 'paramiko'...
    pip install paramiko
)
python "%~dp0test_fan_relay.py"
pause
