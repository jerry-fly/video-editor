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
import signal
import psutil
import threading

# 全局变量，用于跟踪应用程序状态
APP_STARTED = False
LOCK_FILE_PATH = os.path.join(tempfile.gettempdir(), "video_editor_lock.pid")
LOCK_SOCKET = None

# 单实例检查 - 使用文件锁和网络端口双重保障
def is_already_running():
    """检查应用程序是否已经在运行，使用文件锁和网络端口双重检查"""
    global LOCK_SOCKET
    
    # 方法1: 检查PID文件
    if os.path.exists(LOCK_FILE_PATH):
        try:
            with open(LOCK_FILE_PATH, 'r') as f:
                old_pid = int(f.read().strip())
            # 检查PID是否存在
            if psutil.pid_exists(old_pid):
                process = psutil.Process(old_pid)
                # 检查进程名称是否包含python或VideoEditor
                if "python" in process.name().lower() or "videoeditor" in process.name().lower():
                    return True
        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied, IOError):
            # 如果PID文件存在但无效，删除它
            try:
                os.remove(LOCK_FILE_PATH)
            except:
                pass
    
    # 方法2: 尝试绑定一个特定端口
    try:
        LOCK_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        LOCK_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        LOCK_SOCKET.bind(('localhost', 45678))
        LOCK_SOCKET.listen(1)
        
        # 创建PID文件
        with open(LOCK_FILE_PATH, 'w') as f:
            f.write(str(os.getpid()))
            
        # 注册退出时清理
        atexit.register(cleanup_lock)
        
        return False
    except socket.error:
        # 如果端口已被占用，说明已有实例在运行
        return True

def cleanup_lock():
    """清理锁文件和套接字"""
    global LOCK_SOCKET
    
    # 关闭套接字
    if LOCK_SOCKET:
        try:
            LOCK_SOCKET.close()
        except:
            pass
    
    # 删除PID文件
    if os.path.exists(LOCK_FILE_PATH):
        try:
            # 只删除自己创建的PID文件
            with open(LOCK_FILE_PATH, 'r') as f:
                pid = int(f.read().strip())
                if pid == os.getpid():
                    os.remove(LOCK_FILE_PATH)
        except:
            pass

# 强制终止所有VideoEditor相关进程
def kill_all_video_editor_processes(except_pid=None):
    """终止所有VideoEditor相关进程，除了指定的PID"""
    current_pid = os.getpid()
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # 跳过当前进程和指定的例外进程
            if proc.info['pid'] == current_pid or proc.info['pid'] == except_pid:
                continue
                
            # 检查进程名称是否包含VideoEditor
            proc_name = proc.info['name'].lower()
            if "videoeditor" in proc_name or (
                "python" in proc_name and any(
                    "videoeditor" in cmd.lower() or "run.py" in cmd.lower() 
                    for cmd in proc.cmdline() if isinstance(cmd, str)
                )
            ):
                print(f"Terminating process: {proc.info['pid']} ({proc.info['name']})")
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

# 设置超时保护，防止无限循环
def timeout_handler():
    """超时处理函数"""
    global APP_STARTED
    
    if not APP_STARTED:
        logger.critical("应用程序启动超时，可能陷入无限循环，强制退出")
        print("应用程序启动超时，可能陷入无限循环，强制退出")
        
        # 终止所有其他VideoEditor进程
        kill_all_video_editor_processes()
        
        # 强制退出当前进程
        os._exit(1)

# 设置紧急退出处理
def emergency_exit_handler(signum, frame):
    """紧急退出处理函数"""
    logger.critical(f"收到信号 {signum}，紧急退出")
    print(f"收到信号 {signum}，紧急退出")
    
    # 终止所有VideoEditor进程
    kill_all_video_editor_processes()
    
    # 清理锁
    cleanup_lock()
    
    # 强制退出
    os._exit(1)

# 注册信号处理器
signal.signal(signal.SIGTERM, emergency_exit_handler)
signal.signal(signal.SIGINT, emergency_exit_handler)
if hasattr(signal, 'SIGBREAK'):  # Windows特有
    signal.signal(signal.SIGBREAK, emergency_exit_handler)

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
logger.info(f"进程ID: {os.getpid()}")

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

# 设置启动超时（30秒）
timeout_timer = threading.Timer(30, timeout_handler)
timeout_timer.daemon = True
timeout_timer.start()

# 导入主模块
try:
    logger.info("导入主模块...")
    from video_editor_app.main import main
    
    # 取消超时计时器
    timeout_timer.cancel()
    
    # 标记应用程序已启动
    APP_STARTED = True
    
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
    # 清理锁
    cleanup_lock()

# 注册清理函数
atexit.register(cleanup)

if __name__ == "__main__":
    pass  # 主要逻辑已在try块中执行 