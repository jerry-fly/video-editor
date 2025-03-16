#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复 moviepy.editor 模块导入问题
此脚本用于检查和修复 moviepy 安装，确保 moviepy.editor 模块可用
"""

import os
import sys
import subprocess
import logging
import traceback
import importlib
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

    log_file = os.path.join(log_dir, f"fix_moviepy_{time.strftime('%Y%m%d_%H%M%S')}.log")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("MoviepyFixer")

def check_moviepy_installation():
    """检查 moviepy 安装状态"""
    logger = logging.getLogger("MoviepyFixer")
    
    try:
        import moviepy
        logger.info(f"已安装 moviepy 版本: {moviepy.__version__}")
        
        # 尝试导入 moviepy.editor
        try:
            import moviepy.editor
            logger.info("moviepy.editor 模块可用")
            return True, None
        except ImportError as e:
            logger.warning(f"无法导入 moviepy.editor 模块: {str(e)}")
            return False, str(e)
    except ImportError as e:
        logger.error(f"未安装 moviepy: {str(e)}")
        return False, str(e)

def get_moviepy_path():
    """获取 moviepy 安装路径"""
    logger = logging.getLogger("MoviepyFixer")
    
    try:
        import moviepy
        moviepy_path = os.path.dirname(moviepy.__file__)
        logger.info(f"moviepy 安装路径: {moviepy_path}")
        return moviepy_path
    except ImportError:
        logger.error("未安装 moviepy")
        return None

def check_editor_file(moviepy_path):
    """检查 editor.py 文件是否存在"""
    logger = logging.getLogger("MoviepyFixer")
    
    if not moviepy_path:
        return False
    
    editor_path = os.path.join(moviepy_path, "editor.py")
    if os.path.exists(editor_path):
        logger.info(f"找到 editor.py 文件: {editor_path}")
        return True
    else:
        logger.warning(f"未找到 editor.py 文件: {editor_path}")
        return False

def create_editor_module(moviepy_path):
    """创建 editor.py 模块"""
    logger = logging.getLogger("MoviepyFixer")
    
    if not moviepy_path:
        return False
    
    editor_path = os.path.join(moviepy_path, "editor.py")
    editor_content = """
# -*- coding: utf-8 -*-
\"\"\"
This module serves as a compatibility layer for moviepy 2.0.0+
It imports and re-exports the main components from moviepy
\"\"\"

# Import video components
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.video.VideoClip import VideoClip, ImageClip, ColorClip
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    from moviepy.video.compositing.concatenate import concatenate_videoclips
except ImportError as e:
    print(f"Error importing video components: {e}")

# Import audio components
try:
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy.audio.AudioClip import AudioClip, CompositeAudioClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip
except ImportError as e:
    print(f"Error importing audio components: {e}")

# Import other utilities
try:
    from moviepy.Clip import Clip
    from moviepy.config import change_settings
except ImportError as e:
    print(f"Error importing utilities: {e}")
"""
    
    try:
        with open(editor_path, "w", encoding="utf-8") as f:
            f.write(editor_content)
        logger.info(f"创建了 editor.py 文件: {editor_path}")
        return True
    except Exception as e:
        logger.error(f"创建 editor.py 文件时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def reinstall_moviepy():
    """重新安装 moviepy"""
    logger = logging.getLogger("MoviepyFixer")
    
    try:
        logger.info("卸载 moviepy...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "moviepy", "-y"], check=True)
        
        logger.info("安装 moviepy 1.0.3 版本...")
        subprocess.run([sys.executable, "-m", "pip", "install", "moviepy==1.0.3", "--no-cache-dir"], check=True)
        
        logger.info("moviepy 重新安装成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"重新安装 moviepy 时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def fix_moviepy_imports():
    """修复 moviepy 导入问题"""
    logger = logging.getLogger("MoviepyFixer")
    
    # 检查 moviepy 安装
    installed, error = check_moviepy_installation()
    if installed:
        logger.info("moviepy.editor 模块已可用，无需修复")
        return True
    
    # 获取 moviepy 路径
    moviepy_path = get_moviepy_path()
    if not moviepy_path:
        logger.error("未找到 moviepy 安装路径，尝试重新安装")
        if reinstall_moviepy():
            # 重新检查安装
            installed, _ = check_moviepy_installation()
            return installed
        return False
    
    # 检查 editor.py 文件
    if check_editor_file(moviepy_path):
        # 尝试重新加载模块
        try:
            if "moviepy.editor" in sys.modules:
                del sys.modules["moviepy.editor"]
            import moviepy.editor
            logger.info("重新加载 moviepy.editor 模块成功")
            return True
        except ImportError as e:
            logger.warning(f"重新加载 moviepy.editor 模块失败: {str(e)}")
    
    # 创建 editor.py 模块
    if create_editor_module(moviepy_path):
        # 尝试导入新创建的模块
        try:
            if "moviepy.editor" in sys.modules:
                del sys.modules["moviepy.editor"]
            import moviepy.editor
            logger.info("导入新创建的 moviepy.editor 模块成功")
            return True
        except ImportError as e:
            logger.warning(f"导入新创建的 moviepy.editor 模块失败: {str(e)}")
    
    # 如果上述方法都失败，尝试重新安装 moviepy
    logger.info("尝试重新安装 moviepy...")
    if reinstall_moviepy():
        # 重新检查安装
        installed, _ = check_moviepy_installation()
        return installed
    
    return False

def main():
    """主函数"""
    logger = setup_logging()
    logger.info("开始修复 moviepy.editor 模块导入问题")
    
    if fix_moviepy_imports():
        print("moviepy.editor 模块修复成功！")
        return 0
    else:
        print("修复 moviepy.editor 模块失败，请查看日志获取详细信息")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger = logging.getLogger("MoviepyFixer")
        logger.error(f"修复 moviepy.editor 模块时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        print(f"错误: {str(e)}")
        sys.exit(1) 