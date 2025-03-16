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
    # 尝试导入NumPy补丁
    numpy_patch_path = os.path.join(current_dir, "numpy_patch.py")
    if os.path.exists(numpy_patch_path):
        print("应用NumPy补丁...")
        with open(numpy_patch_path, "r", encoding="utf-8") as f:
            patch_code = f.read()
            exec(patch_code)
    
    # 运行完整依赖检查
    from check_numpy import check_dependencies
    check_dependencies()
except ImportError:
    print("警告: 无法导入check_numpy模块，跳过依赖检查")
except Exception as e:
    print(f"警告: 依赖检查时出错: {str(e)}")

# 确保NumPy版本正确
try:
    import numpy
    numpy_version = numpy.__version__
    print(f"运行时NumPy版本: {numpy_version}")
    if numpy_version.startswith("2."):
        print("警告: 检测到NumPy 2.x版本，可能导致OpenCV导入错误")
except Exception as e:
    print(f"检查NumPy版本时出错: {str(e)}")

# 导入主模块
try:
    from video_editor_app.main import main
    main()
except ImportError as e:
    if "cv2" in str(e) or "_ARRAY_API not found" in str(e):
        print("=" * 50)
        print("错误: OpenCV导入失败，可能是NumPy版本不兼容")
        print("请尝试以下步骤:")
        print("1. 卸载NumPy: pip uninstall numpy")
        print("2. 安装兼容版本: pip install numpy==1.24.3")
        print("3. 重新运行应用程序")
        print("=" * 50)
    else:
        print(f"导入错误: {str(e)}")
except Exception as e:
    print(f"运行错误: {str(e)}")

if __name__ == "__main__":
    pass  # 主要逻辑已在try块中执行 