@echo off
chcp 65001 > nul
echo Starting to build video editor application...
echo.

echo Checking Python environment...
python --version
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found, please make sure Python is installed and added to PATH
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting to build application...
python build_app_unified.py
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to build application
    pause
    exit /b 1
)

echo.
echo Build completed!
echo Executable file is in the dist directory
echo.

pause 