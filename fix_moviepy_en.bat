@echo off
rem Set UTF-8 encoding
chcp 65001 > nul

echo ============================================================
echo Fix moviepy.editor Module Import Issue
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
echo Fixing moviepy.editor module...
python fix_moviepy.py
if %ERRORLEVEL% neq 0 (
    echo Warning: moviepy fix failed, will try to continue...
) else (
    echo moviepy.editor module fixed successfully!
)

echo.
echo Fix completed, now you can try to run the Video Editor again
echo Please run safe_run.bat or safe_run_en.bat to start the application
echo.
pause 