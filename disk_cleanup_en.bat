@echo off
rem Set UTF-8 encoding
chcp 65001 > nul

echo ============================================================
echo Disk Cleanup Tool for Video Editor
echo ============================================================
echo.

echo Checking disk space before cleanup...
python -c "import shutil; disk = shutil.disk_usage('.'); free_gb = disk.free / (1024**3); print(f'Free disk space: {free_gb:.2f} GB')"

echo.
echo Starting cleanup operations...

echo.
echo 1. Removing build directories...
if exist "build" (
    rmdir /s /q build
    echo   - Removed build directory
)
if exist "dist" (
    rmdir /s /q dist
    echo   - Removed dist directory
)

echo.
echo 2. Cleaning Python cache files...
if exist "__pycache__" (
    rmdir /s /q __pycache__
    echo   - Removed __pycache__ directory
)
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    rmdir /s /q "%%d"
    echo   - Removed %%d
)
for /r . %%f in (*.pyc) do @if exist "%%f" (
    del "%%f"
    echo   - Removed %%f
)

echo.
echo 3. Cleaning log files...
if exist "logs" (
    echo   - Cleaning old log files...
    python -c "import os, time; log_dir='logs'; now=time.time(); [os.remove(os.path.join(log_dir, f)) for f in os.listdir(log_dir) if f.endswith('.log') and os.path.isfile(os.path.join(log_dir, f)) and now - os.path.getmtime(os.path.join(log_dir, f)) > 7*24*60*60]"
    echo   - Removed log files older than 7 days
)

echo.
echo 4. Cleaning temporary files...
python -c "import tempfile, os, shutil; temp_dir = tempfile.gettempdir(); [shutil.rmtree(os.path.join(temp_dir, d), ignore_errors=True) for d in os.listdir(temp_dir) if 'video_editor' in d.lower() or 'pyinstaller' in d.lower()]"
echo   - Removed temporary files related to Video Editor

echo.
echo 5. Cleaning pip cache...
pip cache purge
echo   - Cleaned pip cache

echo.
echo Checking disk space after cleanup...
python -c "import shutil; disk = shutil.disk_usage('.'); free_gb = disk.free / (1024**3); print(f'Free disk space: {free_gb:.2f} GB')"

echo.
echo Cleanup completed!
echo.
echo If you still need more disk space, consider:
echo - Uninstalling unused programs
echo - Moving large files to external storage
echo - Using Windows Disk Cleanup tool (cleanmgr)
echo.
pause 