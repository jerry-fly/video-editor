#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyInstaller打包修复脚本
用于解决PyInstaller打包时可能遇到的问题
"""

import os
import sys
import shutil
import subprocess
import platform
import time
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

def print_header(message):
    """打印带有分隔符的标题"""
    print("\n" + "=" * 60)
    print(message)
    print("=" * 60)

def run_command(command):
    """运行命令并返回结果"""
    print(f"执行命令: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"错误: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"执行命令时出错: {str(e)}")
        return False

def fix_numpy_opencv():
    """修复NumPy和OpenCV"""
    print_header("修复NumPy和OpenCV")
    
    # 卸载所有版本的NumPy
    print("卸载所有版本的NumPy...")
    run_command([sys.executable, "-m", "pip", "uninstall", "-y", "numpy"])
    
    # 安装兼容版本
    print("\n安装兼容版本的NumPy...")
    success = run_command([sys.executable, "-m", "pip", "install", "numpy==1.24.3", "--force-reinstall"])
    
    # 卸载所有版本的OpenCV
    print("\n卸载所有版本的OpenCV...")
    run_command([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python"])
    run_command([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python-headless"])
    
    # 安装兼容版本
    print("\n安装兼容版本的OpenCV...")
    success = run_command([sys.executable, "-m", "pip", "install", "opencv-python==4.8.0.76", "--force-reinstall"])
    
    return success

def fix_pyinstaller():
    """修复PyInstaller"""
    print_header("修复PyInstaller")
    
    # 卸载PyInstaller
    print("卸载PyInstaller...")
    run_command([sys.executable, "-m", "pip", "uninstall", "-y", "pyinstaller"])
    
    # 安装最新版本
    print("\n安装最新版本的PyInstaller...")
    success = run_command([sys.executable, "-m", "pip", "install", "pyinstaller==6.1.0", "--force-reinstall"])
    
    return success

def create_spec_file():
    """创建自定义spec文件"""
    print_header("创建自定义spec文件")
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

# 防止递归导入
sys.setrecursionlimit(1000)

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('resources', 'resources')],
    hiddenimports=[
        'numpy', 'cv2', 'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
        'PyQt5.QtMultimedia', 'PyQt5.QtMultimediaWidgets', 'moviepy', 'moviepy.editor',
        'video_editor_app', 'video_editor_app.main', 'video_editor_app.clip_tab',
        'video_editor_app.merge_tab', 'video_editor_app.convert_tab'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'tkinter', 'PySide2', 'PySide6', 'PyQt6'],  # 排除不需要的模块
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 清理不必要的二进制文件和库，减小体积
a.binaries = [x for x in a.binaries if not x[0].startswith('matplotlib')]
a.binaries = [x for x in a.binaries if not x[0].startswith('tcl')]
a.binaries = [x for x in a.binaries if not x[0].startswith('tk')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VideoEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 保留控制台窗口以便查看错误信息
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VideoEditor',
)
"""
    
    # 写入spec文件
    with open("VideoEditor.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("自定义spec文件已创建: VideoEditor.spec")
    return True

def build_with_spec():
    """使用自定义spec文件构建"""
    print_header("使用自定义spec文件构建")
    
    # 清理旧的构建文件
    if os.path.exists("build"):
        print("清理build目录...")
        shutil.rmtree("build")
    
    if os.path.exists("dist"):
        print("清理dist目录...")
        shutil.rmtree("dist")
    
    # 使用spec文件构建
    print("\n开始构建...")
    success = run_command([sys.executable, "-m", "PyInstaller", "VideoEditor.spec"])
    
    if success:
        print("\n构建成功!")
        print("可执行文件位于: dist/VideoEditor/VideoEditor.exe")
    else:
        print("\n构建失败!")
    
    return success

def copy_dependencies():
    """复制额外的依赖文件到dist目录"""
    print_header("复制额外的依赖文件")
    
    dist_dir = os.path.join("dist", "VideoEditor")
    if not os.path.exists(dist_dir):
        print(f"错误: 目录不存在: {dist_dir}")
        return False
    
    # 复制check_numpy.py
    print("复制check_numpy.py...")
    shutil.copy("check_numpy.py", os.path.join(dist_dir, "check_numpy.py"))
    
    # 复制requirements.txt
    if os.path.exists("requirements.txt"):
        print("复制requirements.txt...")
        shutil.copy("requirements.txt", os.path.join(dist_dir, "requirements.txt"))
    
    # 创建一个简单的启动脚本
    print("创建启动脚本...")
    with open(os.path.join(dist_dir, "start.bat"), "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("echo 启动视频编辑器...\n")
        f.write("VideoEditor.exe\n")
        f.write("if %ERRORLEVEL% neq 0 (\n")
        f.write("    echo 应用程序启动失败\n")
        f.write("    pause\n")
        f.write(")\n")
    
    print("依赖文件复制完成")
    return True

def main():
    """主函数"""
    print_header("PyInstaller打包修复工具")
    print("此工具将修复PyInstaller打包时可能遇到的问题")
    print("请确保您有管理员权限运行此脚本")
    
    # 修复NumPy和OpenCV
    fix_numpy_opencv()
    time.sleep(1)
    
    # 修复PyInstaller
    fix_pyinstaller()
    time.sleep(1)
    
    # 创建自定义spec文件
    create_spec_file()
    
    # 使用自定义spec文件构建
    build_success = build_with_spec()
    
    if build_success:
        # 复制额外的依赖文件
        copy_dependencies()
        
        print_header("构建完成")
        print("请尝试运行 dist/VideoEditor/VideoEditor.exe 或 dist/VideoEditor/start.bat")
        print("如果仍然遇到问题，请查看日志文件了解详细信息")
    else:
        print_header("构建失败")
        print("请检查错误信息并尝试手动解决问题")
    
    input("\n按Enter键退出...")

if __name__ == "__main__":
    main() 