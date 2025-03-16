#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复模块导入路径问题
此脚本用于解决视频编辑器应用程序的模块导入路径问题
"""

import os
import sys
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

    log_file = os.path.join(log_dir, "fix_module_path.log")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("ModulePathFixer")

def fix_module_path():
    """修复模块导入路径"""
    logger = setup_logging()
    
    # 获取当前脚本的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"当前目录: {current_dir}")
    
    # 检查当前目录是否已在Python路径中
    if current_dir not in sys.path:
        logger.info(f"将当前目录添加到Python路径: {current_dir}")
        sys.path.insert(0, current_dir)
    else:
        logger.info("当前目录已在Python路径中")
    
    # 检查video_editor_app目录
    video_editor_dir = os.path.join(current_dir, "video_editor_app")
    if os.path.exists(video_editor_dir) and os.path.isdir(video_editor_dir):
        logger.info(f"找到video_editor_app目录: {video_editor_dir}")
        
        # 创建或更新__init__.py文件
        init_file = os.path.join(video_editor_dir, "__init__.py")
        if not os.path.exists(init_file):
            logger.info(f"创建__init__.py文件: {init_file}")
            with open(init_file, "w", encoding="utf-8") as f:
                f.write('#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\n"""\n视频编辑器应用程序包\n"""\n\n__version__ = "1.0.0"\n')
        else:
            logger.info(f"__init__.py文件已存在: {init_file}")
    else:
        logger.error(f"video_editor_app目录不存在: {video_editor_dir}")
        return False
    
    # 检查是否可以导入video_editor_app包
    try:
        logger.info("尝试导入video_editor_app包")
        import video_editor_app
        logger.info(f"成功导入video_editor_app包，版本: {video_editor_app.__version__}")
        return True
    except Exception as e:
        logger.error(f"导入video_editor_app包时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def create_run_script():
    """创建正确的运行脚本"""
    logger = setup_logging()
    
    # 获取当前脚本的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建run_fixed.py文件
    run_file = os.path.join(current_dir, "run_fixed.py")
    logger.info(f"创建修复后的运行脚本: {run_file}")
    
    script_content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"
视频编辑器启动脚本（修复版）
\"\"\"

import sys
import os
import traceback
import logging

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 设置日志记录
log_dir = os.path.join(current_dir, "logs")
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
    except Exception:
        log_dir = current_dir

log_file = os.path.join(log_dir, "video_editor.log")
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

try:
    # 导入主程序
    from video_editor_app.main import main
    
    # 运行主程序
    sys.exit(main())
except Exception as e:
    logger.error(f"运行主程序时出错: {str(e)}")
    logger.debug(traceback.format_exc())
    print(f"错误: {str(e)}")
    sys.exit(1)
"""
    
    with open(run_file, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # 设置执行权限
    try:
        os.chmod(run_file, 0o755)
        logger.info(f"已设置执行权限: {run_file}")
    except Exception as e:
        logger.warning(f"设置执行权限时出错: {str(e)}")
    
    return run_file

def create_batch_file():
    """创建Windows批处理文件"""
    logger = setup_logging()
    
    # 获取当前脚本的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建run_fixed.bat文件
    bat_file = os.path.join(current_dir, "run_fixed.bat")
    logger.info(f"创建Windows批处理文件: {bat_file}")
    
    batch_content = """@echo off
chcp 65001 > nul
echo 启动视频编辑器应用程序（修复版）...
echo.

echo 检查Python环境...
python --version
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo.
echo 启动应用程序...
python run_fixed.py
if %ERRORLEVEL% neq 0 (
    echo 错误: 应用程序运行失败
    pause
    exit /b 1
)

exit /b 0
"""
    
    with open(bat_file, "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    return bat_file

def main():
    """主函数"""
    logger = setup_logging()
    logger.info("开始修复模块导入路径问题")
    
    # 修复模块导入路径
    if fix_module_path():
        logger.info("模块导入路径修复成功")
    else:
        logger.error("模块导入路径修复失败")
    
    # 创建运行脚本
    run_file = create_run_script()
    logger.info(f"已创建运行脚本: {run_file}")
    
    # 创建批处理文件
    bat_file = create_batch_file()
    logger.info(f"已创建批处理文件: {bat_file}")
    
    print("\n修复完成！")
    print(f"请使用以下命令运行应用程序：")
    print(f"  Python: python {os.path.basename(run_file)}")
    print(f"  Windows: {os.path.basename(bat_file)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 