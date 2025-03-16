@echo off
chcp 65001 > nul
echo 启动视频编辑器应用程序...
echo.

echo 检查Python环境...
python --version
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo.
echo 检查依赖...

:: 运行依赖检查脚本
python check_numpy.py
if %ERRORLEVEL% neq 0 (
    echo 警告: 依赖检查失败，将尝试继续...
)

:: 确保安装了所有依赖
pip show PyQt5 >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 安装依赖...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo 错误: 安装依赖失败
        pause
        exit /b 1
    )
) else (
    :: 确保numpy是兼容版本
    pip install numpy<2.0.0 -U
)

echo.
echo 修复模块导入路径...
python fix_module_path.py
if %ERRORLEVEL% neq 0 (
    echo 警告: 模块路径修复失败，将尝试继续...
)

echo.
echo 启动应用程序...
python run_fixed.py
if %ERRORLEVEL% neq 0 (
    echo 错误: 应用程序运行失败
    
    echo 尝试使用原始脚本运行...
    python run.py
    if %ERRORLEVEL% neq 0 (
        echo 错误: 应用程序运行失败
        pause
        exit /b 1
    )
)

exit /b 0 