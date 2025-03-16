#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NumPy版本检查脚本
在应用程序启动前检查NumPy版本，确保与OpenCV兼容
"""

import sys
import subprocess
import importlib.util
import pkg_resources

def check_numpy_version():
    """
    检查NumPy版本，如果是2.x版本，则降级到1.x版本
    """
    try:
        # 检查NumPy是否已安装
        numpy_spec = importlib.util.find_spec("numpy")
        if numpy_spec is None:
            print("NumPy未安装，将安装兼容版本...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy<2.0.0"])
            return True
        
        # 获取NumPy版本
        import numpy
        numpy_version = numpy.__version__
        print(f"当前NumPy版本: {numpy_version}")
        
        # 检查是否为2.x版本
        if numpy_version.startswith("2."):
            print("检测到NumPy 2.x版本，与OpenCV不兼容，将降级到兼容版本...")
            
            # 卸载当前版本
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "numpy"])
            
            # 安装兼容版本
            subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy<2.0.0"])
            
            print("NumPy已降级到兼容版本")
            
            # 重新导入numpy以验证版本
            importlib.reload(numpy)
            print(f"新NumPy版本: {numpy.__version__}")
            
            return True
    except Exception as e:
        print(f"检查NumPy版本时出错: {str(e)}")
        return False
    
    return True

def check_opencv_compatibility():
    """
    检查OpenCV是否与当前NumPy版本兼容
    """
    try:
        # 尝试导入cv2
        import cv2
        print(f"OpenCV版本: {cv2.__version__}")
        return True
    except ImportError:
        print("OpenCV未安装，将安装兼容版本...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python==4.8.0.76"])
            return True
        except Exception as e:
            print(f"安装OpenCV时出错: {str(e)}")
            return False
    except AttributeError as e:
        if "_ARRAY_API not found" in str(e):
            print("检测到NumPy与OpenCV不兼容的问题，将尝试修复...")
            if check_numpy_version():
                # 再次尝试导入cv2
                try:
                    import importlib
                    if "cv2" in sys.modules:
                        del sys.modules["cv2"]
                    import cv2
                    print(f"OpenCV版本: {cv2.__version__}")
                    return True
                except Exception as e2:
                    print(f"修复后仍然无法导入OpenCV: {str(e2)}")
                    return False
        else:
            print(f"导入OpenCV时出错: {str(e)}")
            return False
    except Exception as e:
        print(f"导入OpenCV时出错: {str(e)}")
        return False

def check_dependencies():
    """
    检查所有依赖项
    """
    print("检查依赖项...")
    
    # 检查NumPy版本
    if not check_numpy_version():
        print("警告: NumPy版本检查失败")
    
    # 检查OpenCV兼容性
    if not check_opencv_compatibility():
        print("警告: OpenCV兼容性检查失败")
    
    # 检查其他依赖项
    required_packages = {
        "PyQt5": "5.15.6",
        "moviepy": "2.0.0.0",
        "pyinstaller": "6.1.0"
    }
    
    for package, version in required_packages.items():
        try:
            pkg_resources.require(f"{package}=={version}")
            print(f"{package} {version} 已安装")
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            print(f"{package} {version} 未安装或版本不匹配，将尝试安装...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package}=={version}"])
                print(f"{package} {version} 安装成功")
            except Exception as e:
                print(f"安装 {package} 时出错: {str(e)}")
    
    print("依赖项检查完成")

if __name__ == "__main__":
    check_dependencies() 