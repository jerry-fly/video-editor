#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
依赖项安装脚本
此脚本用于安装视频编辑器所需的所有依赖项
支持在线安装和离线安装
"""

import os
import sys
import subprocess
import logging
import traceback
import argparse
import urllib.request
import zipfile
import shutil
import time
import platform

# 依赖项列表
DEPENDENCIES = [
    "numpy>=1.20.0",
    "PyQt5>=5.15.0",
    "opencv-python>=4.5.0",
    "moviepy==1.0.3",  # 指定使用1.0.3版本，这个版本有editor模块
    "psutil>=5.8.0",
    "pillow>=8.0.0",
    "requests>=2.25.0",
    "decorator>=4.4.2",  # moviepy的依赖
    "imageio>=2.9.0",    # moviepy的依赖
    "imageio-ffmpeg>=0.4.5",  # moviepy的依赖
    "tqdm>=4.56.0",      # moviepy的依赖
    "proglog>=0.1.9"     # moviepy的依赖
]

def setup_logging(args):
    """设置日志记录"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception:
            log_dir = os.path.dirname(os.path.abspath(__file__))

    timestamp = time.strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f"install_dependencies_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger("DependencyInstaller")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"平台: {platform.platform()}")
    logger.info(f"安装模式: {'离线' if args.offline else '在线'}")
    logger.info(f"禁用代理: {args.no_proxy}")
    
    return logger

