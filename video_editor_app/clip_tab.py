#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cv2
import tempfile
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QSlider, QProgressBar, 
                            QMessageBox, QFrame, QStyle, QGroupBox, QFormLayout, 
                            QSpinBox, QLineEdit, QDialog, QSplitter, QStyleOptionSlider)
from PyQt5.QtCore import Qt, QTimer, QUrl, QSize, pyqtSignal, QThread, QRect
from PyQt5.QtGui import QIcon, QDrag, QPixmap, QPainter, QColor, QBrush, QPen
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from moviepy.editor import VideoFileClip

class VideoProcessThread(QThread):
    progress_updated = pyqtSignal(int)
    process_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, input_file, output_file, start_time, end_time):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.start_time = start_time
        self.end_time = end_time
        
    def run(self):
        try:
            # 使用moviepy裁剪视频
            video = VideoFileClip(self.input_file)
            
            # 如果结束时间为None，则使用视频总时长
            if self.end_time is None:
                self.end_time = video.duration
                
            # 如果开始时间为None，则使用0
            if self.start_time is None:
                self.start_time = 0
                
            # 裁剪视频
            clip = video.subclip(self.start_time, self.end_time)
            
            # 发送50%进度信号
            self.progress_updated.emit(50)
            
            # 写入输出文件
            clip.write_videofile(self.output_file, 
                                codec='libx264', 
                                audio_codec='aac',
                                temp_audiofile=os.path.join(tempfile.gettempdir(), "temp-audio.m4a"),
                                remove_temp=True)
            
            # 关闭视频对象
            video.close()
            clip.close()
            
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
        self.setMinimumHeight(80)
        self.setMaximumHeight(80)
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

class ClipSlider(QSlider):
    """自定义QSlider，用于显示裁剪区域"""
    
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

class VideoClipTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # 初始化变量
        self.video_path = None
        self.start_time = None
        self.end_time = None
        self.video_duration = 0
        self.is_playing = False
        self.process_thread = None
        self.video_width = 0
        self.video_height = 0
        
        # 初始化媒体播放器
        self.media_player = QMediaPlayer(self)
        self.media_player.setNotifyInterval(100)  # 设置通知间隔为100毫秒
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.stateChanged.connect(self.media_state_changed)
        
        # 初始化UI
        self.initUI()
        
        # 禁用视频控制按钮
        self.set_video_controls_enabled(False)
        
        # 获取屏幕尺寸
        self.update_screen_size()
        
    def update_screen_size(self):
        """获取当前屏幕尺寸"""
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry(desktop.primaryScreen())
        self.screen_width = screen_rect.width()
        self.screen_height = screen_rect.height()
        
    def resizeEvent(self, event):
        """窗口大小改变时调整视频预览区域大小"""
        super().resizeEvent(event)
        if hasattr(self, 'video_widget') and self.video_width > 0 and self.video_height > 0:
            self.adjust_video_size()
            
    def adjust_video_size(self):
        """根据视频尺寸和窗口尺寸调整视频预览区域大小"""
        if self.video_width <= 0 or self.video_height <= 0:
            return
            
        # 获取当前预览区域的尺寸
        preview_width = self.preview_frame.width()
        preview_height = self.preview_frame.height()
        
        if preview_width <= 0 or preview_height <= 0:
            # 如果预览区域尺寸无效，延迟调整
            QTimer.singleShot(100, self.adjust_video_size)
            return
            
        # 计算视频的宽高比
        video_ratio = self.video_width / self.video_height
        
        # 计算预览区域的宽高比
        preview_ratio = preview_width / preview_height
        
        # 清除之前的限制
        self.video_widget.setMinimumSize(1, 1)
        self.video_widget.setMaximumSize(16777215, 16777215)  # Qt的最大值
        
        # 根据宽高比调整视频预览区域大小
        if abs(video_ratio - preview_ratio) < 0.1:
            # 如果比例接近，填充整个预览区域
            self.video_widget.setFixedSize(preview_width, preview_height)
        elif video_ratio > preview_ratio:
            # 视频更宽，以宽度为基准
            new_height = int(preview_width / video_ratio)
            if new_height > 0:
                self.video_widget.setFixedSize(preview_width, new_height)
        else:
            # 视频更高，以高度为基准
            new_width = int(preview_height * video_ratio)
            if new_width > 0:
                self.video_widget.setFixedSize(new_width, preview_height)
        
        # 确保视频组件可见
        self.video_widget.show()
        self.video_widget.raise_()
        
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
        self.drop_area.setMinimumHeight(60)  # 进一步减小高度
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
        
        # 创建主要内容区域 - 使用QSplitter分割视频预览和控制区域
        self.content_splitter = QSplitter(Qt.Vertical)
        self.content_splitter.setHandleWidth(1)  # 设置分割线宽度
        self.content_splitter.setChildrenCollapsible(False)  # 防止区域被完全折叠
        
        # 视频预览区域
        self.preview_frame = QFrame()
        self.preview_frame.setMinimumHeight(300)  # 设置最小高度
        self.preview_frame.setStyleSheet("background-color: #1a1b26; border-radius: 5px;")
        
        # 添加视频预览组件
        preview_layout = QVBoxLayout(self.preview_frame)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建视频播放组件
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: #1a1b26; border-radius: 5px;")
        preview_layout.addWidget(self.video_widget)
        
        # 设置媒体播放器的视频输出
        self.media_player.setVideoOutput(self.video_widget)
        
        # 添加视频控制按钮区域
        controls_frame = QFrame()
        controls_frame.setStyleSheet("background-color: #313244; border-radius: 5px; padding: 5px;")
        controls_frame.setMinimumHeight(180)  # 减小最小高度
        controls_frame.setMaximumHeight(220)  # 减小最大高度
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(2)  # 减小间距
        controls_layout.setContentsMargins(5, 5, 5, 5)  # 减小内边距
        
        # 进度条和时间显示
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(0)  # 减小间距为0
        progress_layout.setContentsMargins(0, 0, 0, 0)  # 移除内边距
        
        # 进度条
        self.progress_slider = ClipSlider(Qt.Horizontal)  # 使用自定义滑块
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #313244;
                height: 8px;
                background: #313244;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #89b4fa;
                border: 1px solid #89b4fa;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #89b4fa;
                border-radius: 4px;
            }
        """)
        self.progress_slider.sliderMoved.connect(self.set_position)
        self.progress_slider.sliderPressed.connect(self.slider_pressed)
        self.progress_slider.sliderReleased.connect(self.slider_released)
        # 添加鼠标点击事件
        self.progress_slider.mousePressEvent = self.progress_slider_mouse_press
        progress_layout.addWidget(self.progress_slider)
        
        # 时间显示布局
        time_layout = QHBoxLayout()
        time_layout.setAlignment(Qt.AlignCenter)
        time_layout.setSpacing(3)  # 减小间距
        time_layout.setContentsMargins(0, 0, 0, 0)  # 移除内边距
        
        # 当前时间标签
        self.current_time_label = QLabel("00:00:00")
        self.current_time_label.setStyleSheet("color: #cdd6f4; font-size: 11px;")
        time_layout.addWidget(self.current_time_label)
        
        time_layout.addWidget(QLabel("/"))
        
        # 总时长标签
        self.duration_label = QLabel("00:00:00")
        self.duration_label.setStyleSheet("color: #cdd6f4; font-size: 11px;")
        time_layout.addWidget(self.duration_label)
        
        # 裁剪时长标签
        self.clip_duration_label = QLabel("裁剪: 00:00:00")
        self.clip_duration_label.setAlignment(Qt.AlignRight)
        self.clip_duration_label.setStyleSheet("color: #cdd6f4; font-size: 11px; font-weight: bold;")
        time_layout.addStretch(1)
        time_layout.addWidget(self.clip_duration_label)
        
        progress_layout.addLayout(time_layout)
        
        controls_layout.addLayout(progress_layout)
        
        # 播放控制按钮和快进快退按钮合并到一行
        media_controls_layout = QHBoxLayout()
        media_controls_layout.setAlignment(Qt.AlignCenter)
        media_controls_layout.setSpacing(3)  # 减小间距
        media_controls_layout.setContentsMargins(0, 0, 0, 5)  # 减小内边距，只保留底部5px
        
        # 快退30秒按钮
        self.rewind_30_btn = QPushButton("<<30")
        self.rewind_30_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """)
        self.rewind_30_btn.clicked.connect(lambda: self.seek_relative(-30))
        media_controls_layout.addWidget(self.rewind_30_btn)
        
        # 快退10秒按钮
        self.rewind_10_btn = QPushButton("<<10")
        self.rewind_10_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """)
        self.rewind_10_btn.clicked.connect(lambda: self.seek_relative(-10))
        media_controls_layout.addWidget(self.rewind_10_btn)
        
        # 播放/暂停按钮
        self.play_btn = QPushButton("播放")
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.setIconSize(QSize(14, 14))
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
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
        self.play_btn.clicked.connect(self.toggle_play)
        media_controls_layout.addWidget(self.play_btn)
        
        # 停止按钮
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_btn.setIconSize(QSize(14, 14))
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f5c2e7;
            }
            QPushButton:pressed {
                background-color: #eba0ac;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_playback)
        media_controls_layout.addWidget(self.stop_btn)
        
        # 快进10秒按钮
        self.forward_10_btn = QPushButton("10>>")
        self.forward_10_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """)
        self.forward_10_btn.clicked.connect(lambda: self.seek_relative(10))
        media_controls_layout.addWidget(self.forward_10_btn)
        
        # 快进30秒按钮
        self.forward_30_btn = QPushButton("30>>")
        self.forward_30_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """)
        self.forward_30_btn.clicked.connect(lambda: self.seek_relative(30))
        media_controls_layout.addWidget(self.forward_30_btn)
        
        controls_layout.addLayout(media_controls_layout)
        
        # 底部控制区域
        bottom_controls_layout = QHBoxLayout()
        bottom_controls_layout.setSpacing(5)  # 减小间距
        
        # 左侧：裁剪点设置按钮
        clip_points_layout = QHBoxLayout()
        clip_points_layout.setAlignment(Qt.AlignLeft)
        clip_points_layout.setSpacing(3)  # 减小间距
        
        # 设置起始点按钮
        self.set_start_btn = QPushButton("起点")
        self.set_start_btn.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #94e2d5;
            }
        """)
        self.set_start_btn.clicked.connect(self.set_start_point)
        clip_points_layout.addWidget(self.set_start_btn)
        
        # 设置结束点按钮
        self.set_end_btn = QPushButton("终点")
        self.set_end_btn.setStyleSheet("""
            QPushButton {
                background-color: #fab387;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f9e2af;
            }
        """)
        self.set_end_btn.clicked.connect(self.set_end_point)
        clip_points_layout.addWidget(self.set_end_btn)
        
        # 重置裁剪点按钮
        self.reset_points_btn = QPushButton("重置")
        self.reset_points_btn.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f5c2e7;
            }
        """)
        self.reset_points_btn.clicked.connect(self.reset_clip_points)
        clip_points_layout.addWidget(self.reset_points_btn)
        
        bottom_controls_layout.addLayout(clip_points_layout)
        
        # 中间：剪辑参数
        params_layout = QHBoxLayout()
        params_layout.setAlignment(Qt.AlignCenter)
        params_layout.setSpacing(5)  # 减小间距
        
        # 开始时间
        params_layout.addWidget(QLabel("开始:"))
        
        self.start_min_spin = QSpinBox()
        self.start_min_spin.setRange(0, 999)
        self.start_min_spin.setFixedWidth(45)  # 设置固定宽度
        self.start_min_spin.setStyleSheet("""
            QSpinBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 2px;
                font-size: 11px;
            }
        """)
        params_layout.addWidget(self.start_min_spin)
        
        params_layout.addWidget(QLabel("分"))
        
        self.start_sec_spin = QSpinBox()
        self.start_sec_spin.setRange(0, 59)
        self.start_sec_spin.setFixedWidth(45)  # 设置固定宽度
        self.start_sec_spin.setStyleSheet("""
            QSpinBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 2px;
                font-size: 11px;
            }
        """)
        params_layout.addWidget(self.start_sec_spin)
        
        params_layout.addWidget(QLabel("秒"))
        
        # 结束时间
        params_layout.addWidget(QLabel("结束:"))
        
        self.end_min_spin = QSpinBox()
        self.end_min_spin.setRange(0, 999)
        self.end_min_spin.setFixedWidth(45)  # 设置固定宽度
        self.end_min_spin.setStyleSheet("""
            QSpinBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 2px;
                font-size: 11px;
            }
        """)
        params_layout.addWidget(self.end_min_spin)
        
        params_layout.addWidget(QLabel("分"))
        
        self.end_sec_spin = QSpinBox()
        self.end_sec_spin.setRange(0, 59)
        self.end_sec_spin.setFixedWidth(45)  # 设置固定宽度
        self.end_sec_spin.setStyleSheet("""
            QSpinBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 2px;
                font-size: 11px;
            }
        """)
        params_layout.addWidget(self.end_sec_spin)
        
        params_layout.addWidget(QLabel("秒"))
        
        bottom_controls_layout.addLayout(params_layout)
        
        # 右侧：开始剪辑按钮
        self.start_clip_btn = QPushButton("开始剪辑")
        self.start_clip_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
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
        self.start_clip_btn.clicked.connect(self.show_output_dialog)
        bottom_controls_layout.addWidget(self.start_clip_btn)
        
        controls_layout.addLayout(bottom_controls_layout)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)
        
        # 将视频预览和控制区域添加到分割器
        self.content_splitter.addWidget(self.preview_frame)
        self.content_splitter.addWidget(controls_frame)
        
        # 设置分割器的初始大小比例
        self.content_splitter.setSizes([700, 300])  # 视频区域占更多空间
        
        # 添加分割器到主布局
        main_layout.addWidget(self.content_splitter, 1)  # 分割器占据所有剩余空间
        
        # 初始化禁用控件
        self.set_controls_enabled(False)
        
        # 初始化进度条拖动状态
        self.is_slider_pressed = False
        
        # 连接数值输入框的信号
        self.start_min_spin.valueChanged.connect(self.update_clip_from_spinbox)
        self.start_sec_spin.valueChanged.connect(self.update_clip_from_spinbox)
        self.end_min_spin.valueChanged.connect(self.update_clip_from_spinbox)
        self.end_sec_spin.valueChanged.connect(self.update_clip_from_spinbox)
        
    def set_controls_enabled(self, enabled):
        """启用或禁用控件"""
        self.start_clip_btn.setEnabled(enabled)
        self.start_min_spin.setEnabled(enabled)
        self.start_sec_spin.setEnabled(enabled)
        self.end_min_spin.setEnabled(enabled)
        self.end_sec_spin.setEnabled(enabled)
        
    def set_video_controls_enabled(self, enabled):
        """启用或禁用视频控制按钮"""
        self.play_btn.setEnabled(enabled)
        self.stop_btn.setEnabled(enabled)
        self.rewind_10_btn.setEnabled(enabled)
        self.rewind_30_btn.setEnabled(enabled)
        self.forward_10_btn.setEnabled(enabled)
        self.forward_30_btn.setEnabled(enabled)
        self.progress_slider.setEnabled(enabled)
        self.set_start_btn.setEnabled(enabled)
        self.set_end_btn.setEnabled(enabled)
        self.reset_points_btn.setEnabled(enabled)
        
    def media_state_changed(self, state):
        """媒体状态改变回调"""
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setText("暂停")
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.is_playing = True
        else:
            self.play_btn.setText("播放")
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.is_playing = False
            
    def stop_playback(self):
        """停止播放"""
        self.media_player.stop()
        self.is_playing = False
        
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
        self.set_controls_enabled(True)
        self.is_playing = False
        
        # 获取视频信息
        try:
            video = cv2.VideoCapture(file_path)
            
            # 获取视频格式
            _, ext = os.path.splitext(file_path)
            format_str = ext[1:].upper()
            
            # 获取分辨率
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # 保存视频尺寸
            self.video_width = width
            self.video_height = height
            
            # 获取帧率
            fps = video.get(cv2.CAP_PROP_FPS)
            
            # 获取视频总时长（毫秒）
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration_sec = total_frames / fps if fps > 0 else 0
            
            # 更新视频信息标签
            self.video_info_label.setText(
                f"已选择视频: {os.path.basename(file_path)}\n"
                f"格式: {format_str}, 分辨率: {width}x{height}, 帧率: {fps:.2f} fps\n"
                f"时长: {int(duration_sec//60)}分{int(duration_sec%60)}秒"
            )
            
            # 设置默认结束时间为视频总时长
            self.end_min_spin.setValue(int(duration_sec // 60))
            self.end_sec_spin.setValue(int(duration_sec % 60))
            
            video.release()
            
            # 加载视频到媒体播放器
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            
            # 启用视频控制按钮
            self.set_video_controls_enabled(True)
            
            # 调整视频尺寸以适应窗口
            self.adjust_video_size()
            
            # 根据视频尺寸调整窗口大小
            self.adjust_window_size()
            
            # 播放一帧然后暂停，以显示视频画面
            self.media_player.play()
            QTimer.singleShot(100, self.media_player.pause)
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法读取视频信息: {str(e)}")
            
    def adjust_window_size(self):
        """根据视频尺寸和屏幕尺寸调整窗口大小"""
        if self.video_width <= 0 or self.video_height <= 0:
            return
            
        # 更新屏幕尺寸
        self.update_screen_size()
        
        # 计算合适的窗口尺寸
        # 窗口宽度不超过屏幕宽度的85%
        max_width = int(self.screen_width * 0.85)
        # 窗口高度不超过屏幕高度的85%
        max_height = int(self.screen_height * 0.85)
        
        # 计算视频的宽高比
        video_ratio = self.video_width / self.video_height
        
        # 根据视频宽高比计算窗口尺寸
        if self.video_width > self.video_height:
            # 横向视频
            window_width = min(max_width, self.video_width + 50)  # 添加一些边距
            window_height = int(window_width / video_ratio) + 350  # 控制区域高度
        else:
            # 纵向视频
            window_height = min(max_height, self.video_height + 350)
            window_width = int((window_height - 350) * video_ratio) + 50  # 添加一些边距
            
        # 确保窗口尺寸不小于最小值
        window_width = max(window_width, 800)
        window_height = max(window_height, 600)
        
        # 确保窗口尺寸不超过屏幕尺寸
        window_width = min(window_width, max_width)
        window_height = min(window_height, max_height)
            
        # 获取主窗口
        main_window = self.window()
        
        # 调整主窗口大小
        main_window.resize(window_width, window_height)
        
        # 调整分割器比例
        total_height = self.content_splitter.height()
        video_height = int(total_height * 0.7)  # 视频区域占70%
        controls_height = total_height - video_height
        self.content_splitter.setSizes([video_height, controls_height])
        
    def toggle_play(self):
        """切换播放/暂停状态"""
        if self.is_playing:
            self.media_player.pause()
            self.play_btn.setText("播放")
        else:
            self.media_player.play()
            self.play_btn.setText("暂停")
            
        self.is_playing = not self.is_playing
        
    def update_position(self, position):
        """更新进度条位置"""
        # 只有在没有拖动进度条时才更新位置
        if not self.is_slider_pressed:
            self.progress_slider.setValue(position)
        
        # 更新当前时间标签
        seconds = position // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        self.current_time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # 注意：不在这里更新进度条样式，避免随播放位置变化
        
    def update_duration(self, duration):
        """更新视频总时长"""
        self.progress_slider.setRange(0, duration)
        self.video_duration = duration
        
        # 更新总时长标签
        seconds = duration // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        self.duration_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
    def set_position(self, position):
        """设置视频位置"""
        self.media_player.setPosition(position)
        
    def seek_relative(self, seconds):
        """相对当前位置跳转"""
        new_position = self.media_player.position() + seconds * 1000
        new_position = max(0, min(new_position, self.video_duration))
        self.media_player.setPosition(new_position)
        
    def set_start_point(self):
        """设置裁剪起始点"""
        self.start_time = self.media_player.position() / 1000  # 转换为秒
        
        # 更新裁剪时长显示
        self.update_clip_duration()
        
        # 更新进度条样式以显示裁剪区域
        self.update_progress_bar_style()
        
        # 更新数值输入框
        total_seconds = int(self.start_time)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        self.start_min_spin.setValue(minutes)
        self.start_sec_spin.setValue(seconds)
        
    def set_end_point(self):
        """设置裁剪结束点"""
        self.end_time = self.media_player.position() / 1000  # 转换为秒
        
        # 更新裁剪时长显示
        self.update_clip_duration()
        
        # 更新进度条样式以显示裁剪区域
        self.update_progress_bar_style()
        
        # 更新数值输入框
        total_seconds = int(self.end_time)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        self.end_min_spin.setValue(minutes)
        self.end_sec_spin.setValue(seconds)
        
    def reset_clip_points(self):
        """重置裁剪点"""
        # 清除裁剪点
        self.start_time = None
        self.end_time = None
        
        # 更新裁剪时长显示
        self.update_clip_duration()
        
        # 恢复进度条样式 - 确保完全清除绿色标记
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #313244;
                height: 8px;
                background: #313244;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #89b4fa;
                border: 1px solid #89b4fa;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #89b4fa;
                border-radius: 4px;
            }
        """)
        
        # 强制重绘进度条，确保视觉效果立即更新
        self.progress_slider.update()
        
        # 重置数值输入框
        if self.video_duration > 0:
            total_seconds = int(self.video_duration / 1000)
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            self.start_min_spin.setValue(0)
            self.start_sec_spin.setValue(0)
            self.end_min_spin.setValue(minutes)
            self.end_sec_spin.setValue(seconds)
        
    def update_clip_duration(self):
        """更新裁剪时长显示"""
        if self.start_time is not None and self.end_time is not None:
            if self.start_time < self.end_time:
                duration = self.end_time - self.start_time
            else:
                # 如果起始点在结束点之后，交换它们
                self.start_time, self.end_time = self.end_time, self.start_time
                duration = self.end_time - self.start_time
        elif self.start_time is not None:
            duration = (self.video_duration / 1000) - self.start_time
        elif self.end_time is not None:
            duration = self.end_time
        else:
            duration = 0
            
        # 更新裁剪时长标签
        hours = int(duration) // 3600
        minutes = (int(duration) % 3600) // 60
        seconds = int(duration) % 60
        self.clip_duration_label.setText(f"裁剪: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
    def update_progress_bar_style(self):
        """更新进度条样式，显示裁剪区域"""
        if self.start_time is None or self.end_time is None:
            # 没有裁剪点，恢复默认样式
            self.progress_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid #313244;
                    height: 8px;
                    background: #313244;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #89b4fa;
                    border: 1px solid #89b4fa;
                    width: 16px;
                    margin: -4px 0;
                    border-radius: 8px;
                }
                QSlider::sub-page:horizontal {
                    background: #89b4fa;
                    border-radius: 4px;
                }
            """)
            return
            
        # 计算裁剪区域的范围（毫秒）
        start_pos = int(self.start_time * 1000)
        end_pos = int(self.end_time * 1000)
        
        # 计算裁剪区域的百分比
        start_percent = start_pos / self.video_duration * 100
        end_percent = end_pos / self.video_duration * 100
        
        # 确保百分比值在有效范围内
        start_percent = max(0, min(start_percent, 100))
        end_percent = max(0, min(end_percent, 100))
        
        # 确保结束点大于起始点
        if start_percent >= end_percent:
            start_percent, end_percent = end_percent, start_percent
        
        # 更新进度条样式，使用QSS显示裁剪区域
        style = f"""
            QSlider::groove:horizontal {{
                border: 1px solid #313244;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #313244, 
                    stop:{start_percent/100} #313244, 
                    stop:{start_percent/100+0.001} #00ff00, 
                    stop:{end_percent/100} #00ff00, 
                    stop:{end_percent/100+0.001} #313244,
                    stop:1 #313244);
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: #89b4fa;
                border: 1px solid #89b4fa;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: #89b4fa;
                border-radius: 4px;
                /* 使用半透明的蓝色，这样可以看到下面的绿色，但颜色会有区分 */
                background-color: rgba(137, 180, 250, 120);
            }}
        """
        self.progress_slider.setStyleSheet(style)
        
    def show_output_dialog(self):
        """显示输出设置对话框"""
        if not self.video_path:
            QMessageBox.warning(self, "错误", "请先加载视频")
            return
            
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("输出设置")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
            }
        """)
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        
        # 输出文件路径布局
        path_layout = QHBoxLayout()
        path_layout.setSpacing(5)
        
        # 输出文件标签
        path_layout.addWidget(QLabel("输出文件:"))
        
        # 输出文件路径
        self.output_path_edit = QLineEdit()
        # 设置默认输出路径
        base_name = os.path.splitext(self.video_path)[0]
        self.output_path_edit.setText(f"{base_name}_剪辑.mp4")
        
        self.output_path_edit.setStyleSheet("""
            QLineEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        path_layout.addWidget(self.output_path_edit)
        
        # 浏览按钮
        browse_btn = QPushButton("浏览")
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """)
        browse_btn.clicked.connect(self.browse_output_file)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        # 确认按钮
        confirm_btn = QPushButton("开始剪辑")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
        """)
        confirm_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(confirm_btn)
        
        layout.addLayout(button_layout)
        
        # 显示对话框
        if dialog.exec() == QDialog.Accepted:
            self.start_clipping()
        
    def browse_output_file(self):
        """浏览输出文件路径"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存剪辑后的视频", "", "视频文件 (*.mp4)"
        )
        
        if file_path:
            # 确保文件扩展名为.mp4
            if not file_path.lower().endswith('.mp4'):
                file_path += '.mp4'
                
            self.output_path_edit.setText(file_path)
        
    def start_clipping(self):
        """开始裁剪视频"""
        if not self.video_path:
            QMessageBox.warning(self, "错误", "请先加载视频")
            return
            
        # 获取输出文件路径
        output_path = self.output_path_edit.text()
        if not output_path:
            QMessageBox.warning(self, "错误", "请设置输出文件路径")
            return
                
        # 显示进度条
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # 禁用控件
        self.set_controls_enabled(False)
        self.add_video_btn.setEnabled(False)
        self.start_clip_btn.setEnabled(False)
        
        # 获取开始和结束时间（从分钟和秒钟转换为秒）
        start_time = self.start_min_spin.value() * 60 + self.start_sec_spin.value()
        end_time = self.end_min_spin.value() * 60 + self.end_sec_spin.value()
        
        # 创建并启动处理线程
        self.process_thread = VideoProcessThread(
            self.video_path, output_path, start_time, end_time
        )
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
        self.start_clip_btn.setEnabled(True)
        
        # 显示成功消息
        QMessageBox.information(self, "成功", f"视频裁剪完成\n保存至: {output_file}")
        
    def on_process_error(self, error_msg):
        """处理错误回调"""
        self.progress_bar.setVisible(False)
        
        # 启用控件
        self.set_controls_enabled(True)
        self.add_video_btn.setEnabled(True)
        self.start_clip_btn.setEnabled(True)
        
        # 显示错误消息
        QMessageBox.critical(self, "错误", f"视频裁剪失败: {error_msg}")
        
    def slider_pressed(self):
        """进度条被按下"""
        self.is_slider_pressed = True
        
    def slider_released(self):
        """进度条被释放"""
        self.is_slider_pressed = False
        self.set_position(self.progress_slider.value())
        
    def progress_slider_mouse_press(self, event):
        """处理进度条的鼠标点击事件"""
        # 调用原始的鼠标按下事件处理
        QSlider.mousePressEvent(self.progress_slider, event)
        
        # 计算点击位置对应的值
        if self.progress_slider.maximum() > 0:
            x_pos = event.pos().x()
            slider_width = self.progress_slider.width()
            value_ratio = x_pos / slider_width
            value = int(value_ratio * self.progress_slider.maximum())
            
            # 设置进度条值
            self.progress_slider.setValue(value)
            
            # 设置视频位置
            self.set_position(value)
        
    def update_clip_from_spinbox(self):
        """从数值输入框更新裁剪点"""
        # 只有在视频已加载时才更新
        if self.video_path is None or self.video_duration == 0:
            return
            
        # 计算开始和结束时间（秒）
        start_time = self.start_min_spin.value() * 60 + self.start_sec_spin.value()
        end_time = self.end_min_spin.value() * 60 + self.end_sec_spin.value()
        
        # 确保结束时间大于开始时间
        if end_time <= start_time:
            # 如果是结束时间被调整到小于等于开始时间，则将结束时间设为开始时间+1秒
            if self.sender() in [self.end_min_spin, self.end_sec_spin]:
                end_time = start_time + 1
                minutes = end_time // 60
                seconds = end_time % 60
                self.end_min_spin.setValue(minutes)
                self.end_sec_spin.setValue(seconds)
            # 如果是开始时间被调整到大于等于结束时间，则将开始时间设为结束时间-1秒
            else:
                start_time = end_time - 1
                minutes = start_time // 60
                seconds = start_time % 60
                self.start_min_spin.setValue(minutes)
                self.start_sec_spin.setValue(seconds)
        
        # 确保时间不超过视频总时长
        max_time = self.video_duration / 1000
        if end_time > max_time:
            end_time = int(max_time)
            minutes = end_time // 60
            seconds = end_time % 60
            self.end_min_spin.setValue(minutes)
            self.end_sec_spin.setValue(seconds)
        
        # 更新裁剪点
        self.start_time = start_time
        self.end_time = end_time
        
        # 更新裁剪时长显示
        self.update_clip_duration()
        
        # 更新进度条样式
        self.update_progress_bar_style() 