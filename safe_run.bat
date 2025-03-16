@echo off
chcp 65001 > nul
echo ============================================================
echo 安全启动视频编辑器
echo ============================================================
echo.

echo 检查Python环境...
python --version
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo.
echo 安装psutil库...
pip install psutil
if %ERRORLEVEL% neq 0 (
    echo 警告: 安装psutil失败，将尝试继续...
)

echo.
echo 清理可能存在的VideoEditor进程...
python process_monitor.py --cleanup

echo.
echo 启动进程监控...
start "VideoEditor进程监控" cmd /c "python process_monitor.py --monitor --max 2 --auto-kill --interval 3"

echo.
echo 启动视频编辑器...
if exist "dist\VideoEditor\VideoEditor.exe" (
    cd dist\VideoEditor
    start VideoEditor.exe
    cd ..\..
) else if exist "dist\VideoEditor_Debug\VideoEditor_Debug.exe" (
    cd dist\VideoEditor_Debug
    start VideoEditor_Debug.exe
    cd ..\..
) else (
    echo 未找到可执行文件，将直接运行Python脚本
    python run.py
)

echo.
echo 应用程序已启动
echo 如果遇到问题，请运行 cleanup_processes.bat 清理所有进程
echo.
pause 