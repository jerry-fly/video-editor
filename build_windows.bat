@echo off
echo 开始构建视频编辑器应用程序...
echo.

echo 检查Python环境...
python --version
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python，请确保已安装Python并添加到PATH环境变量中
    exit /b 1
)

echo.
echo 安装依赖...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo 错误: 安装依赖失败
    exit /b 1
)

echo.
echo 开始构建应用程序...
python build_app_unified.py
if %ERRORLEVEL% neq 0 (
    echo 错误: 构建应用程序失败
    exit /b 1
)

echo.
echo 构建完成！
echo 可执行文件位于dist目录中
echo.

pause 