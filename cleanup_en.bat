@echo off
rem Set UTF-8 encoding
chcp 65001 > nul

echo ============================================================
echo VideoEditor Process Cleanup Tool
echo ============================================================
echo.

echo Checking Python environment...
python --version 2>nul
if errorlevel 1 (
    echo Error: Python not found. Please make sure Python is installed and added to PATH.
    pause
    exit /b 1
)

echo.
echo Installing psutil library...
pip install psutil
if errorlevel 1 (
    echo Warning: Failed to install psutil. Will try to continue...
)

echo.
echo Starting process cleanup...
python process_monitor.py --cleanup

echo.
echo Cleanup completed!
pause 