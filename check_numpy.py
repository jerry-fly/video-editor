#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NumPy版本检查脚本
在应用程序启动前检查NumPy版本，确保与OpenCV兼容
"""

import sys
import os
import subprocess
import importlib.util
import pkg_resources
import time

def force_uninstall_numpy():
    """
    强制卸载所有版本的NumPy
    """
    print("强制卸载所有版本的NumPy...")
    try:
        # 尝试多次卸载以确保完全移除
        for _ in range(3):
            subprocess.call([sys.executable, "-m", "pip", "uninstall", "-y", "numpy"])
    except Exception as e:
        print(f"卸载NumPy时出错: {str(e)}")

def install_compatible_numpy():
    """
    安装兼容的NumPy版本
    """
    print("安装兼容的NumPy版本...")
    try:
        # 使用--force-reinstall确保完全重新安装
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.24.3", "--force-reinstall"])
        print("NumPy 1.24.3 安装成功")
        return True
    except Exception as e:
        print(f"安装NumPy时出错: {str(e)}")
        # 尝试备用版本
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.23.5", "--force-reinstall"])
            print("NumPy 1.23.5 安装成功")
            return True
        except Exception as e2:
            print(f"安装备用NumPy版本时出错: {str(e2)}")
            return False

def check_numpy_version():
    """
    检查NumPy版本，如果是2.x版本，则降级到1.x版本
    """
    try:
        # 检查NumPy是否已安装
        numpy_spec = importlib.util.find_spec("numpy")
        if numpy_spec is None:
            print("NumPy未安装，将安装兼容版本...")
            return install_compatible_numpy()
        
        # 获取NumPy版本
        import numpy
        numpy_version = numpy.__version__
        print(f"当前NumPy版本: {numpy_version}")
        
        # 检查是否为2.x版本或其他不兼容版本
        if numpy_version.startswith("2.") or float(numpy_version.split('.')[0]) > 1:
            print("检测到NumPy 2.x或更高版本，与OpenCV不兼容，将降级到兼容版本...")
            
            # 强制卸载所有版本的NumPy
            force_uninstall_numpy()
            
            # 安装兼容版本
            if not install_compatible_numpy():
                return False
            
            # 清除sys.modules中的numpy相关模块
            for module_name in list(sys.modules.keys()):
                if module_name.startswith('numpy'):
                    del sys.modules[module_name]
            
            # 重新导入numpy以验证版本
            import numpy
            importlib.reload(numpy)
            print(f"新NumPy版本: {numpy.__version__}")
            
            return True
    except Exception as e:
        print(f"检查NumPy版本时出错: {str(e)}")
        # 出错时尝试强制重装
        force_uninstall_numpy()
        return install_compatible_numpy()
    
    return True

def reinstall_opencv():
    """
    重新安装OpenCV
    """
    print("重新安装OpenCV...")
    try:
        # 卸载现有OpenCV
        subprocess.call([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python"])
        subprocess.call([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python-headless"])
        
        # 安装指定版本
        subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python==4.8.0.76", "--force-reinstall"])
        print("OpenCV 4.8.0.76 安装成功")
        return True
    except Exception as e:
        print(f"重新安装OpenCV时出错: {str(e)}")
        return False

def check_opencv_compatibility():
    """
    检查OpenCV是否与当前NumPy版本兼容
    """
    # 清除sys.modules中的cv2相关模块
    for module_name in list(sys.modules.keys()):
        if module_name.startswith('cv2'):
            del sys.modules[module_name]
    
    try:
        # 尝试导入cv2
        import cv2
        print(f"OpenCV版本: {cv2.__version__}")
        return True
    except ImportError:
        print("OpenCV未安装，将安装兼容版本...")
        return reinstall_opencv()
    except AttributeError as e:
        if "_ARRAY_API not found" in str(e):
            print("检测到NumPy与OpenCV不兼容的问题，将尝试修复...")
            
            # 先确保NumPy版本正确
            if not check_numpy_version():
                print("NumPy版本修复失败")
                return False
            
            # 然后重新安装OpenCV
            if not reinstall_opencv():
                print("OpenCV重新安装失败")
                return False
            
            # 再次尝试导入cv2
            try:
                # 清除sys.modules中的cv2相关模块
                for module_name in list(sys.modules.keys()):
                    if module_name.startswith('cv2'):
                        del sys.modules[module_name]
                
                import cv2
                print(f"修复后的OpenCV版本: {cv2.__version__}")
                return True
            except Exception as e2:
                print(f"修复后仍然无法导入OpenCV: {str(e2)}")
                return False
        else:
            print(f"导入OpenCV时出错: {str(e)}")
            return reinstall_opencv()
    except Exception as e:
        print(f"导入OpenCV时出错: {str(e)}")
        return reinstall_opencv()

def create_numpy_patch():
    """
    创建一个临时补丁文件，在导入cv2前强制设置正确的NumPy版本
    """
    patch_content = """
# NumPy补丁，确保在导入cv2前使用兼容的NumPy版本
import sys
import importlib

# 检查NumPy版本
try:
    import numpy
    numpy_version = numpy.__version__
    if numpy_version.startswith('2.'):
        print(f"警告: 检测到NumPy {numpy_version}，可能与OpenCV不兼容")
        print("尝试使用预安装的NumPy 1.x版本...")
        
        # 从sys.modules中移除numpy
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('numpy'):
                del sys.modules[module_name]
        
        # 尝试导入兼容版本
        try:
            import numpy
            print(f"使用NumPy版本: {numpy.__version__}")
        except ImportError:
            print("无法导入兼容的NumPy版本")
except ImportError:
    print("NumPy未安装")
except Exception as e:
    print(f"检查NumPy版本时出错: {str(e)}")
"""
    
    # 创建补丁文件
    patch_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "numpy_patch.py")
    with open(patch_file, "w", encoding="utf-8") as f:
        f.write(patch_content)
    
    print(f"NumPy补丁文件已创建: {patch_file}")
    return patch_file

def check_dependencies():
    """
    检查所有依赖项
    """
    print("=" * 50)
    print("开始全面依赖项检查...")
    print("=" * 50)
    
    # 创建NumPy补丁
    create_numpy_patch()
    
    # 检查NumPy版本
    if not check_numpy_version():
        print("警告: NumPy版本检查失败，将尝试继续...")
    else:
        print("NumPy版本检查通过")
    
    # 等待一会儿，确保NumPy安装完成
    time.sleep(2)
    
    # 检查OpenCV兼容性
    if not check_opencv_compatibility():
        print("警告: OpenCV兼容性检查失败，将尝试继续...")
    else:
        print("OpenCV兼容性检查通过")
    
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
    
    print("=" * 50)
    print("依赖项检查完成")
    print("=" * 50)
    
    # 最后再次验证NumPy版本
    try:
        import numpy
        print(f"最终NumPy版本: {numpy.__version__}")
    except Exception as e:
        print(f"验证NumPy版本时出错: {str(e)}")

if __name__ == "__main__":
    check_dependencies() 