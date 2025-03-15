#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
构建脚本 - 将视频编辑器打包为可执行文件
"""

import os
import sys
import platform
import subprocess
import shutil
import site
import glob

def build_executable():
    """构建可执行文件"""
    print("开始构建视频编辑器可执行文件...")
    
    # 获取当前操作系统
    system = platform.system()
    print(f"当前操作系统: {system}")
    
    # 确保所有必要的依赖都已安装
    print("检查并安装必要的依赖...")
    try:
        # 安装PyQt5多媒体组件
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "PyQt5"], check=True)
        print("PyQt5已更新安装")
        
        # 尝试导入多媒体模块，如果失败则提示错误
        try:
            import PyQt5.QtMultimedia
            import PyQt5.QtMultimediaWidgets
            print("PyQt5多媒体模块已可用")
        except ImportError as e:
            print(f"警告: 无法导入PyQt5多媒体模块: {e}")
            print("尝试继续构建，但可能会失败...")
    except subprocess.CalledProcessError:
        print("警告: 依赖安装过程中出现错误，构建可能会失败")
    
    # 查找PyQt5库文件路径
    pyqt_paths = []
    for path in site.getsitepackages():
        qt_libs = glob.glob(os.path.join(path, "PyQt5", "Qt5", "lib", "*"))
        if qt_libs:
            pyqt_paths.extend(qt_libs)
            print(f"找到PyQt5库文件: {qt_libs}")
    
    # 清理之前的构建文件
    if os.path.exists("dist"):
        print("清理之前的构建文件...")
        shutil.rmtree("dist", ignore_errors=True)
    if os.path.exists("build"):
        shutil.rmtree("build", ignore_errors=True)
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--name=视频编辑器",
        "--windowed",  # 不显示控制台窗口
        "--clean",     # 清理临时文件
        "--noconfirm", # 不询问确认
    ]
    
    # 根据操作系统调整打包选项
    if system == "Darwin":  # macOS
        cmd.append("--onefile")  # macOS上使用单文件模式更方便
    else:
        cmd.append("--onedir")   # 其他系统使用文件夹模式
    
    # 添加图标（如果存在）
    icon_path = None
    if system == "Windows":
        icon_path = "resources/icon.ico"
    elif system == "Darwin":  # macOS
        icon_path = "resources/icon.icns"
    elif system == "Linux":
        icon_path = "resources/icon.png"
    
    if icon_path and os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
        print(f"使用图标文件: {icon_path}")
    else:
        print(f"警告: 图标文件 {icon_path} 不存在，将使用默认图标")
    
    # 添加数据文件 - 根据操作系统调整分隔符
    if system == "Windows":
        cmd.append("--add-data=video_editor_app;video_editor_app")
    else:
        cmd.append("--add-data=video_editor_app:video_editor_app")
    
    # 添加PyQt5库文件路径
    for path in pyqt_paths:
        if os.path.isdir(path):
            if system == "Windows":
                cmd.append(f"--add-data={path};{os.path.basename(path)}")
            else:
                cmd.append(f"--add-data={path}:{os.path.basename(path)}")
    
    # 添加隐藏导入，确保所有依赖都被包含
    cmd.append("--hidden-import=cv2")
    cmd.append("--hidden-import=moviepy")
    cmd.append("--hidden-import=moviepy.editor")
    cmd.append("--hidden-import=numpy")
    cmd.append("--hidden-import=PyQt5")
    cmd.append("--hidden-import=PyQt5.QtCore")
    cmd.append("--hidden-import=PyQt5.QtGui")
    cmd.append("--hidden-import=PyQt5.QtWidgets")
    # 添加多媒体模块 - 修复缺少的依赖
    cmd.append("--hidden-import=PyQt5.QtMultimedia")
    cmd.append("--hidden-import=PyQt5.QtMultimediaWidgets")
    
    # 为macOS添加特殊处理
    if system == "Darwin":
        # 添加额外的库路径
        cmd.append("--collect-all=PyQt5")
    
    # 创建spec文件
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('video_editor_app', 'video_editor_app')],
    hiddenimports=['cv2', 'moviepy', 'moviepy.editor', 'numpy', 'PyQt5', 'PyQt5.QtCore', 
                  'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.QtMultimedia', 'PyQt5.QtMultimediaWidgets'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# 添加PyQt5多媒体库
try:
    from PyQt5.QtMultimedia import QMediaPlayer
    print("成功导入QMediaPlayer")
except ImportError:
    print("警告: 无法导入QMediaPlayer")

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='视频编辑器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon_path}',
)

app = BUNDLE(
    exe,
    name='视频编辑器.app',
    icon='{icon_path}',
    bundle_identifier='com.videoeditor.app',
)
"""
    
    # 写入spec文件
    with open("视频编辑器.spec", "w") as f:
        f.write(spec_content)
    
    # 使用spec文件构建
    build_cmd = ["pyinstaller", "--clean", "--noconfirm", "视频编辑器.spec"]
    
    # 执行构建命令
    print("执行构建命令:", " ".join(build_cmd))
    try:
        subprocess.run(build_cmd, check=True)
        build_success = True
    except subprocess.CalledProcessError:
        build_success = False
        print("构建过程中发生错误")
    
    # 构建完成
    if build_success:
        if system == "Darwin" and os.path.exists("dist/视频编辑器.app"):
            print("\n构建成功!")
            print(f"可执行文件位于: {os.path.abspath('dist/视频编辑器.app')}")
            print("运行方式: 双击 dist/视频编辑器.app 应用程序")
        elif system == "Darwin" and os.path.exists("dist/视频编辑器"):
            print("\n构建成功!")
            print(f"可执行文件位于: {os.path.abspath('dist/视频编辑器')}")
            print("运行方式: 双击 dist/视频编辑器 应用程序")
        elif system != "Darwin" and os.path.exists("dist/视频编辑器"):
            print("\n构建成功!")
            print(f"可执行文件位于: {os.path.abspath('dist/视频编辑器')}")
            
            # 根据操作系统提供不同的说明
            if system == "Windows":
                print("运行方式: 双击 dist/视频编辑器/视频编辑器.exe")
            elif system == "Linux":
                print("运行方式: 从命令行运行 dist/视频编辑器/视频编辑器")
        else:
            print("\n构建可能成功，但找不到预期的输出文件。")
            print("请检查 dist 目录中的内容。")
    else:
        print("\n构建失败，请检查错误信息。")
        print("常见问题:")
        print("1. 确保已安装所有依赖: pip install -r requirements.txt")
        print("2. 确保 PyInstaller 已正确安装: pip install --upgrade pyinstaller")
        print("3. 如果使用虚拟环境，确保已激活")
        print("4. 对于macOS用户，可能需要安装额外的PyQt5组件: pip install --force-reinstall PyQt5")
        print("5. 尝试手动安装PyQt5多媒体组件: brew install qt5")

if __name__ == "__main__":
    build_executable() 