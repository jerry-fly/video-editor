@echo off
rem Set UTF-8 encoding
chcp 65001 > nul

echo ============================================================
echo Building Release Version of Video Editor
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
echo Installing PyInstaller...
pip install pyinstaller==6.1.0
if errorlevel 1 (
    echo Error: Failed to install PyInstaller.
    pause
    exit /b 1
)

echo.
echo Ensuring NumPy compatibility...
pip install "numpy<2.0.0" --upgrade
if errorlevel 1 (
    echo Warning: NumPy installation failed. Will try to continue...
)

echo.
echo Building release version...
pyinstaller --name=VideoEditor --windowed --add-data="resources;resources" run.py
if errorlevel 1 (
    echo Error: Build failed.
    pause
    exit /b 1
)

echo.
echo Release build completed!
echo Executable is located in the dist directory: VideoEditor\VideoEditor.exe
echo.

pause 