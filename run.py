#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视频编辑器启动脚本
"""

import sys
import os
import traceback
import time
import logging
import socket
import tempfile
import atexit

# 单实例检查 - 使用文件锁或网络端口
def is_already_running():
    """检查应用程序是否已经在运行"""
    # 方法1: 尝试绑定一个特定端口
    try:
        # 使用一个不太常用的端口
        port = 45678
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', port))
        # 如果成功绑定，说明没有其他实例在运行
        sock.close()
        return False
    except socket.error:
        # 如果端口已被占用，说明已有实例在运行
        return True

# 如果应用程序已经在运行，则退出
if is_already_running():
    print("应用程序已经在运行！")
    sys.exit(0)

# 设置日志记录
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
    except Exception:
        log_dir = os.path.dirname(os.path.abspath(__file__))

log_file = os.path.join(log_dir, f"video_editor_{time.strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("VideoEditor")

logger.info("应用程序启动")
logger.info(f"Python版本: {sys.version}")
logger.info(f"运行路径: {os.path.abspath(__file__)}")

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    logger.info(f"添加路径到sys.path: {current_dir}")

# 显示所有环境变量（可能有助于调试）
logger.debug("环境变量:")
for key, value in os.environ.items():
    logger.debug(f"  {key}={value}")

# 设置最大递归深度，防止无限递归
sys.setrecursionlimit(1000)  # 默认值通常是1000
logger.info(f"设置最大递归深度: {sys.getrecursionlimit()}")

# 先检查NumPy版本兼容性
try:
    # 尝试导入NumPy补丁
    numpy_patch_path = os.path.join(current_dir, "numpy_patch.py")
    if os.path.exists(numpy_patch_path):
        logger.info("应用NumPy补丁...")
        with open(numpy_patch_path, "r", encoding="utf-8") as f:
            patch_code = f.read()
            exec(patch_code)
    
    # 运行完整依赖检查
    logger.info("开始依赖检查...")
    from check_numpy import check_dependencies
    check_dependencies()
except ImportError as e:
    logger.warning(f"无法导入check_numpy模块，跳过依赖检查: {str(e)}")
except Exception as e:
    logger.warning(f"依赖检查时出错: {str(e)}")
    logger.debug(traceback.format_exc())

# 确保NumPy版本正确
try:
    import numpy
    numpy_version = numpy.__version__
    logger.info(f"运行时NumPy版本: {numpy_version}")
    if numpy_version.startswith("2."):
        logger.warning("检测到NumPy 2.x版本，可能导致OpenCV导入错误")
except Exception as e:
    logger.warning(f"检查NumPy版本时出错: {str(e)}")
    logger.debug(traceback.format_exc())

# 检查PyQt5
try:
    import PyQt5
    from PyQt5.QtWidgets import QApplication
    logger.info(f"PyQt5版本: {PyQt5.QtCore.PYQT_VERSION_STR}")
except Exception as e:
    logger.error(f"导入PyQt5时出错: {str(e)}")
    logger.debug(traceback.format_exc())

# 检查OpenCV
try:
    import cv2
    logger.info(f"OpenCV版本: {cv2.__version__}")
except Exception as e:
    logger.error(f"导入OpenCV时出错: {str(e)}")
    logger.debug(traceback.format_exc())

# 检查moviepy
try:
    import moviepy
    logger.info(f"moviepy版本: {moviepy.__version__}")
except Exception as e:
    logger.error(f"导入moviepy时出错: {str(e)}")
    logger.debug(traceback.format_exc())

# 设置超时保护，防止无限循环
def timeout_handler():
    """超时处理函数"""
    logger.critical("应用程序启动超时，可能陷入无限循环，强制退出")
    print("应用程序启动超时，可能陷入无限循环，强制退出")
    os._exit(1)  # 强制退出

# 设置启动超时（30秒）
import threading
timeout_timer = threading.Timer(30, timeout_handler)
timeout_timer.daemon = True
timeout_timer.start()

# 导入主模块
try:
    logger.info("导入主模块...")
    from video_editor_app.main import main
    
    # 取消超时计时器
    timeout_timer.cancel()
    
    logger.info("开始运行主程序...")
    main()
except ImportError as e:
    # 取消超时计时器
    timeout_timer.cancel()
    
    logger.error(f"导入错误: {str(e)}")
    logger.debug(traceback.format_exc())
    
    if "cv2" in str(e) or "_ARRAY_API not found" in str(e):
        logger.error("=" * 50)
        logger.error("错误: OpenCV导入失败，可能是NumPy版本不兼容")
        logger.error("请尝试以下步骤:")
        logger.error("1. 卸载NumPy: pip uninstall numpy")
        logger.error("2. 安装兼容版本: pip install numpy==1.24.3")
        logger.error("3. 重新运行应用程序")
        logger.error("=" * 50)
        
        # 在控制台显示错误信息
        print("=" * 50)
        print("错误: OpenCV导入失败，可能是NumPy版本不兼容")
        print("请尝试以下步骤:")
        print("1. 卸载NumPy: pip uninstall numpy")
        print("2. 安装兼容版本: pip install numpy==1.24.3")
        print("3. 重新运行应用程序")
        print("=" * 50)
        print(f"详细日志请查看: {log_file}")
        input("按Enter键退出...")
except Exception as e:
    # 取消超时计时器
    timeout_timer.cancel()
    
    logger.error(f"运行错误: {str(e)}")
    logger.debug(traceback.format_exc())
    
    # 在控制台显示错误信息
    print("=" * 50)
    print(f"运行错误: {str(e)}")
    print(f"详细日志请查看: {log_file}")
    print("=" * 50)
    input("按Enter键退出...")

# 确保程序正常退出
def cleanup():
    """清理函数，确保程序正常退出"""
    logger.info("应用程序退出")
    # 确保超时计时器被取消
    if timeout_timer.is_alive():
        timeout_timer.cancel()

# 注册清理函数
atexit.register(cleanup)

if __name__ == "__main__":
    pass  # 主要逻辑已在try块中执行 