#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图标生成脚本 - 为视频编辑器应用程序创建图标
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_icon():
    """创建应用程序图标"""
    print("正在创建视频编辑器应用程序图标...")
    
    # 创建图标尺寸
    sizes = {
        'ico': [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
        'icns': [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)],
        'png': [(512, 512)]
    }
    
    # 创建基础图标 (1024x1024)
    icon = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # 绘制背景圆形
    circle_center = (512, 512)
    circle_radius = 480
    
    # 创建渐变背景
    for r in range(circle_radius, 0, -1):
        # 从深蓝色到浅蓝色的渐变
        ratio = r / circle_radius
        color = (
            int(41 + (92 - 41) * (1 - ratio)),  # R: 41 -> 92
            int(128 + (173 - 128) * (1 - ratio)),  # G: 128 -> 173
            int(185 + (255 - 185) * (1 - ratio))   # B: 185 -> 255
        )
        draw.ellipse(
            (circle_center[0] - r, circle_center[1] - r, 
             circle_center[0] + r, circle_center[1] + r), 
            fill=color
        )
    
    # 绘制播放按钮三角形
    triangle_size = 320
    triangle_points = [
        (512 - triangle_size//4, 512 - triangle_size//2),  # 左上
        (512 - triangle_size//4, 512 + triangle_size//2),  # 左下
        (512 + triangle_size//2, 512),                     # 右中
    ]
    draw.polygon(triangle_points, fill=(255, 255, 255, 230))
    
    # 绘制编辑条纹
    stripe_width = 40
    stripe_spacing = 60
    stripe_length = 280
    stripe_color = (255, 255, 255, 180)
    
    # 右上角的编辑条纹
    for i in range(3):
        start_x = 512 + 100
        start_y = 512 - 180 + (i * stripe_spacing)
        draw.rectangle(
            (start_x, start_y, start_x + stripe_length, start_y + stripe_width),
            fill=stripe_color
        )
    
    # 应用模糊效果使图标更平滑
    icon = icon.filter(ImageFilter.GaussianBlur(radius=2))
    
    # 保存不同格式的图标
    os.makedirs('resources', exist_ok=True)
    
    # 保存PNG格式
    icon.save('resources/icon.png', 'PNG')
    print(f"已创建PNG图标: resources/icon.png")
    
    # 保存ICO格式 (Windows)
    try:
        icon.save('resources/icon.ico', 'ICO', sizes=sizes['ico'])
        print(f"已创建ICO图标: resources/icon.ico")
    except Exception as e:
        print(f"创建ICO图标时出错: {e}")
    
    # 保存ICNS格式 (macOS)
    try:
        # 对于ICNS，我们需要使用iconutil，这需要先创建一个.iconset目录
        iconset_dir = 'resources/icon.iconset'
        os.makedirs(iconset_dir, exist_ok=True)
        
        # 创建不同尺寸的图标
        for size in [16, 32, 64, 128, 256, 512, 1024]:
            resized = icon.resize((size, size), Image.LANCZOS)
            resized.save(f'{iconset_dir}/icon_{size}x{size}.png', 'PNG')
            # 为Retina显示创建2x版本
            if size <= 512:
                resized = icon.resize((size*2, size*2), Image.LANCZOS)
                resized.save(f'{iconset_dir}/icon_{size}x{size}@2x.png', 'PNG')
        
        print(f"已创建iconset目录: {iconset_dir}")
        print("要生成.icns文件，请在终端中运行以下命令:")
        print(f"iconutil -c icns {iconset_dir}")
    except Exception as e:
        print(f"创建ICNS图标时出错: {e}")
    
    print("图标创建完成！")

if __name__ == "__main__":
    create_icon() 