#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
依赖安装脚本
此脚本用于安装视频编辑器应用程序所需的所有依赖
支持在线安装和离线安装
"""

import os
import sys
import subprocess
import logging
import platform
import traceback
import argparse
import urllib.request
import zipfile
import shutil
import time

def setup_logging():
    """设置日志记录"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception:
            log_dir = os.path.dirname(os.path.abspath(__file__))

    log_file = os.path.join(log_dir, f"install_dependencies_{time.strftime('%Y%m%d_%H%M%S')}.log")
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

def disable_pip_proxy():
    """禁用pip代理设置"""
    logger = logging.getLogger("DependencyInstaller")
    
    try:
        # 禁用HTTP代理
        logger.info("禁用HTTP代理...")
        subprocess.run([sys.executable, "-m", "pip", "config", "set", "global.proxy", ""], check=True)
        
        # 禁用HTTPS代理
        logger.info("禁用HTTPS代理...")
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)
        
        logger.info("代理设置已禁用")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"禁用代理设置时出错: {str(e)}")
        logger.debug(traceback.format_exc())
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
            subprocess.run([sys.executable, "-m", "pip", "install", dep, "--no-cache-dir"], check=True)
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
            subprocess.run([sys.executable, "-m", "pip", "install", dep, "--no-cache-dir"], check=True)
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

