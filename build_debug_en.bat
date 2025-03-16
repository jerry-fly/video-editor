@echo off
rem Set UTF-8 encoding
chcp 65001 > nul

echo ============================================================
echo Building Debug Version of Video Editor
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
echo Checking disk space...
python -c "import shutil; disk = shutil.disk_usage('.'); free_gb = disk.free / (1024**3); print(f'Free disk space: {free_gb:.2f} GB'); exit(1 if free_gb < 2 else 0)"
if errorlevel 1 (
    echo ERROR: Not enough disk space! You need at least 2 GB of free space.
    echo Please free up some disk space and try again.
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
echo Cleaning previous build files...
if exist "build" rmdir /s /q build
if exist "dist\VideoEditor_Debug" rmdir /s /q "dist\VideoEditor_Debug"

echo.
echo Building debug version...
pyinstaller --name=VideoEditor_Debug --console --add-data="resources;resources" ^
  --exclude-module=tkinter ^
  --exclude-module=tcl ^
  --exclude-module=tk ^
  --exclude-module=matplotlib ^
  --exclude-module=PySide2 ^
  --exclude-module=PySide6 ^
  --exclude-module=PyQt6 ^
  --exclude-module=PIL ^
  --exclude-module=IPython ^
  --exclude-module=pandas ^
  --exclude-module=scipy ^
  --exclude-module=notebook ^
  --exclude-module=sphinx ^
  --exclude-module=pytest ^
  run.py

if errorlevel 1 (
    echo Error: Build failed.
    pause
    exit /b 1
)

echo.
echo Debug build completed!
echo Executable is located in the dist directory: VideoEditor_Debug\VideoEditor_Debug.exe
echo Run this file and check the console output to diagnose issues.
echo.

pause 