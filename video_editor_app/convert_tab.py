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
        
        # 初始化变量
        self.video_path = None
        self.process_thread = None
        
    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)  # 减小边距
        main_layout.setSpacing(10)  # 减小间距
        
        # 创建顶部区域（拖放区域和添加按钮并排）
        top_layout = QHBoxLayout()
        
        # 创建拖放区域
        self.drop_area = VideoDropArea()
        self.drop_area.video_dropped.connect(self.load_video)
        self.drop_area.setMinimumHeight(60)  # 减小高度
        self.drop_area.setMaximumHeight(60)  # 限制最大高度
        top_layout.addWidget(self.drop_area, 4)  # 拖放区域占4份宽度
        
        # 创建添加视频按钮（垂直布局）
        add_btn_layout = QVBoxLayout()
        add_btn_layout.setAlignment(Qt.AlignCenter)
        
        self.add_video_btn = QPushButton("添加视频")
        self.add_video_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.add_video_btn.setIconSize(QSize(16, 16))
        self.add_video_btn.setMinimumHeight(40)
        self.add_video_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
        """)
        self.add_video_btn.clicked.connect(self.open_file_dialog)
        add_btn_layout.addWidget(self.add_video_btn)
        
        top_layout.addLayout(add_btn_layout, 1)  # 按钮占1份宽度
        
        main_layout.addLayout(top_layout)
        
        # 创建视频信息标签
        self.video_info_label = QLabel("未选择视频")
        self.video_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_info_label.setStyleSheet("color: #cdd6f4; font-size: 12px; background-color: #313244; padding: 5px; border-radius: 5px;")
        self.video_info_label.setMinimumHeight(40)  # 减小高度
        self.video_info_label.setMaximumHeight(40)  # 限制最大高度
        main_layout.addWidget(self.video_info_label)
        
        # 创建主要内容区域
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        
        # 左侧：转换参数区域
        params_group = QGroupBox("转换参数")
        params_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #313244;
                border-radius: 5px;
                margin-top: 10px;
                font-size: 14px;
                color: #cdd6f4;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        params_layout = QFormLayout(params_group)
        params_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        params_layout.setSpacing(8)  # 减小间距
        
        # 输出格式
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "AVI", "MOV", "MKV", "FLV"])
        self.format_combo.setStyleSheet("""
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #45475a;
            }
        """)
        params_layout.addRow("输出格式:", self.format_combo)
        
        # 视频编解码器
        self.video_codec_combo = QComboBox()
        self.video_codec_combo.addItems(["libx264", "mpeg4", "libxvid", "libvpx"])
        self.video_codec_combo.setStyleSheet("""
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #45475a;
            }
        """)
        params_layout.addRow("视频编解码器:", self.video_codec_combo)
        
        # 分辨率
        resolution_layout = QHBoxLayout()
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 7680)  # 支持8K分辨率
        self.width_spin.setValue(1920)
        self.width_spin.setStyleSheet("""
            QSpinBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        resolution_layout.addWidget(self.width_spin)
        
        resolution_layout.addWidget(QLabel("x"))
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 4320)  # 支持8K分辨率
        self.height_spin.setValue(1080)
        self.height_spin.setStyleSheet("""
            QSpinBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        resolution_layout.addWidget(self.height_spin)
        
        # 保持原始分辨率选项
        self.keep_resolution_check = QComboBox()
        self.keep_resolution_check.addItems(["自定义", "保持原始"])
        self.keep_resolution_check.setStyleSheet("""
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #45475a;
            }
        """)
        self.keep_resolution_check.currentIndexChanged.connect(self.toggle_resolution)
        
        resolution_layout.addWidget(self.keep_resolution_check)
        
        params_layout.addRow("分辨率:", resolution_layout)
        
        # 帧率
        self.fps_spin = QDoubleSpinBox()
        self.fps_spin.setRange(1, 120)
        self.fps_spin.setValue(30)
        self.fps_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        params_layout.addRow("帧率 (fps):", self.fps_spin)
        
        # 视频比特率
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["500k", "1000k", "2000k", "5000k", "10000k", "20000k"])
        self.bitrate_combo.setCurrentIndex(2)  # 默认2000k
        self.bitrate_combo.setStyleSheet("""
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #45475a;
            }
        """)
        params_layout.addRow("视频比特率:", self.bitrate_combo)
        
        # 音频编解码器
        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.addItems(["aac", "mp3", "libvorbis"])
        self.audio_codec_combo.setStyleSheet("""
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #45475a;
            }
        """)
        params_layout.addRow("音频编解码器:", self.audio_codec_combo)
        
        # 音频比特率
        self.audio_bitrate_combo = QComboBox()
        self.audio_bitrate_combo.addItems(["64k", "128k", "192k", "256k", "320k"])
        self.audio_bitrate_combo.setCurrentIndex(1)  # 默认128k
        self.audio_bitrate_combo.setStyleSheet("""
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #45475a;
            }
        """)
        params_layout.addRow("音频比特率:", self.audio_bitrate_combo)
        
        content_layout.addWidget(params_group, 3)  # 参数区域占3份宽度
        
        # 右侧：输出设置区域
        output_group = QGroupBox("输出设置")
        output_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #313244;
                border-radius: 5px;
                margin-top: 10px;
                font-size: 14px;
                color: #cdd6f4;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(10)
        
        # 输出路径
        path_layout = QHBoxLayout()
        path_layout.setSpacing(5)
        
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setStyleSheet("""
            QLineEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        path_layout.addWidget(self.output_path_edit)
        
        self.browse_output_btn = QPushButton("浏览")
        self.browse_output_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """)
        self.browse_output_btn.clicked.connect(self.browse_output_file)
        path_layout.addWidget(self.browse_output_btn)
        
        output_layout.addLayout(path_layout)
        
        # 添加弹性空间
        output_layout.addStretch(1)
        
        # 开始转换按钮
        self.start_convert_btn = QPushButton("开始转换")
        self.start_convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
        """)
        self.start_convert_btn.clicked.connect(self.start_converting)
        output_layout.addWidget(self.start_convert_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #45475a;
                border-radius: 5px;
                text-align: center;
                background-color: #313244;
                color: #cdd6f4;
            }
            QProgressBar::chunk {
                background-color: #89b4fa;
                border-radius: 5px;
            }
        """)
        self.progress_bar.setVisible(False)
        output_layout.addWidget(self.progress_bar)
        
        content_layout.addWidget(output_group, 2)  # 输出设置区域占2份宽度
        
        main_layout.addLayout(content_layout, 1)  # 内容区域占据所有剩余空间
        
        # 初始化禁用控件
        self.set_controls_enabled(False)
        
    def set_controls_enabled(self, enabled):
        """启用或禁用控件"""
        self.format_combo.setEnabled(enabled)
        self.video_codec_combo.setEnabled(enabled)
        self.width_spin.setEnabled(enabled)
        self.height_spin.setEnabled(enabled)
        self.keep_resolution_check.setEnabled(enabled)
        self.fps_spin.setEnabled(enabled)
        self.bitrate_combo.setEnabled(enabled)
        self.audio_codec_combo.setEnabled(enabled)
        self.audio_bitrate_combo.setEnabled(enabled)
        self.output_path_edit.setEnabled(enabled)
        self.browse_output_btn.setEnabled(enabled)
        self.start_convert_btn.setEnabled(enabled)
        
    def toggle_resolution(self, index):
        """切换分辨率设置"""
        self.width_spin.setEnabled(index == 0)
        self.height_spin.setEnabled(index == 0)
        
    def open_file_dialog(self):
        """打开文件对话框选择视频"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv)"
        )
        
        if file_path:
            self.load_video(file_path)
            
    def load_video(self, file_path):
        """加载视频文件"""
        self.video_path = file_path
        
        # 获取视频信息
        try:
            video = cv2.VideoCapture(file_path)
            
            # 获取视频格式
            _, ext = os.path.splitext(file_path)
            format_str = ext[1:].upper()
            
            # 获取分辨率
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # 获取帧率
            fps = video.get(cv2.CAP_PROP_FPS)
            
            # 更新视频信息标签
            self.video_info_label.setText(
                f"已选择视频: {os.path.basename(file_path)}\n"
                f"格式: {format_str}, 分辨率: {width}x{height}, 帧率: {fps:.2f} fps"
            )
            
            # 更新分辨率输入框
            self.width_spin.setValue(width)
            self.height_spin.setValue(height)
            
            # 更新帧率输入框
            self.fps_spin.setValue(fps)
            
            # 设置默认输出路径
            base_name = os.path.splitext(file_path)[0]
            self.output_path_edit.setText(f"{base_name}_converted.mp4")
            
            video.release()
            
            # 启用控件
            self.set_controls_enabled(True)
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法读取视频信息: {str(e)}")
            
    def browse_output_file(self):
        """浏览输出文件路径"""
        # 获取当前选择的格式
        format_ext = self.format_combo.currentText().lower()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存转换后的视频", "", f"视频文件 (*.{format_ext})"
        )
        
        if file_path:
            # 确保文件扩展名正确
            if not file_path.lower().endswith(f".{format_ext}"):
                file_path += f".{format_ext}"
                
            self.output_path_edit.setText(file_path)
            
    def get_conversion_params(self):
        """获取转换参数"""
        params = {
            'resize': self.keep_resolution_check.currentIndex() == 0,
            'resolution': (self.width_spin.value(), self.height_spin.value()),
            'fps': self.fps_spin.value(),
            'video_codec': self.video_codec_combo.currentText(),
            'bitrate': self.bitrate_combo.currentText(),
            'audio_codec': self.audio_codec_combo.currentText(),
            'audio_bitrate': self.audio_bitrate_combo.currentText()
        }
        
        return params
        
    def start_converting(self):
        """开始转换视频"""
        if not self.video_path:
            QMessageBox.warning(self, "错误", "请先选择视频")
            return
            
        output_path = self.output_path_edit.text()
        if not output_path:
            QMessageBox.warning(self, "错误", "请设置输出文件路径")
            return
            
        # 获取转换参数
        params = self.get_conversion_params()
        
        # 显示进度条
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # 禁用控件
        self.set_controls_enabled(False)
        self.add_video_btn.setEnabled(False)
        
        # 创建并启动处理线程
        self.process_thread = VideoConvertThread(self.video_path, output_path, params)
        self.process_thread.progress_updated.connect(self.update_progress)
        self.process_thread.process_finished.connect(self.on_process_finished)
        self.process_thread.error_occurred.connect(self.on_process_error)
        self.process_thread.start()
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def on_process_finished(self, output_file):
        """处理完成回调"""
        self.progress_bar.setVisible(False)
        
        # 启用控件
        self.set_controls_enabled(True)
        self.add_video_btn.setEnabled(True)
        
        # 显示成功消息
        QMessageBox.information(self, "成功", f"视频转换完成\n保存至: {output_file}")
        
    def on_process_error(self, error_msg):
        """处理错误回调"""
        self.progress_bar.setVisible(False)
        
        # 启用控件
        self.set_controls_enabled(True)
        self.add_video_btn.setEnabled(True)
        
        # 显示错误消息
        QMessageBox.critical(self, "错误", f"视频转换失败: {error_msg}") 