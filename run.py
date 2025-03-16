#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视频编辑器启动脚本
"""

import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 先检查NumPy版本兼容性
try:
    from check_numpy import check_dependencies
    check_dependencies()
except ImportError:
    print("警告: 无法导入check_numpy模块，跳过依赖检查")
except Exception as e:
    print(f"警告: 依赖检查时出错: {str(e)}")

# 导入主模块
from video_editor_app.main import main

if __name__ == "__main__":
    main() 