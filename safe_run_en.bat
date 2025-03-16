@echo off
rem Set UTF-8 encoding
chcp 65001 > nul

echo ============================================================
echo Safe Start Video Editor (Enhanced Protection)
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
echo Installing required libraries...
pip install psutil
if errorlevel 1 (
    echo Warning: Failed to install psutil. Will try to continue...
)

echo.
echo EMERGENCY CLEANUP - Terminating any existing VideoEditor processes...
python process_monitor.py --emergency
timeout /t 2 > nul

echo.
echo Starting enhanced process monitor...
start "VideoEditor Process Monitor" cmd /c "python process_monitor.py --monitor --max 1 --auto-kill --interval 2 --cpu 80 --memory 80"

echo.
echo Starting Video Editor with protection...
if exist "dist\VideoEditor\VideoEditor.exe" (
    cd dist\VideoEditor
    start VideoEditor.exe
    cd ..\..
) else if exist "dist\VideoEditor_Debug\VideoEditor_Debug.exe" (
    cd dist\VideoEditor_Debug
    start VideoEditor_Debug.exe
    cd ..\..
) else (
    echo Executable not found, will run Python script directly
    start "VideoEditor" cmd /c "python run.py"
)

echo.
echo Application started with enhanced protection
echo.
echo If the application becomes unresponsive or creates too many processes:
echo 1. Run emergency_cleanup_en.bat to force terminate all processes
echo 2. Check logs in the logs directory for error information
echo.
pause 