def download_whl_files():
    """下载所需的whl文件"""
    logger = logging.getLogger("DependencyInstaller")
    
    # 创建下载目录
    download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whl_files")
    if not os.path.exists(download_dir):
        try:
            os.makedirs(download_dir)
            logger.info(f"创建下载目录: {download_dir}")
        except Exception as e:
            logger.error(f"创建下载目录时出错: {str(e)}")
            return False
    
    # 下载whl文件的URL列表
    # 这些URL应该指向与您的Python版本兼容的whl文件
    # 以下是示例URL，您需要根据实际情况修改
    whl_urls = {
        "numpy": "https://files.pythonhosted.org/packages/a7/e3/5c56a0c6be7a9c67e9d8b3af84ad8c09f1ad59baa6c3c1c2f7a7c3d1cf8/numpy-1.24.4-cp39-cp39-win_amd64.whl",
        "PyQt5": "https://files.pythonhosted.org/packages/4b/3b/56b3b0d7f6d596ff5e79a3e3a4a5879a053a6b8c84c0a2a48f8c2c123c0/PyQt5-5.15.9-cp39-abi3-win_amd64.whl",
        "opencv-python": "https://files.pythonhosted.org/packages/8c/c4/a1ab8d9e0e4c0f4a0a6d7f2e9c00f8f2b8fb2a9c0f6b7f1f8e9e1b2b0e1/opencv_python-4.8.0.76-cp39-abi3-win_amd64.whl",
        "moviepy": "https://files.pythonhosted.org/packages/a1/d3/d8d7afc3a3e82a4d5be8177e0e2b6a5a6808c6f050a66b1d5b9a3b98e8e/moviepy-1.0.3-py3-none-any.whl",
        "psutil": "https://files.pythonhosted.org/packages/e1/b0/7276de53321c12981717490516b7e612364f2cb372ee8901bd4a66a000d7/psutil-5.9.5-cp39-cp39-win_amd64.whl",
        "pillow": "https://files.pythonhosted.org/packages/e5/05/f9f29307d6e9994a07d0db8c5c94a3527482d2f1cfb9b7c2e611e6d0bdcf/Pillow-10.0.1-cp39-cp39-win_amd64.whl",
        "requests": "https://files.pythonhosted.org/packages/70/8e/0e2d847013cb52cd35b38c009bb167a1a26b2ce6cd6de7ff3d7a7a9dcec8/requests-2.31.0-py3-none-any.whl"
    }
    
    # 下载whl文件
    success = True
    for package, url in whl_urls.items():
        try:
            whl_file = os.path.join(download_dir, os.path.basename(url))
            if not os.path.exists(whl_file):
                logger.info(f"下载 {package} whl文件: {url}")
                urllib.request.urlretrieve(url, whl_file)
                logger.info(f"{package} whl文件下载成功")
            else:
                logger.info(f"{package} whl文件已存在: {whl_file}")
        except Exception as e:
            logger.error(f"下载 {package} whl文件时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            success = False
    
    return success, download_dir

def install_from_whl(whl_dir):
    """从whl文件安装依赖"""
    logger = logging.getLogger("DependencyInstaller")
    
    # 检查whl目录是否存在
    if not os.path.exists(whl_dir):
        logger.error(f"whl目录不存在: {whl_dir}")
        return False
    
    # 获取whl文件列表
    whl_files = [f for f in os.listdir(whl_dir) if f.endswith('.whl')]
    if not whl_files:
        logger.error(f"whl目录中没有whl文件: {whl_dir}")
        return False
    
    # 安装whl文件
    success = True
    for whl_file in whl_files:
        try:
            whl_path = os.path.join(whl_dir, whl_file)
            logger.info(f"安装whl文件: {whl_file}")
            subprocess.run([sys.executable, "-m", "pip", "install", whl_path, "--no-deps"], check=True)
            logger.info(f"whl文件安装成功: {whl_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"安装whl文件时出错: {whl_file}, {str(e)}")
            success = False
    
    return success

def download_offline_package():
    """下载离线安装包"""
    logger = logging.getLogger("DependencyInstaller")
    
    # 离线安装包URL
    offline_url = "https://github.com/jerry-fly/video-editor-deps/releases/download/v1.0.0/video-editor-deps-win-py39.zip"
    
    # 创建下载目录
    download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offline_deps")
    if not os.path.exists(download_dir):
        try:
            os.makedirs(download_dir)
            logger.info(f"创建下载目录: {download_dir}")
        except Exception as e:
            logger.error(f"创建下载目录时出错: {str(e)}")
            return False, None
    
    # 下载离线安装包
    try:
        zip_file = os.path.join(download_dir, "video-editor-deps.zip")
        logger.info(f"下载离线安装包: {offline_url}")
        urllib.request.urlretrieve(offline_url, zip_file)
        logger.info("离线安装包下载成功")
        
        # 解压离线安装包
        logger.info(f"解压离线安装包: {zip_file}")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(download_dir)
        logger.info("离线安装包解压成功")
        
        # 删除zip文件
        os.remove(zip_file)
        
        # 返回whl文件目录
        whl_dir = os.path.join(download_dir, "whl_files")
        if os.path.exists(whl_dir):
            return True, whl_dir
        else:
            logger.error(f"解压后未找到whl文件目录: {whl_dir}")
            return False, None
    except Exception as e:
        logger.error(f"下载或解压离线安装包时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        return False, None

def try_offline_installation():
    """尝试离线安装"""
    logger = logging.getLogger("DependencyInstaller")
    
    print("尝试离线安装...")
    
    # 检查是否有本地whl文件目录
    local_whl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whl_files")
    if os.path.exists(local_whl_dir) and os.listdir(local_whl_dir):
        logger.info(f"找到本地whl文件目录: {local_whl_dir}")
        if install_from_whl(local_whl_dir):
            logger.info("从本地whl文件安装成功")
            return True
        else:
            logger.warning("从本地whl文件安装失败")
    
    # 尝试下载并安装离线包
    try:
        success, whl_dir = download_offline_package()
        if success and whl_dir:
            logger.info(f"下载离线安装包成功: {whl_dir}")
            if install_from_whl(whl_dir):
                logger.info("从离线安装包安装成功")
                return True
            else:
                logger.warning("从离线安装包安装失败")
    except Exception as e:
        logger.error(f"离线安装时出错: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # 尝试下载并安装单个whl文件
    try:
        success, whl_dir = download_whl_files()
        if success and whl_dir:
            logger.info(f"下载whl文件成功: {whl_dir}")
            if install_from_whl(whl_dir):
                logger.info("从下载的whl文件安装成功")
                return True
            else:
                logger.warning("从下载的whl文件安装失败")
    except Exception as e:
        logger.error(f"下载whl文件时出错: {str(e)}")
        logger.debug(traceback.format_exc())
    
    return False

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="安装视频编辑器应用程序所需的所有依赖")
    parser.add_argument("--offline", action="store_true", help="使用离线安装模式")
    parser.add_argument("--no-proxy", action="store_true", help="禁用代理设置")
    args = parser.parse_args()
    
    logger = setup_logging()
    logger.info("开始安装依赖")
    logger.info(f"命令行参数: {args}")
    
    # 检查Python版本
    if not check_python_version():
        print("错误: Python版本过低，需要Python 3.6或更高版本")
        return 1
    
    # 确保pip已安装
    if not install_pip():
        print("错误: 无法安装pip，请手动安装")
        return 1
    
    # 禁用代理（如果需要）
    if args.no_proxy:
        logger.info("禁用代理设置...")
        disable_pip_proxy()
    
    # 升级pip
    upgrade_pip()
    
    # 创建requirements.txt文件
    create_requirements_file()
    
    # 检查依赖
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"发现缺失的依赖: {', '.join(missing_deps)}")
        
        if args.offline:
            # 离线安装模式
            if try_offline_installation():
                print("离线安装成功")
            else:
                print("离线安装失败，请尝试在线安装或手动安装")
                return 1
        else:
            # 在线安装模式
            print("正在安装缺失的依赖...")
            try:
                if install_missing_dependencies(missing_deps):
                    print("所有依赖安装成功")
                else:
                    print("警告: 部分依赖安装失败，尝试离线安装...")
                    if try_offline_installation():
                        print("离线安装成功")
                    else:
                        print("离线安装也失败，请查看日志获取详细信息")
                        print("请尝试手动安装: pip install -r requirements.txt")
                        return 1
            except Exception as e:
                logger.error(f"安装依赖时出错: {str(e)}")
                logger.debug(traceback.format_exc())
                print(f"在线安装出错: {str(e)}")
                print("尝试离线安装...")
                if try_offline_installation():
                    print("离线安装成功")
                else:
                    print("离线安装也失败，请查看日志获取详细信息")
                    return 1
        
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