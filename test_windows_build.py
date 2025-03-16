#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windows构建测试脚本
用于测试应用程序在Windows环境中的构建和运行
"""

import os
import sys
import platform
import subprocess
from datetime import datetime

def check_platform():
    """检查当前平台是否为Windows"""
    if platform.system() != "Windows":
        print("❌ 此脚本只能在Windows平台上运行")
        return False
    return True

def check_dependencies():
    """检查必要的依赖是否已安装"""
    try:
        # 检查PyInstaller
        subprocess.run(["pyinstaller", "--version"], check=True, stdout=subprocess.PIPE)
        print("✅ PyInstaller已安装")
        
        # 检查Python包
        import PyQt5
        import cv2
        import moviepy
        import numpy
        
        print("✅ 所有必要的Python包已安装")
        return True
    except (ImportError, subprocess.CalledProcessError) as e:
        print(f"❌ 依赖检查失败: {str(e)}")
        return False

def build_application():
    """构建应用程序"""
    try:
        print("开始构建应用程序...")
        subprocess.run(["python", "build_app_unified.py"], check=True)
        print("✅ 应用程序构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 应用程序构建失败: {str(e)}")
        return False

def test_executable():
    """测试可执行文件"""
    exe_path = os.path.join("dist", "视频编辑器.exe")
    if not os.path.exists(exe_path):
        print(f"❌ 可执行文件不存在: {exe_path}")
        return False
    
    print(f"✅ 可执行文件已生成: {exe_path}")
    print("请手动运行可执行文件进行测试")
    return True

def main():
    """主函数"""
    print(f"Windows构建测试脚本 - 视频编辑器")
    print(f"当前平台: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 检查平台
    if not check_platform():
        return 1
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    # 构建应用程序
    if not build_application():
        return 1
    
    # 测试可执行文件
    if not test_executable():
        return 1
    
    print("-" * 50)
    print("✅ Windows构建测试完成!")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 