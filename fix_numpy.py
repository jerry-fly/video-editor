#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NumPy和OpenCV兼容性修复脚本
用于解决NumPy 2.x与OpenCV的兼容性问题
"""

import sys
import os
import subprocess
import time

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

def fix_numpy():
    """修复NumPy版本"""
    print_header("开始修复NumPy版本")
    
    # 卸载所有版本的NumPy
    print("卸载所有版本的NumPy...")
    run_command([sys.executable, "-m", "pip", "uninstall", "-y", "numpy"])
    run_command([sys.executable, "-m", "pip", "uninstall", "-y", "numpy"])
    
    # 安装兼容版本
    print("\n安装兼容版本的NumPy...")
    success = run_command([sys.executable, "-m", "pip", "install", "numpy==1.24.3", "--force-reinstall"])
    
    if not success:
        print("尝试安装备用版本...")
        success = run_command([sys.executable, "-m", "pip", "install", "numpy==1.23.5", "--force-reinstall"])
    
    if success:
        print("\nNumPy版本修复成功!")
    else:
        print("\n警告: NumPy版本修复可能不完整")
    
    return success

def fix_opencv():
    """修复OpenCV"""
    print_header("开始修复OpenCV")
    
    # 卸载所有版本的OpenCV
    print("卸载所有版本的OpenCV...")
    run_command([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python"])
    run_command([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python-headless"])
    
    # 安装兼容版本
    print("\n安装兼容版本的OpenCV...")
    success = run_command([sys.executable, "-m", "pip", "install", "opencv-python==4.8.0.76", "--force-reinstall"])
    
    if success:
        print("\nOpenCV修复成功!")
    else:
        print("\n警告: OpenCV修复可能不完整")
    
    return success

def fix_all_dependencies():
    """修复所有依赖项"""
    print_header("开始修复所有依赖项")
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(current_dir, "requirements.txt")
    
    if os.path.exists(requirements_file):
        print(f"从{requirements_file}安装依赖项...")
        success = run_command([sys.executable, "-m", "pip", "install", "-r", requirements_file, "--force-reinstall"])
        
        if success:
            print("\n所有依赖项修复成功!")
        else:
            print("\n警告: 依赖项修复可能不完整")
    else:
        print(f"错误: 未找到requirements.txt文件")
        return False
    
    return success

def verify_installation():
    """验证安装"""
    print_header("验证安装")
    
    # 验证NumPy
    print("验证NumPy...")
    try:
        import numpy
        print(f"NumPy版本: {numpy.__version__}")
        if numpy.__version__.startswith("2."):
            print("警告: 仍然使用NumPy 2.x版本，可能与OpenCV不兼容")
            return False
    except ImportError:
        print("错误: NumPy未安装")
        return False
    except Exception as e:
        print(f"验证NumPy时出错: {str(e)}")
        return False
    
    # 验证OpenCV
    print("\n验证OpenCV...")
    try:
        import cv2
        print(f"OpenCV版本: {cv2.__version__}")
    except ImportError:
        print("错误: OpenCV未安装")
        return False
    except AttributeError as e:
        if "_ARRAY_API not found" in str(e):
            print("错误: 仍然存在NumPy与OpenCV的兼容性问题")
            return False
        else:
            print(f"验证OpenCV时出错: {str(e)}")
            return False
    except Exception as e:
        print(f"验证OpenCV时出错: {str(e)}")
        return False
    
    # 验证PyQt5
    print("\n验证PyQt5...")
    try:
        import PyQt5
        print(f"PyQt5已安装")
    except ImportError:
        print("错误: PyQt5未安装")
        return False
    except Exception as e:
        print(f"验证PyQt5时出错: {str(e)}")
        return False
    
    # 验证moviepy
    print("\n验证moviepy...")
    try:
        import moviepy
        print(f"moviepy已安装")
    except ImportError:
        print("错误: moviepy未安装")
        return False
    except Exception as e:
        print(f"验证moviepy时出错: {str(e)}")
        return False
    
    print("\n所有依赖项验证通过!")
    return True

def main():
    """主函数"""
    print_header("NumPy和OpenCV兼容性修复工具")
    print("此工具将修复NumPy 2.x与OpenCV的兼容性问题")
    print("请确保您有管理员权限运行此脚本")
    
    # 修复NumPy
    numpy_fixed = fix_numpy()
    time.sleep(1)  # 等待一会儿，确保安装完成
    
    # 修复OpenCV
    opencv_fixed = fix_opencv()
    time.sleep(1)  # 等待一会儿，确保安装完成
    
    # 修复所有依赖项
    all_fixed = fix_all_dependencies()
    time.sleep(1)  # 等待一会儿，确保安装完成
    
    # 验证安装
    verified = verify_installation()
    
    print_header("修复结果")
    print(f"NumPy修复: {'成功' if numpy_fixed else '失败'}")
    print(f"OpenCV修复: {'成功' if opencv_fixed else '失败'}")
    print(f"所有依赖项修复: {'成功' if all_fixed else '失败'}")
    print(f"验证结果: {'通过' if verified else '失败'}")
    
    if verified:
        print("\n修复成功! 现在您可以运行应用程序了。")
    else:
        print("\n修复可能不完整，请尝试以下步骤:")
        print("1. 手动卸载NumPy: pip uninstall numpy")
        print("2. 手动安装兼容版本: pip install numpy==1.24.3")
        print("3. 手动卸载OpenCV: pip uninstall opencv-python")
        print("4. 手动安装兼容版本: pip install opencv-python==4.8.0.76")
        print("5. 重新运行应用程序")
    
    input("\n按Enter键退出...")

if __name__ == "__main__":
    main() 