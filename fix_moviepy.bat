@echo off
rem 设置UTF-8编码
chcp 65001 > nul

echo ============================================================
echo 修复 moviepy.editor 模块导入问题
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
echo 正在修复moviepy.editor模块...
python fix_moviepy.py
if %ERRORLEVEL% neq 0 (
    echo 警告: moviepy修复失败，将尝试继续运行...
) else (
    echo moviepy.editor模块修复成功！
)

echo.
echo 修复完成，现在可以尝试重新运行视频编辑器
echo 请运行 safe_run.bat 或 safe_run_en.bat 启动应用程序
echo.
pause 