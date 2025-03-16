@echo off
chcp 65001 > nul
echo ============================================================
echo 构建调试版本视频编辑器应用程序
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
echo 运行依赖检查脚本...
python check_numpy.py
if %ERRORLEVEL% neq 0 (
    echo 警告: 依赖检查失败，将尝试继续...
)

echo.
echo 安装依赖项...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo 错误: 安装依赖项失败
    pause
    exit /b 1
)

echo.
echo 确保NumPy版本兼容...
pip install numpy==1.24.3 --force-reinstall
if %ERRORLEVEL% neq 0 (
    echo 警告: NumPy安装失败，将尝试继续...
)

echo.
echo 开始构建调试版本应用程序...
python -c "import sys; from PyInstaller.__main__ import run; sys.argv = ['pyinstaller', '--name=VideoEditor_Debug', '--console', '--add-data=resources;resources', 'run.py']; run()"
if %ERRORLEVEL% neq 0 (
    echo 错误: 构建应用程序失败
    pause
    exit /b 1
)

echo.
echo 调试版本构建完成!
echo 可执行文件位于dist目录中: VideoEditor_Debug.exe
echo 请运行此文件并查看控制台输出以诊断问题
echo.

pause 