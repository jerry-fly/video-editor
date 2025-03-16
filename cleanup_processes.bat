@echo off
chcp 65001 > nul
echo ============================================================
echo VideoEditor进程清理工具
echo ============================================================
echo.
echo 此批处理文件将清理所有VideoEditor相关进程
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
echo 开始清理进程...
python process_monitor.py --cleanup

echo.
echo 清理完成！
echo.
pause 