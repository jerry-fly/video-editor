@echo off
chcp 65001 > nul
echo ============================================================
echo NumPy和OpenCV兼容性修复工具
echo ============================================================
echo.
echo 此批处理文件将修复NumPy 2.x与OpenCV的兼容性问题
echo 请确保您有管理员权限运行此脚本
echo.
echo 按任意键开始修复...
pause > nul

echo.
echo 运行修复脚本...
python fix_numpy.py

echo.
echo 修复完成！
echo 现在您可以尝试运行应用程序了。
echo.
pause 