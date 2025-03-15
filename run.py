#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视频编辑器启动脚本
"""

import sys
import os

# 添加应用程序目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'video_editor_app'))

# 导入主应用程序
from video_editor_app.main import main

if __name__ == '__main__':
    main() 