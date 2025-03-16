@echo off
chcp 65001 > nul
echo 启动视频编辑器应用程序（修复版）...
echo.

echo 检查Python环境...
python --version
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo.
echo 启动应用程序...
python run_fixed.py
if %ERRORLEVEL% neq 0 (
    echo 错误: 应用程序运行失败
    pause
    exit /b 1
)

exit /b 0
