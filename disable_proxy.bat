@echo off
chcp 65001 > nul
echo ============================================================
echo 禁用代理设置工具
echo ============================================================
echo.
echo 此批处理文件将禁用Python pip的代理设置，解决代理连接问题
echo.

echo 检查Python环境...
python --version
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo.
echo 运行禁用代理脚本...
python disable_proxy.py
if %ERRORLEVEL% neq 0 (
    echo 错误: 禁用代理失败，请查看日志获取详细信息
    pause
    exit /b 1
)

echo.
echo 代理设置已处理完成！
echo 现在您可以尝试重新安装依赖了。
echo.
echo 是否立即运行依赖安装程序？(Y/N)
choice /c YN /n
if %ERRORLEVEL% equ 1 (
    echo.
    echo 运行依赖安装程序...
    call install_dependencies.bat
) else (
    echo.
    echo 您可以稍后手动运行 install_dependencies.bat 安装依赖
)

pause 