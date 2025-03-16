#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
依赖安装脚本
此脚本用于安装视频编辑器应用程序所需的所有依赖
"""

import os
import sys
import subprocess
import logging
import platform
import traceback

def setup_logging():
    """设置日志记录"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception:
            log_dir = os.path.dirname(os.path.abspath(__file__))

    log_file = os.path.join(log_dir, "install_dependencies.log")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("DependencyInstaller")

def check_python_version():
    """检查Python版本"""
    logger = logging.getLogger("DependencyInstaller")
    
    # 获取Python版本
    python_version = platform.python_version()
    logger.info(f"Python版本: {python_version}")
    
    # 检查Python版本是否满足要求
    major, minor, _ = map(int, python_version.split('.'))
    if major < 3 or (major == 3 and minor < 6):
        logger.error(f"Python版本过低: {python_version}，需要Python 3.6或更高版本")
        return False
    
    return True

def install_pip():
    """确保pip已安装"""
    logger = logging.getLogger("DependencyInstaller")
    
    try:
        # 检查pip是否已安装
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("pip已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("pip未安装，尝试安装...")
        
        try:
            # 下载get-pip.py
            import urllib.request
            urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
            
            # 安装pip
            subprocess.run([sys.executable, "get-pip.py"], check=True)
            
            # 清理
            if os.path.exists("get-pip.py"):
                os.remove("get-pip.py")
            
            logger.info("pip安装成功")
            return True
        except Exception as e:
            logger.error(f"安装pip时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            return False

def upgrade_pip():
    """升级pip到最新版本"""
    logger = logging.getLogger("DependencyInstaller")
    
    try:
        logger.info("升级pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        logger.info("pip升级成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"升级pip时出错: {str(e)}")
        return False

def install_dependencies():
    """安装所有必要的依赖"""
    logger = logging.getLogger("DependencyInstaller")
    
    # 基本依赖列表
    dependencies = [
        "PyQt5",
        "numpy<2.0.0",  # 限制numpy版本，避免与OpenCV不兼容
        "opencv-python",
        "moviepy",
        "psutil",
        "pillow",
        "requests"
    ]
    
    # 尝试安装每个依赖
    success = True
    for dep in dependencies:
        try:
            logger.info(f"安装 {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            logger.info(f"{dep} 安装成功")
        except subprocess.CalledProcessError as e:
            logger.error(f"安装 {dep} 时出错: {str(e)}")
            success = False
    
    return success

def check_dependencies():
    """检查依赖是否已安装"""
    logger = logging.getLogger("DependencyInstaller")
    
    # 检查每个依赖
    dependencies = {
        "PyQt5": "PyQt5",
        "numpy": "numpy",
        "opencv-python": "cv2",
        "moviepy": "moviepy",
        "psutil": "psutil",
        "pillow": "PIL",
        "requests": "requests"
    }
    
    missing_deps = []
    for package, module in dependencies.items():
        try:
            __import__(module)
            logger.info(f"{package} 已安装")
        except ImportError:
            logger.warning(f"{package} 未安装")
            missing_deps.append(package)
    
    return missing_deps

def install_missing_dependencies(missing_deps):
    """安装缺失的依赖"""
    logger = logging.getLogger("DependencyInstaller")
    
    if not missing_deps:
        logger.info("所有依赖已安装")
        return True
    
    # 尝试安装缺失的依赖
    success = True
    for dep in missing_deps:
        try:
            logger.info(f"安装 {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            logger.info(f"{dep} 安装成功")
        except subprocess.CalledProcessError as e:
            logger.error(f"安装 {dep} 时出错: {str(e)}")
            success = False
    
    return success

def create_requirements_file():
    """创建requirements.txt文件"""
    logger = logging.getLogger("DependencyInstaller")
    
    requirements = """
# 基本依赖
PyQt5>=5.15.0
numpy<2.0.0
opencv-python>=4.5.0
moviepy>=1.0.3
psutil>=5.8.0
pillow>=8.0.0
requests>=2.25.0
"""
    
    try:
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write(requirements.strip())
        logger.info("requirements.txt文件创建成功")
        return True
    except Exception as e:
        logger.error(f"创建requirements.txt文件时出错: {str(e)}")
        return False

def main():
    """主函数"""
    logger = setup_logging()
    logger.info("开始安装依赖")
    
    # 检查Python版本
    if not check_python_version():
        print("错误: Python版本过低，需要Python 3.6或更高版本")
        return 1
    
    # 确保pip已安装
    if not install_pip():
        print("错误: 无法安装pip，请手动安装")
        return 1
    
    # 升级pip
    upgrade_pip()
    
    # 创建requirements.txt文件
    create_requirements_file()
    
    # 检查依赖
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"发现缺失的依赖: {', '.join(missing_deps)}")
        print("正在安装缺失的依赖...")
        
        # 安装缺失的依赖
        if install_missing_dependencies(missing_deps):
            print("所有依赖安装成功")
        else:
            print("警告: 部分依赖安装失败，请查看日志获取详细信息")
            
        # 再次检查依赖
        missing_deps = check_dependencies()
        if missing_deps:
            print(f"仍有缺失的依赖: {', '.join(missing_deps)}")
            print("请尝试手动安装: pip install -r requirements.txt")
            return 1
    else:
        print("所有依赖已安装")
    
    print("\n依赖安装完成！")
    print("现在您可以运行应用程序了。")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger = logging.getLogger("DependencyInstaller")
        logger.error(f"安装依赖时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        print(f"错误: {str(e)}")
        sys.exit(1) 