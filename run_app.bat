@echo off
echo 启动视频编辑器应用程序...
echo.

echo 检查Python环境...
python --version
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python，请确保已安装Python并添加到PATH环境变量中
    exit /b 1
)

echo.
echo 检查依赖...
pip show PyQt5 >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 安装依赖...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo 错误: 安装依赖失败
        exit /b 1
    )
)

echo.
echo 启动应用程序...
python run.py
if %ERRORLEVEL% neq 0 (
    echo 错误: 应用程序运行失败
    exit /b 1
)

exit /b 0 