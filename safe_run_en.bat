@echo off
rem Set UTF-8 encoding
chcp 65001 > nul

echo ============================================================
echo Safe Start Video Editor
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
echo Cleaning up existing VideoEditor processes...
python process_monitor.py --cleanup

echo.
echo Starting process monitor...
start "VideoEditor Process Monitor" cmd /c "python process_monitor.py --monitor --max 2 --auto-kill --interval 3"

echo.
echo Starting Video Editor...
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
    python run.py
)

echo.
echo Application started
echo If you encounter issues, run cleanup_en.bat to clean up all processes
echo.
pause 