@echo off
rem Set UTF-8 encoding
chcp 65001 > nul

echo ============================================================
echo Starting Video Editor Application
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
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Warning: Failed to install some dependencies. Will try to continue...
)

echo.
echo Ensuring NumPy compatibility...
pip install "numpy<2.0.0" --upgrade
if errorlevel 1 (
    echo Warning: NumPy installation failed. Will try to continue...
)

echo.
echo Starting application...
python run.py
if errorlevel 1 (
    echo Error: Application failed to start.
    pause
    exit /b 1
)

echo.
echo Application closed.
pause 