#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windows平台构建脚本
用于在Windows系统上构建视频编辑器的独立可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """清理构建目录"""
    print("清理构建目录...")
    
    # 清理build目录
    if os.path.exists("build"):
        shutil.rmtree("build")
        
    # 清理dist目录
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        
    # 清理spec文件
    if os.path.exists("视频编辑器.spec"):
        os.remove("视频编辑器.spec")
        
    print("清理完成")

def build_executable():
    """构建Windows可执行文件"""
    print("开始构建Windows可执行文件...")
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--name=视频编辑器",
        "--windowed",  # 使用窗口模式，不显示控制台
        "--onefile",   # 生成单个可执行文件
        "--clean",     # 清理临时文件
        "--noconfirm", # 不询问确认
    ]
    
    # 添加图标
    icon_path = os.path.join("resources", "icon.ico")
    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
    else:
        print(f"警告: 图标文件 {icon_path} 不存在，将使用默认图标")
    
    # 添加隐藏导入
    cmd.append("--hidden-import=cv2")
    cmd.append("--hidden-import=moviepy")
    cmd.append("--hidden-import=numpy")
    cmd.append("--hidden-import=PyQt5")
    cmd.append("--hidden-import=PyQt5.QtCore")
    cmd.append("--hidden-import=PyQt5.QtGui")
    cmd.append("--hidden-import=PyQt5.QtWidgets")
    cmd.append("--hidden-import=PyQt5.QtMultimedia")
    cmd.append("--hidden-import=PyQt5.QtMultimediaWidgets")
    
    # 添加数据文件
    # 如果有需要包含的数据文件，可以在这里添加
    # cmd.append("--add-data=data;data")
    
    # 添加主脚本
    cmd.append("run.py")
    
    # 执行构建命令
    print("执行命令:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    
    print("构建完成")

def create_zip_package():
    """创建ZIP包"""
    print("创建ZIP包...")
    
    # 检查dist目录是否存在
    if not os.path.exists("dist"):
        print("错误: dist目录不存在，构建可能失败")
        return
    
    # 检查可执行文件是否存在
    exe_path = os.path.join("dist", "视频编辑器.exe")
    if not os.path.exists(exe_path):
        print(f"错误: 可执行文件 {exe_path} 不存在")
        return
    
    # 创建ZIP包
    zip_name = "视频编辑器_v1.0.0_Windows.zip"
    
    # 使用powershell的Compress-Archive命令创建ZIP包
    cmd = [
        "powershell",
        "-Command",
        f"Compress-Archive -Path '{exe_path}' -DestinationPath '{zip_name}' -Force"
    ]
    
    print("执行命令:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    
    print(f"ZIP包创建完成: {zip_name}")

def main():
    """主函数"""
    print("Windows平台构建脚本")
    
    # 检查是否在Windows平台上运行
    if sys.platform != "win32":
        print("错误: 此脚本只能在Windows平台上运行")
        return
    
    # 清理构建目录
    clean_build_dirs()
    
    # 构建可执行文件
    build_executable()
    
    # 创建ZIP包
    create_zip_package()
    
    print("所有操作完成")

if __name__ == "__main__":
    main() 