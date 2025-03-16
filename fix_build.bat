@echo off
chcp 65001 > nul
echo ============================================================
echo PyInstaller打包修复工具
echo ============================================================
echo.
echo 此批处理文件将修复PyInstaller打包时可能遇到的问题
echo 请确保您有管理员权限运行此脚本
echo.
echo 按任意键开始修复...
pause > nul

echo.
echo 运行修复脚本...
python fix_pyinstaller.py

echo.
echo 修复完成！
echo 如果构建成功，请尝试运行 dist/VideoEditor/VideoEditor.exe 或 dist/VideoEditor/start.bat
echo.
pause 