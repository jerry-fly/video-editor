#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                            QVBoxLayout, QWidget, QPushButton, QHBoxLayout,
                            QLabel, QFileDialog, QMessageBox, QStyle)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor, QPalette, QFont

# 导入自定义模块
from clip_tab import VideoClipTab
from merge_tab import VideoMergeTab
from convert_tab import VideoConvertTab

class VideoEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('视频编辑器')
        self.setMinimumSize(1000, 700)
        
        # 设置应用程序样式表，增强科技感
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QTabWidget::pane {
                border: 1px solid #313244;
                background-color: #1e1e2e;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #313244;
                color: #cdd6f4;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                min-width: 100px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #89b4fa;
                color: #1e1e2e;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 13px;
            }
            QProgressBar {
                border: 1px solid #313244;
                border-radius: 5px;
                text-align: center;
                background-color: #313244;
            }
            QProgressBar::chunk {
                background-color: #89b4fa;
                border-radius: 5px;
            }
        """)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标签页控件
        self.tabs = QTabWidget()
        
        # 创建三个功能标签页
        self.clip_tab = VideoClipTab()
        self.merge_tab = VideoMergeTab()
        self.convert_tab = VideoConvertTab()
        
        # 添加标签页到标签页控件
        self.tabs.addTab(self.clip_tab, "视频裁剪")
        self.tabs.addTab(self.merge_tab, "视频拼接")
        self.tabs.addTab(self.convert_tab, "格式转换")
        
        # 将标签页控件添加到主布局
        main_layout.addWidget(self.tabs)
        
        # 设置状态栏
        self.statusBar().showMessage('就绪')
        
        # 显示窗口
        self.show()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion风格，更现代化
    
    # 创建应用程序实例
    window = VideoEditorApp()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