def disable_pip_proxy():
    """禁用pip代理设置"""
    logger = logging.getLogger("DependencyInstaller")
    
    try:
        # 检查是否存在代理设置
        result = subprocess.run(
            [sys.executable, "-m", "pip", "config", "list"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        if "proxy" in result.stdout.lower():
            logger.info("检测到代理设置，尝试禁用...")
            
            # 尝试禁用全局代理
            subprocess.run(
                [sys.executable, "-m", "pip", "config", "unset", "global.proxy"], 
                check=False
            )
            
            # 尝试禁用用户代理
            subprocess.run(
                [sys.executable, "-m", "pip", "config", "unset", "user.proxy"], 
                check=False
            )
            
            logger.info("代理设置已禁用")
        else:
            logger.info("未检测到代理设置")
        
        return True
    except Exception as e:
        logger.error(f"禁用代理设置时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def check_dependencies():
    """检查依赖项是否已安装"""
    logger = logging.getLogger("DependencyInstaller")
    missing_deps = []
    
    for dep in DEPENDENCIES:
        package_name = dep.split(">=")[0].split("==")[0]
        try:
            __import__(package_name.replace("-", "_"))
            logger.info(f"已安装: {package_name}")
        except ImportError:
            logger.warning(f"未安装: {package_name}")
            missing_deps.append(dep)
    
    return missing_deps

def install_dependencies(missing_deps, args):
    """安装缺失的依赖项"""
    logger = logging.getLogger("DependencyInstaller")
    
    if not missing_deps:
        logger.info("所有依赖项已安装")
        return True
    
    logger.info(f"开始安装缺失的依赖项: {missing_deps}")
    
    try:
        cmd = [sys.executable, "-m", "pip", "install", "--no-cache-dir"]
        if args.no_proxy:
            cmd.append("--no-proxy")
        cmd.extend(missing_deps)
        
        logger.debug(f"运行命令: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        logger.info("依赖项安装成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"安装依赖项时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def download_whl_files(missing_deps, download_dir):
    """下载wheel文件"""
    logger = logging.getLogger("DependencyInstaller")
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    logger.info(f"开始下载wheel文件到: {download_dir}")
    
    try:
        cmd = [sys.executable, "-m", "pip", "download", "--no-cache-dir", "--dest", download_dir]
        cmd.extend(missing_deps)
        
        logger.debug(f"运行命令: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        logger.info("wheel文件下载成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"下载wheel文件时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def install_from_whl(whl_dir):
    """从wheel文件安装"""
    logger = logging.getLogger("DependencyInstaller")
    
    if not os.path.exists(whl_dir):
        logger.error(f"wheel目录不存在: {whl_dir}")
        return False
    
    logger.info(f"开始从wheel文件安装: {whl_dir}")
    
    try:
        cmd = [sys.executable, "-m", "pip", "install", "--no-cache-dir", "--no-index", "--find-links", whl_dir]
        cmd.extend([dep.split(">=")[0].split("==")[0] for dep in DEPENDENCIES])
        
        logger.debug(f"运行命令: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        logger.info("从wheel文件安装成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"从wheel文件安装时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def download_offline_package(output_zip):
    """下载离线安装包"""
    logger = logging.getLogger("DependencyInstaller")
    
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_whl")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    os.makedirs(temp_dir)
    
    logger.info(f"开始创建离线安装包: {output_zip}")
    
    try:
        # 下载所有依赖项的wheel文件
        if not download_whl_files(DEPENDENCIES, temp_dir):
            logger.error("下载wheel文件失败")
            return False
        
        # 创建zip文件
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(temp_dir))
                    logger.debug(f"添加文件到zip: {arcname}")
                    zipf.write(file_path, arcname)
        
        logger.info(f"离线安装包创建成功: {output_zip}")
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        
        return True
    except Exception as e:
        logger.error(f"创建离线安装包时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        return False

def try_offline_installation(args):
    """尝试离线安装"""
    logger = logging.getLogger("DependencyInstaller")
    
    # 检查是否存在离线安装包
    offline_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offline_packages")
    whl_dir = os.path.join(offline_dir, "whl")
    
    if os.path.exists(whl_dir):
        logger.info(f"找到离线安装包: {whl_dir}")
        return install_from_whl(whl_dir)
    
    # 检查是否存在zip文件
    zip_file = os.path.join(offline_dir, "dependencies.zip")
    if os.path.exists(zip_file):
        logger.info(f"找到离线安装包zip文件: {zip_file}")
        
        # 解压zip文件
        try:
            if not os.path.exists(whl_dir):
                os.makedirs(whl_dir)
            
            with zipfile.ZipFile(zip_file, 'r') as zipf:
                zipf.extractall(whl_dir)
            
            logger.info(f"离线安装包解压成功: {whl_dir}")
            return install_from_whl(whl_dir)
        except Exception as e:
            logger.error(f"解压离线安装包时出错: {str(e)}")
            logger.debug(traceback.format_exc())
    
    logger.warning("未找到离线安装包，无法进行离线安装")
    return False

def check_moviepy_editor():
    """检查moviepy.editor模块是否可用"""
    logger = logging.getLogger("DependencyInstaller")
    
    try:
        import moviepy.editor
        logger.info("moviepy.editor模块可用")
        return True
    except ImportError as e:
        logger.warning(f"无法导入moviepy.editor模块: {str(e)}")
        
        # 检查moviepy是否已安装
        try:
            import moviepy
            logger.info(f"已安装moviepy版本: {moviepy.__version__}")
            
            # 如果已安装但版本不是1.0.3，尝试重新安装
            if moviepy.__version__ != "1.0.3":
                logger.info(f"当前moviepy版本 {moviepy.__version__} 不是1.0.3，尝试重新安装")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "uninstall", "moviepy", "-y"], check=True)
                    subprocess.run([sys.executable, "-m", "pip", "install", "moviepy==1.0.3", "--no-cache-dir"], check=True)
                    logger.info("moviepy 1.0.3版本安装成功")
                    
                    # 重新检查
                    import moviepy.editor
                    logger.info("moviepy.editor模块现在可用")
                    return True
                except Exception as e:
                    logger.error(f"重新安装moviepy时出错: {str(e)}")
                    logger.debug(traceback.format_exc())
        except ImportError:
            logger.error("moviepy未安装")
        
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="安装视频编辑器所需的依赖项")
    parser.add_argument("--offline", action="store_true", help="使用离线安装模式")
    parser.add_argument("--no-proxy", action="store_true", help="禁用代理设置")
    parser.add_argument("--create-offline", action="store_true", help="创建离线安装包")
    args = parser.parse_args()
    
    logger = setup_logging(args)
    logger.info("开始安装依赖项")
    
    # 如果需要禁用代理
    if args.no_proxy:
        disable_pip_proxy()
    
    # 如果需要创建离线安装包
    if args.create_offline:
        offline_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offline_packages")
        if not os.path.exists(offline_dir):
            os.makedirs(offline_dir)
        
        output_zip = os.path.join(offline_dir, "dependencies.zip")
        if download_offline_package(output_zip):
            print(f"离线安装包创建成功: {output_zip}")
            return 0
        else:
            print("创建离线安装包失败")
            return 1
    
    # 检查依赖项
    missing_deps = check_dependencies()
    
    # 安装依赖项
    if missing_deps:
        if args.offline:
            if not try_offline_installation(args):
                logger.error("离线安装失败")
                return 1
        else:
            if not install_dependencies(missing_deps, args):
                logger.error("在线安装失败")
                return 1
    
    # 检查moviepy.editor模块
    if not check_moviepy_editor():
        logger.warning("moviepy.editor模块不可用，请运行fix_moviepy.py脚本修复")
    
    logger.info("依赖项安装完成")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger = logging.getLogger("DependencyInstaller")
        logger.error(f"安装依赖项时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        print(f"错误: {str(e)}")
        sys.exit(1) 