#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cv2
import tempfile
import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QProgressBar, QMessageBox, 
                            QFrame, QComboBox, QSpinBox, QFormLayout, QStyle,
                            QGroupBox, QDoubleSpinBox, QLineEdit, QCheckBox)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QUrl
from PyQt5.QtGui import QIcon, QDrag, QPixmap, QPainter, QColor
from moviepy.editor import VideoFileClip

# 获取logger
logger = logging.getLogger("VideoEditor.convert")

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
                remove_temp=True,
                threads=2,
                logger=None
            )
            
            # 发送100%进度信号
            self.progress_updated.emit(100)
            
            # 发送完成信号
            self.process_finished.emit(self.output_file)
            
        except Exception as e:
            # 发送错误信号
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
        
        logger.info("初始化VideoConvertTab")
        
        # 创建布局
        self.main_layout = QVBoxLayout(self)
        
        # 创建文件选择区域
        self.create_file_selection_area()
        
        # 创建转换参数区域
        self.create_conversion_params_area()
        
        # 创建转换按钮和进度条
        self.create_convert_controls()
        
        # 初始化变量
        self.input_file = None
        self.convert_thread = None
        
        logger.info("VideoConvertTab初始化完成")
    
    def create_file_selection_area(self):
        # 创建文件选择组
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout(file_group)
        
        # 创建文件选择按钮
        file_button_layout = QHBoxLayout()
        
        self.add_file_button = QPushButton("添加视频")
        self.add_file_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogStart))
        self.add_file_button.clicked.connect(self.add_video_file)
        file_button_layout.addWidget(self.add_file_button)
        
        file_button_layout.addStretch()
        file_layout.addLayout(file_button_layout)
        
        # 创建文件信息标签
        self.file_info_label = QLabel("未选择文件")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.file_info_label.setStyleSheet("padding: 10px; background-color: #313244; border-radius: 4px;")
        file_layout.addWidget(self.file_info_label)
        
        # 添加到主布局
        self.main_layout.addWidget(file_group)
    
    def create_conversion_params_area(self):
        # 创建转换参数组
        params_group = QGroupBox("转换参数")
        params_layout = QFormLayout(params_group)
        
        # 创建格式选择下拉框
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "AVI", "MKV", "MOV", "WMV", "GIF"])
        params_layout.addRow("输出格式:", self.format_combo)
        
        # 创建视频编码选择下拉框
        self.video_codec_combo = QComboBox()
        self.video_codec_combo.addItems(["libx264", "mpeg4", "libxvid", "rawvideo"])
        params_layout.addRow("视频编码:", self.video_codec_combo)
        
        # 创建音频编码选择下拉框
        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.addItems(["aac", "mp3", "libvorbis"])
        params_layout.addRow("音频编码:", self.audio_codec_combo)
        
        # 创建帧率输入框
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(1, 120)
        self.fps_spinbox.setValue(30)
        params_layout.addRow("帧率 (FPS):", self.fps_spinbox)
        
        # 创建视频比特率输入框
        self.bitrate_edit = QLineEdit("5000k")
        params_layout.addRow("视频比特率:", self.bitrate_edit)
        
        # 创建音频比特率输入框
        self.audio_bitrate_edit = QLineEdit("192k")
        params_layout.addRow("音频比特率:", self.audio_bitrate_edit)
        
        # 创建分辨率设置
        resolution_layout = QHBoxLayout()
        
        self.resize_checkbox = QCheckBox("调整分辨率")
        resolution_layout.addWidget(self.resize_checkbox)
        
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(1, 7680)  # 支持8K分辨率
        self.width_spinbox.setValue(1280)
        self.width_spinbox.setEnabled(False)
        resolution_layout.addWidget(QLabel("宽:"))
        resolution_layout.addWidget(self.width_spinbox)
        
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(1, 4320)  # 支持8K分辨率
        self.height_spinbox.setValue(720)
        self.height_spinbox.setEnabled(False)
        resolution_layout.addWidget(QLabel("高:"))
        resolution_layout.addWidget(self.height_spinbox)
        
        # 连接复选框和分辨率输入框
        self.resize_checkbox.stateChanged.connect(self.toggle_resolution_inputs)
        
        params_layout.addRow("分辨率:", resolution_layout)
        
        # 添加到主布局
        self.main_layout.addWidget(params_group)
    
    def create_convert_controls(self):
        # 创建控制按钮布局
        controls_layout = QHBoxLayout()
        
        # 创建转换按钮
        self.convert_button = QPushButton("转换")
        self.convert_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setEnabled(False)
        controls_layout.addWidget(self.convert_button)
        
        # 添加到主布局
        self.main_layout.addLayout(controls_layout)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% - %v / %m")
        self.main_layout.addWidget(self.progress_bar)
    
    def toggle_resolution_inputs(self, state):
        # 启用或禁用分辨率输入框
        enabled = state == Qt.Checked
        self.width_spinbox.setEnabled(enabled)
        self.height_spinbox.setEnabled(enabled)
    
    def add_video_file(self):
        # 打开文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm);;所有文件 (*)"
        )
        
        if file_path:
            self.input_file = file_path
            file_name = os.path.basename(file_path)
            self.file_info_label.setText(f"已选择: {file_name}")
            self.convert_button.setEnabled(True)
            
            # 尝试获取视频信息
            try:
                video = VideoFileClip(file_path)
                info_text = (
                    f"已选择: {file_name}\n"
                    f"时长: {video.duration:.2f} 秒\n"
                    f"分辨率: {video.size[0]}x{video.size[1]}\n"
                    f"FPS: {video.fps:.2f}"
                )
                self.file_info_label.setText(info_text)
                
                # 设置默认分辨率为视频原始分辨率
                self.width_spinbox.setValue(video.size[0])
                self.height_spinbox.setValue(video.size[1])
                
                # 关闭视频对象
                video.close()
            except Exception as e:
                logger.error(f"获取视频信息时出错: {str(e)}")
    
    def start_conversion(self):
        if not self.input_file:
            QMessageBox.warning(self, "警告", "请先选择视频文件")
            return
        
        # 获取输出格式
        output_format = self.format_combo.currentText().lower()
        
        # 打开保存文件对话框
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "保存转换后的视频",
            "",
            f"{output_format.upper()} 文件 (*.{output_format});;所有文件 (*)"
        )
        
        if not output_file:
            return
        
        # 确保文件扩展名正确
        if not output_file.lower().endswith(f".{output_format}"):
            output_file += f".{output_format}"
        
        # 获取转换参数
        params = {
            'video_codec': self.video_codec_combo.currentText(),
            'audio_codec': self.audio_codec_combo.currentText(),
            'fps': self.fps_spinbox.value(),
            'bitrate': self.bitrate_edit.text(),
            'audio_bitrate': self.audio_bitrate_edit.text(),
            'resize': self.resize_checkbox.isChecked(),
            'resolution': (self.width_spinbox.value(), self.height_spinbox.value())
        }
        
        # 禁用控件
        self.convert_button.setEnabled(False)
        self.add_file_button.setEnabled(False)
        
        # 创建并启动转换线程
        self.convert_thread = VideoConvertThread(self.input_file, output_file, params)
        self.convert_thread.progress_updated.connect(self.update_progress)
        self.convert_thread.process_finished.connect(self.conversion_finished)
        self.convert_thread.error_occurred.connect(self.conversion_error)
        self.convert_thread.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def conversion_finished(self, output_file):
        # 重置进度条
        self.progress_bar.setValue(100)
        
        # 启用控件
        self.convert_button.setEnabled(True)
        self.add_file_button.setEnabled(True)
        
        # 显示完成消息
        QMessageBox.information(
            self,
            "转换完成",
            f"视频已成功转换并保存到:\n{output_file}"
        )
    
    def conversion_error(self, error_message):
        # 重置进度条
        self.progress_bar.setValue(0)
        
        # 启用控件
        self.convert_button.setEnabled(True)
        self.add_file_button.setEnabled(True)
        
        # 显示错误消息
        QMessageBox.critical(
            self,
            "转换错误",
            f"转换过程中出错:\n{error_message}"
        ) 