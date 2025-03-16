#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
禁用代理脚本
此脚本用于禁用Python pip的代理设置，解决代理连接问题
"""

import os
import sys
import subprocess
import logging
import traceback

def setup_logging():
    """设置日志记录"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception:
            log_dir = os.path.dirname(os.path.abspath(__file__))

    log_file = os.path.join(log_dir, "disable_proxy.log")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("ProxyDisabler")

def disable_pip_proxy():
    """禁用pip代理设置"""
    logger = setup_logging()
    
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

def check_pip_config():
    """检查pip配置"""
    logger = setup_logging()
    
    try:
        # 显示当前pip配置
        logger.info("检查当前pip配置...")
        result = subprocess.run([sys.executable, "-m", "pip", "config", "list"], check=True, capture_output=True, text=True)
        config = result.stdout.strip()
        
        logger.info(f"当前pip配置:\n{config}")
        
        # 检查是否存在代理设置
        if "proxy" in config.lower():
            logger.warning("检测到代理设置，将尝试禁用...")
            return True
        else:
            logger.info("未检测到代理设置")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"检查pip配置时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def create_pip_conf():
    """创建pip配置文件"""
    logger = setup_logging()
    
    # 确定pip配置文件路径
    if sys.platform == "win32":
        pip_conf_dir = os.path.join(os.path.expanduser("~"), "pip")
        pip_conf_file = os.path.join(pip_conf_dir, "pip.ini")
    else:
        pip_conf_dir = os.path.join(os.path.expanduser("~"), ".pip")
        pip_conf_file = os.path.join(pip_conf_dir, "pip.conf")
    
    # 创建配置目录
    if not os.path.exists(pip_conf_dir):
        try:
            os.makedirs(pip_conf_dir)
            logger.info(f"创建pip配置目录: {pip_conf_dir}")
        except Exception as e:
            logger.error(f"创建pip配置目录时出错: {str(e)}")
            return False
    
    # 创建配置文件
    try:
        with open(pip_conf_file, "w") as f:
            f.write("[global]\n")
            f.write("timeout = 60\n")
            f.write("index-url = https://pypi.org/simple\n")
            f.write("trusted-host = pypi.org\n")
            f.write("               files.pythonhosted.org\n")
            f.write("proxy = \n")  # 空代理设置
        
        logger.info(f"创建pip配置文件: {pip_conf_file}")
        return True
    except Exception as e:
        logger.error(f"创建pip配置文件时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def main():
    """主函数"""
    logger = setup_logging()
    logger.info("开始禁用代理设置")
    
    # 检查pip配置
    has_proxy = check_pip_config()
    
    if has_proxy:
        # 禁用代理
        if disable_pip_proxy():
            print("代理设置已成功禁用")
        else:
            print("禁用代理设置失败，尝试创建新的配置文件...")
            
            # 创建新的配置文件
            if create_pip_conf():
                print("已创建新的pip配置文件，代理已禁用")
            else:
                print("创建pip配置文件失败")
                return 1
    else:
        print("未检测到代理设置，无需禁用")
    
    print("\n代理设置已处理完成！")
    print("现在您可以尝试重新安装依赖了。")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger = logging.getLogger("ProxyDisabler")
        logger.error(f"禁用代理时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        print(f"错误: {str(e)}")
        sys.exit(1) 