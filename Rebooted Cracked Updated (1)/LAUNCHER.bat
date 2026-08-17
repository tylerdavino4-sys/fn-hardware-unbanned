@echo off
title REBOOTEDSPOOFER Crack
cd /d "%~dp0"

:: Check admin - relaunch as admin if not
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Requesting admin privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [*] Starting REBOOTEDSPOOFER Crack...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0LAUNCHER.ps1"
pause