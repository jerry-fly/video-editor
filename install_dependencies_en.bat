@echo off
chcp 65001 > nul
echo ============================================================
echo Video Editor Dependency Installation Tool
echo ============================================================
echo.
echo This batch file will install all dependencies required for the Video Editor
echo.

echo Checking Python environment...
python --version
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found, please make sure Python is installed and added to PATH
    pause
    exit /b 1
)

echo.
echo Running dependency installation script...
python install_dependencies.py
if %ERRORLEVEL% neq 0 (
    echo Error: Dependency installation failed, please check the logs for details
    pause
    exit /b 1
)

echo.
echo Dependency installation completed!
echo You can now run the application.
echo.
pause 