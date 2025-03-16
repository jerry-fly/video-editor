@echo off
chcp 65001 > nul
echo ============================================================
echo 视频编辑器依赖安装工具
echo ============================================================
echo.
echo 此批处理文件将安装视频编辑器所需的所有依赖
echo.

echo 检查Python环境...
python --version
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo.
echo 运行依赖安装脚本...
python install_dependencies.py
if %ERRORLEVEL% neq 0 (
    echo 错误: 依赖安装失败，请查看日志获取详细信息
    pause
    exit /b 1
)

echo.
echo 依赖安装完成！
echo 现在您可以运行应用程序了。
echo.
pause 