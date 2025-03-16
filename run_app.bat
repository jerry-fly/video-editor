@echo off
chcp 65001 > nul
echo Starting video editor application...
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
pip show PyQt5 >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting application...
python run.py
if %ERRORLEVEL% neq 0 (
    echo Error: Application failed to run
    pause
    exit /b 1
)

exit /b 0 