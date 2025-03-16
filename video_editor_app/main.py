#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging
import traceback
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                            QVBoxLayout, QWidget, QLabel, QStatusBar, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# 获取logger
logger = logging.getLogger("VideoEditor.main")

# 正确导入模块
try:
    from video_editor_app.clip_tab import VideoClipTab
    logger.info("成功导入VideoClipTab")
except Exception as e:
    logger.error(f"导入VideoClipTab时出错: {str(e)}")
    logger.debug(traceback.format_exc())

try:
    from video_editor_app.merge_tab import VideoMergeTab
    logger.info("成功导入VideoMergeTab")
except Exception as e:
    logger.error(f"导入VideoMergeTab时出错: {str(e)}")
    logger.debug(traceback.format_exc())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        logger.info("初始化MainWindow")
        
        self.setWindowTitle("视频编辑器")
        self.setMinimumSize(800, 600)
        
        # 设置图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icon.png")
        if os.path.exists(icon_path):
            logger.info(f"设置图标: {icon_path}")
            self.setWindowIcon(QIcon(icon_path))
        else:
            logger.warning(f"图标文件不存在: {icon_path}")
        
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
        
        try:
            # 添加视频剪辑标签页
            logger.info("创建VideoClipTab")
            self.clip_tab = VideoClipTab()
            self.tabs.addTab(self.clip_tab, "视频剪辑")
        except Exception as e:
            logger.error(f"创建VideoClipTab时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            # 创建一个错误提示标签
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("视频剪辑模块加载失败，请检查日志")
            error_label.setAlignment(Qt.AlignCenter)
            error_layout.addWidget(error_label)
            self.tabs.addTab(error_widget, "视频剪辑(错误)")
        
        try:
            # 添加视频合并标签页
            logger.info("创建VideoMergeTab")
            self.merge_tab = VideoMergeTab()
            self.tabs.addTab(self.merge_tab, "视频合并")
        except Exception as e:
            logger.error(f"创建VideoMergeTab时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            # 创建一个错误提示标签
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("视频合并模块加载失败，请检查日志")
            error_label.setAlignment(Qt.AlignCenter)
            error_layout.addWidget(error_label)
            self.tabs.addTab(error_widget, "视频合并(错误)")
        
        # 添加视频转换标签页（待实现）
        self.convert_tab = QWidget()
        convert_layout = QVBoxLayout(self.convert_tab)
        convert_label = QLabel("视频转换功能正在开发中...")
        convert_label.setAlignment(Qt.AlignCenter)
        convert_layout.addWidget(convert_label)
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
        
        logger.info("MainWindow初始化完成")

def main():
    try:
        logger.info("创建QApplication")
        app = QApplication(sys.argv)
        
        logger.info("创建MainWindow")
        window = MainWindow()
        
        logger.info("显示MainWindow")
        window.show()
        
        logger.info("进入应用程序主循环")
        return_code = app.exec_()
        logger.info(f"应用程序退出，返回码: {return_code}")
        return return_code
    except Exception as e:
        logger.error(f"应用程序运行时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        
        # 尝试显示错误对话框
        try:
            app = QApplication.instance()
            if not app:
                app = QApplication(sys.argv)
            
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("错误")
            error_box.setText("应用程序启动失败")
            error_box.setInformativeText(str(e))
            error_box.setDetailedText(traceback.format_exc())
            error_box.exec_()
        except Exception as dialog_error:
            print(f"显示错误对话框时出错: {str(dialog_error)}")
            print(f"原始错误: {str(e)}")
            print(traceback.format_exc())
        
        return 1

if __name__ == "__main__":
    main()
