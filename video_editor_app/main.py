#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                            QVBoxLayout, QWidget, QLabel, QStatusBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# 正确导入模块
from video_editor_app.clip_tab import VideoClipTab
from video_editor_app.merge_tab import VideoMergeTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("视频编辑器")
        self.setMinimumSize(800, 600)
        
        # 设置图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标签页
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(True)
        
        # 添加视频剪辑标签页
        self.clip_tab = VideoClipTab()
        self.tabs.addTab(self.clip_tab, "视频剪辑")
        
        # 添加视频合并标签页
        self.merge_tab = VideoMergeTab()
        self.tabs.addTab(self.merge_tab, "视频合并")
        
        # 添加视频转换标签页（待实现）
        self.convert_tab = QWidget()
        self.tabs.addTab(self.convert_tab, "视频转换")
        
        # 添加标签页到主布局
        main_layout.addWidget(self.tabs)
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QTabWidget::pane {
                border: 1px solid #313244;
                background-color: #1e1e2e;
            }
            QTabBar::tab {
                background-color: #313244;
                color: #cdd6f4;
                border-bottom-color: #313244;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background-color: #45475a;
            }
            QTabBar::tab:selected {
                border-bottom-color: #89b4fa;
                border-bottom-width: 2px;
                border-bottom-style: solid;
            }
            QStatusBar {
                background-color: #313244;
                color: #cdd6f4;
            }
        """)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
