@echo off
rem Set UTF-8 encoding
chcp 65001 > nul

echo ============================================================
echo EMERGENCY CLEANUP - VideoEditor Process Terminator
echo ============================================================
echo.
echo WARNING: This will forcefully terminate ALL VideoEditor processes!
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
echo STARTING EMERGENCY CLEANUP...
python process_monitor.py --emergency

echo.
echo Emergency cleanup completed!
echo All VideoEditor processes should be terminated.
echo.
pause 