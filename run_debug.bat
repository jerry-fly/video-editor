@echo off
chcp 65001 > nul
echo ============================================================
echo 运行调试版本视频编辑器
echo ============================================================
echo.

if exist "dist\VideoEditor_Debug\VideoEditor_Debug.exe" (
    echo 找到调试版本可执行文件，开始运行...
    echo.
    cd dist\VideoEditor_Debug
    VideoEditor_Debug.exe
    cd ..\..
) else (
    echo 未找到调试版本可执行文件，请先运行 build_debug.bat 构建
    echo.
    pause
    exit /b 1
)

echo.
echo 应用程序已退出
echo 如果遇到问题，请查看日志文件了解详细信息
echo.
pause 