#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视频编辑器启动脚本（修复版）
"""

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
