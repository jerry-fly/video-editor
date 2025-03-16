#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本地测试脚本
用于在本地环境中测试视频编辑器应用程序的各项功能
"""

import os
import sys
import platform
import importlib.util
from datetime import datetime

def check_dependencies():
    """检查必要的依赖是否已安装"""
    required_packages = [
        "PyQt5", "cv2", "moviepy", "numpy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    return missing_packages

def test_import_modules():
    """测试导入模块"""
    try:
        from video_editor_app.main import MainWindow
        from video_editor_app.clip_tab import VideoClipTab
        from video_editor_app.merge_tab import VideoMergeTab
        print("✅ 模块导入测试通过")
        return True
    except ImportError as e:
        print(f"❌ 模块导入测试失败: {str(e)}")
        return False

def test_run_app():
    """测试运行应用程序"""
    try:
        # 尝试导入主模块
        from video_editor_app.main import MainWindow
        from PyQt5.QtWidgets import QApplication
        
        # 创建应用程序实例，但不显示窗口
        app = QApplication([])
        window = MainWindow()
        
        print("✅ 应用程序初始化测试通过")
        return True
    except Exception as e:
        print(f"❌ 应用程序初始化测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print(f"本地测试脚本 - 视频编辑器")
    print(f"当前平台: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 检查依赖
    missing_packages = check_dependencies()
    if missing_packages:
        print(f"❌ 缺少必要的依赖: {', '.join(missing_packages)}")
        print("请安装缺少的依赖: pip install " + " ".join(missing_packages))
        return 1
    else:
        print("✅ 依赖检查通过")
    
    # 测试导入模块
    if not test_import_modules():
        return 1
    
    # 测试运行应用程序
    if not test_run_app():
        return 1
    
    print("-" * 50)
    print("✅ 所有测试通过!")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 