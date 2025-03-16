#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一构建脚本
支持在Windows、macOS和Linux平台上构建视频编辑器的独立可执行文件
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# 应用版本号
APP_VERSION = "1.0.0"
APP_NAME = "视频编辑器"

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
    spec_file = f"{APP_NAME}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        
    print("清理完成")

def get_platform_info():
    """获取平台信息"""
    system = platform.system()
    if system == "Windows":
        return {
            "name": "Windows",
            "icon": os.path.join("resources", "icon.ico"),
            "separator": ";",
            "exe_ext": ".exe",
            "zip_cmd": ["powershell", "-Command"],
            "zip_args": lambda src, dst: [f"Compress-Archive -Path '{src}' -DestinationPath '{dst}' -Force"]
        }
    elif system == "Darwin":  # macOS
        return {
            "name": "macOS",
            "icon": os.path.join("resources", "icon.icns"),
            "separator": ":",
            "exe_ext": ".app",
            "zip_cmd": ["zip", "-r"],
            "zip_args": lambda src, dst: [dst, src]
        }
    elif system == "Linux":
        return {
            "name": "Linux",
            "icon": os.path.join("resources", "icon.png"),
            "separator": ":",
            "exe_ext": "",
            "zip_cmd": ["zip", "-r"],
            "zip_args": lambda src, dst: [dst, src]
        }
    else:
        raise ValueError(f"不支持的操作系统: {system}")

def build_executable():
    """构建可执行文件"""
    platform_info = get_platform_info()
    platform_name = platform_info["name"]
    
    print(f"开始构建{platform_name}可执行文件...")
    
    # 构建命令
    cmd = [
        "pyinstaller",
        f"--name={APP_NAME}",
        "--windowed",  # 使用窗口模式，不显示控制台
        "--clean",     # 清理临时文件
        "--noconfirm", # 不询问确认
    ]
    
    # 根据平台添加特定选项
    if platform_name == "Windows" or platform_name == "Linux":
        cmd.append("--onefile")  # Windows和Linux使用单文件模式
    
    # 添加图标
    icon_path = platform_info["icon"]
    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
    else:
        print(f"警告: 图标文件 {icon_path} 不存在，将使用默认图标")
    
    # 添加隐藏导入
    hidden_imports = [
        "cv2", "moviepy", "numpy", 
        "PyQt5", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets",
        "PyQt5.QtMultimedia", "PyQt5.QtMultimediaWidgets"
    ]
    
    for imp in hidden_imports:
        cmd.append(f"--hidden-import={imp}")
    
    # 添加数据文件
    # 如果有需要包含的数据文件，可以在这里添加
    # data_files = [("path/to/data", "data")]
    # for src, dst in data_files:
    #     cmd.append(f"--add-data={src}{platform_info['separator']}{dst}")
    
    # 添加主脚本
    cmd.append("run.py")
    
    # 执行构建命令
    print("执行命令:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    
    print("构建完成")
    return platform_info

def create_zip_package(platform_info):
    """创建ZIP包"""
    platform_name = platform_info["name"]
    print(f"创建{platform_name} ZIP包...")
    
    # 检查dist目录是否存在
    if not os.path.exists("dist"):
        print("错误: dist目录不存在，构建可能失败")
        return
    
    # 确定可执行文件路径
    if platform_name == "Windows":
        exe_path = os.path.join("dist", f"{APP_NAME}{platform_info['exe_ext']}")
    elif platform_name == "macOS":
        exe_path = os.path.join("dist", f"{APP_NAME}{platform_info['exe_ext']}")
    elif platform_name == "Linux":
        exe_path = os.path.join("dist", APP_NAME)
    
    # 检查可执行文件是否存在
    if not os.path.exists(exe_path):
        print(f"错误: 可执行文件 {exe_path} 不存在")
        return
    
    # 创建ZIP包
    zip_name = f"{APP_NAME}_v{APP_VERSION}_{platform_name}.zip"
    
    # 使用平台特定的命令创建ZIP包
    cmd = platform_info["zip_cmd"] + platform_info["zip_args"](exe_path, zip_name)
    
    print("执行命令:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    
    print(f"ZIP包创建完成: {zip_name}")

def create_source_package():
    """创建源代码包"""
    print("创建源代码包...")
    
    # 要包含的文件和目录
    files_to_include = [
        "run.py",
        "video_editor_app/",
        "requirements.txt",
        "build_app_unified.py",
        "README.md",
        "LICENSE",
        "RELEASE_NOTES.md",
        "resources/"
    ]
    
    # 创建ZIP包
    zip_name = f"{APP_NAME}_v{APP_VERSION}_源代码.zip"
    
    # 使用zip命令创建ZIP包
    if platform.system() == "Windows":
        # Windows使用PowerShell
        files_str = "', '".join(files_to_include)
        cmd = [
            "powershell",
            "-Command",
            f"Compress-Archive -Path '{files_str}' -DestinationPath '{zip_name}' -Force"
        ]
    else:
        # macOS和Linux使用zip命令
        cmd = ["zip", "-r", zip_name] + files_to_include
    
    print("执行命令:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    
    print(f"源代码包创建完成: {zip_name}")

def main():
    """主函数"""
    print(f"统一构建脚本 - {APP_NAME} v{APP_VERSION}")
    print(f"当前平台: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 清理构建目录
    clean_build_dirs()
    
    try:
        # 构建可执行文件
        platform_info = build_executable()
        
        # 创建ZIP包
        create_zip_package(platform_info)
        
        # 创建源代码包
        create_source_package()
        
        print("-" * 50)
        print(f"所有操作完成，结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"生成的文件:")
        print(f"1. {APP_NAME}_v{APP_VERSION}_{platform_info['name']}.zip")
        print(f"2. {APP_NAME}_v{APP_VERSION}_源代码.zip")
        
    except Exception as e:
        print(f"构建过程中发生错误: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 