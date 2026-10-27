@echo off
chcp 65001 >nul
title Safe Shutdown - Raspberry Pi
color 0C
python "%~dp0deploy\shutdown_pi.py"
