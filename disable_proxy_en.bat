@echo off
chcp 65001 > nul
echo ============================================================
echo Disable Proxy Settings Tool
echo ============================================================
echo.
echo This batch file will disable Python pip proxy settings to resolve proxy connection issues
echo.

echo Checking Python environment...
python --version
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found, please make sure Python is installed and added to PATH
    pause
    exit /b 1
)

echo.
echo Running proxy disabling script...
python disable_proxy.py
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to disable proxy, please check the logs for details
    pause
    exit /b 1
)

echo.
echo Proxy settings have been processed!
echo You can now try to reinstall dependencies.
echo.
echo Run dependency installation program now? (Y/N)
choice /c YN /n
if %ERRORLEVEL% equ 1 (
    echo.
    echo Running dependency installation program...
    call install_dependencies_en.bat
) else (
    echo.
    echo You can manually run install_dependencies_en.bat later to install dependencies
)

pause 