@echo off
rem Set UTF-8 encoding
chcp 65001 > nul

echo ============================================================
echo Safe Start Video Editor
echo ============================================================
echo.

echo Checking Python environment...
python --version
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found, please make sure Python is installed and added to PATH
    pause
    exit /b 1
)

echo.
echo Checking dependencies...
python install_dependencies.py
if %ERRORLEVEL% neq 0 (
    echo Warning: Dependency check failed, will try to continue...
)

echo.
echo Installing psutil library...
pip install psutil
if %ERRORLEVEL% neq 0 (
    echo Warning: Failed to install psutil, will try to continue...
)

echo.
echo Cleaning up existing VideoEditor processes...
python process_monitor.py --cleanup
if %ERRORLEVEL% neq 0 (
    echo Warning: Process cleanup failed, will try to continue...
)

echo.
echo Starting process monitoring...
start "VideoEditor Process Monitor" cmd /c "python process_monitor.py --monitor --max 2 --auto-kill --interval 3"

echo.
echo Fixing module import path...
python fix_module_path.py
if %ERRORLEVEL% neq 0 (
    echo Warning: Module path fix failed, will try to continue...
)

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
    python run_fixed.py
)

echo.
echo Application has been started
echo If you encounter any issues, please run cleanup_processes.bat to clean up all processes
echo.
pause 