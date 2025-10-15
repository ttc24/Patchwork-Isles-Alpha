@echo off
title Patchwork Isles v1.0.0
echo Starting Patchwork Isles...
echo.

cd /d "%~dp0"
python patchwork_isles.py
if errorlevel 1 (
    echo.
    echo ❌ Error running Patchwork Isles
    echo Make sure Python 3.8+ is installed and in your PATH
    pause
)
