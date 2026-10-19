@echo off
chcp 65001 >nul
title Hardware Diagnostic Suite - Smart Rice Cooker
color 0B
python "%~dp0hardware_test.py" %*
pause
