@echo off
title Hand Controller Pro v3.0
echo ========================================
echo    Hand Controller Pro v3.0
echo    Advanced Hand Gesture Controller
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found!
echo.

echo Starting Hand Controller Pro v3.0...
echo.

python run.py

echo.
echo Program finished.
pause

