#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cv2
import tempfile
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QProgressBar, QMessageBox, 
                            QFrame, QComboBox, QSpinBox, QFormLayout, QStyle,
                            QGroupBox, QDoubleSpinBox, QLineEdit)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QUrl
from PyQt5.QtGui import QIcon, QDrag, QPixmap, QPainter, QColor
from moviepy.editor import VideoFileClip

class VideoConvertThread(QThread):
    progress_updated = pyqtSignal(int)
    process_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, input_file, output_file, params):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.params = params
        
    def run(self):
        try:
            # 加载视频
            video = VideoFileClip(self.input_file)
            
            # 发送25%进度信号
            self.progress_updated.emit(25)
            
            # 调整分辨率
            if self.params['resize']:
                width, height = self.params['resolution']
                video = video.resize(width=width, height=height)
            
            # 发送50%进度信号
            self.progress_updated.emit(50)
            
            # 写入输出文件
            video.write_videofile(
                self.output_file, 
                codec=self.params['video_codec'],
                audio_codec=self.params['audio_codec'],
                fps=self.params['fps'],
                bitrate=self.params['bitrate'],
                audio_bitrate=self.params['audio_bitrate'],
                temp_audiofile=os.path.join(tempfile.gettempdir(), "temp-audio.m4a"),
                remove_temp=True
            )
            
            # 关闭视频对象
            video.close()
            
            # 发送100%进度信号
            self.progress_updated.emit(100)
            
            # 发送完成信号
            self.process_finished.emit(self.output_file)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class VideoDropArea(QFrame):
    video_dropped = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setMinimumHeight(60)
        self.setMaximumHeight(60)
        self.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border: 2px dashed #89b4fa;
                border-radius: 8px;
            }
        """)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 添加提示标签
        self.label = QLabel("拖放视频文件到此处")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: none; font-size: 14px; color: #cdd6f4;")
        layout.addWidget(self.label)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    background-color: #45475a;
                    border: 2px dashed #89b4fa;
                    border-radius: 10px;
                }
            """)
            
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border: 2px dashed #89b4fa;
                border-radius: 10px;
            }
        """)
        
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            
            # 检查是否为视频文件
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
            if any(file_path.lower().endswith(ext) for ext in video_extensions):
                self.video_dropped.emit(file_path)
            else:
                QMessageBox.warning(self, "文件类型错误", "请拖放视频文件")
                
        self.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border: 2px dashed #89b4fa;
                border-radius: 10px;
            }
        """)

class VideoConvertTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 创建标签
        label = QLabel("视频转换功能正在开发中...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #cdd6f4;")
        main_layout.addWidget(label) 