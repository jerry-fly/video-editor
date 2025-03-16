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
echo 请选择安装模式:
echo 1. 在线安装（默认）
echo 2. 离线安装
echo 3. 禁用代理并在线安装
echo 4. 禁用代理并离线安装
echo.
choice /c 1234 /n /m "请选择 [1-4]: "

if %ERRORLEVEL% equ 1 (
    echo.
    echo 选择了在线安装模式
    echo 运行依赖安装脚本...
    python install_dependencies.py
)
if %ERRORLEVEL% equ 2 (
    echo.
    echo 选择了离线安装模式
    echo 运行依赖安装脚本（离线模式）...
    python install_dependencies.py --offline
)
if %ERRORLEVEL% equ 3 (
    echo.
    echo 选择了禁用代理并在线安装模式
    echo 运行禁用代理脚本...
    python disable_proxy.py
    echo 运行依赖安装脚本...
    python install_dependencies.py --no-proxy
)
if %ERRORLEVEL% equ 4 (
    echo.
    echo 选择了禁用代理并离线安装模式
    echo 运行禁用代理脚本...
    python disable_proxy.py
    echo 运行依赖安装脚本（离线模式）...
    python install_dependencies.py --offline --no-proxy
)

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