#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cv2
import tempfile
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QProgressBar, QMessageBox, 
                            QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                            QCheckBox, QDialog, QLineEdit, QFormLayout, QStyle)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QUrl
from PyQt5.QtGui import QIcon, QDrag, QPixmap, QPainter, QColor
from moviepy.editor import VideoFileClip, concatenate_videoclips

class VideoMergeThread(QThread):
    progress_updated = pyqtSignal(int)
    process_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, input_files, output_file):
        super().__init__()
        self.input_files = input_files
        self.output_file = output_file
        
    def run(self):
        try:
            # 加载所有视频
            clips = []
            total_clips = len(self.input_files)
            
            for i, file in enumerate(self.input_files):
                # 更新进度
                self.progress_updated.emit(int((i / total_clips) * 50))
                
                # 加载视频
                clip = VideoFileClip(file)
                clips.append(clip)
                
            # 合并视频
            final_clip = concatenate_videoclips(clips)
            
            # 发送50%进度信号
            self.progress_updated.emit(50)
            
            # 写入输出文件
            final_clip.write_videofile(
                self.output_file, 
                codec='libx264', 
                audio_codec='aac',
                temp_audiofile=os.path.join(tempfile.gettempdir(), "temp-audio.m4a"),
                remove_temp=True
            )
            
            # 关闭视频对象
            for clip in clips:
                clip.close()
            final_clip.close()
            
            # 发送100%进度信号
            self.progress_updated.emit(100)
            
            # 发送完成信号
            self.process_finished.emit(self.output_file)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class VideoDropArea(QFrame):
    videos_dropped = pyqtSignal(list)
    
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
                    border-radius: 8px;
                }
            """)
            
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border: 2px dashed #89b4fa;
                border-radius: 8px;
            }
        """)
        
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = []
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                
                # 检查是否为视频文件
                video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
                if any(file_path.lower().endswith(ext) for ext in video_extensions):
                    file_paths.append(file_path)
            
            if file_paths:
                self.videos_dropped.emit(file_paths)
            else:
                QMessageBox.warning(self, "文件类型错误", "请拖放视频文件")
                
        self.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border: 2px dashed #89b4fa;
                border-radius: 8px;
            }
        """)

class OutputSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输出设置")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
            }
            QLineEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 5px;
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
        """)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        # 输出目录
        self.output_dir_edit = QLineEdit()
        self.output_dir_btn = QPushButton("浏览...")
        self.output_dir_btn.clicked.connect(self.browse_output_dir)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.output_dir_edit)
        dir_layout.addWidget(self.output_dir_btn)
        
        form_layout.addRow("输出目录:", dir_layout)
        
        # 输出文件名
        self.output_name_edit = QLineEdit("合成后视频")
        form_layout.addRow("输出文件名:", self.output_name_edit)
        
        layout.addLayout(form_layout)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 确认按钮
        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.confirm_btn)
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
    def browse_output_dir(self):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir_edit.setText(dir_path)
            
    def get_output_path(self):
        """获取输出路径"""
        output_dir = self.output_dir_edit.text()
        output_name = self.output_name_edit.text()
        
        # 确保文件名有扩展名
        if not output_name.lower().endswith('.mp4'):
            output_name += '.mp4'
            
        return os.path.join(output_dir, output_name)

class VideoMergeTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # 初始化变量
        self.video_files = []
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
        self.drop_area.videos_dropped.connect(self.add_videos)
        self.drop_area.setMinimumHeight(60)  # 减小高度
        self.drop_area.setMaximumHeight(60)  # 限制最大高度
        top_layout.addWidget(self.drop_area, 4)  # 拖放区域占4份宽度
        
        # 创建添加视频按钮（垂直布局）
        add_btn_layout = QVBoxLayout()
        add_btn_layout.setAlignment(Qt.AlignCenter)
        
        self.add_videos_btn = QPushButton("添加视频")
        self.add_videos_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.add_videos_btn.setIconSize(QSize(16, 16))
        self.add_videos_btn.setMinimumHeight(40)
        self.add_videos_btn.setStyleSheet("""
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
        self.add_videos_btn.clicked.connect(self.open_file_dialog)
        add_btn_layout.addWidget(self.add_videos_btn)
        
        top_layout.addLayout(add_btn_layout, 1)  # 按钮占1份宽度
        
        main_layout.addLayout(top_layout)
        
        # 创建视频列表表格
        self.videos_table = QTableWidget(0, 8)  # 增加为8列，包括码率
        self.videos_table.setHorizontalHeaderLabels(["选择", "视频文件", "时长", "格式", "分辨率", "帧率", "码率", "音频采样率"])
        self.videos_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.videos_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.videos_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.videos_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
                gridline-color: #313244;
            }
            QHeaderView::section {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                padding: 5px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #313244;
            }
            QTableWidget::item:selected {
                background-color: #45475a;
            }
        """)
        self.videos_table.setMinimumHeight(300)
        main_layout.addWidget(self.videos_table)
        
        # 创建底部控制区域
        bottom_layout = QHBoxLayout()
        
        # 左侧：视频排序和删除按钮
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        # 向上移动按钮
        self.move_up_btn = QPushButton("向上移动")
        self.move_up_btn.setStyleSheet("""
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
        self.move_up_btn.clicked.connect(self.move_video_up)
        control_layout.addWidget(self.move_up_btn)
        
        # 向下移动按钮
        self.move_down_btn = QPushButton("向下移动")
        self.move_down_btn.setStyleSheet("""
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
        self.move_down_btn.clicked.connect(self.move_video_down)
        control_layout.addWidget(self.move_down_btn)
        
        # 删除视频按钮
        self.remove_video_btn = QPushButton("删除视频")
        self.remove_video_btn.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #f5c2e7;
            }
        """)
        self.remove_video_btn.clicked.connect(self.remove_selected_video)
        control_layout.addWidget(self.remove_video_btn)
        
        bottom_layout.addLayout(control_layout)
        
        # 添加弹性空间
        bottom_layout.addStretch(1)
        
        # 右侧：开始拼接按钮
        self.start_merge_btn = QPushButton("开始拼接")
        self.start_merge_btn.setMinimumWidth(120)
        self.start_merge_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
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
        self.start_merge_btn.clicked.connect(self.start_merging)
        bottom_layout.addWidget(self.start_merge_btn)
        
        main_layout.addLayout(bottom_layout)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 初始化禁用控件
        self.set_controls_enabled(False)
        
    def set_controls_enabled(self, enabled):
        """启用或禁用控件"""
        self.move_up_btn.setEnabled(enabled)
        self.move_down_btn.setEnabled(enabled)
        self.remove_video_btn.setEnabled(enabled)
        self.start_merge_btn.setEnabled(enabled)
        
    def open_file_dialog(self):
        """打开文件对话框选择多个视频"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv)"
        )
        
        if file_paths:
            self.add_videos(file_paths)
            
    def add_videos(self, file_paths):
        """添加多个视频到列表"""
        for file_path in file_paths:
            if file_path not in self.video_files:
                self.video_files.append(file_path)
                self.add_video_to_table(file_path)
                
        # 启用控件
        if self.video_files:
            self.set_controls_enabled(True)
            
    def add_video_to_table(self, file_path):
        """将视频添加到表格"""
        row = self.videos_table.rowCount()
        self.videos_table.insertRow(row)
        
        # 创建复选框
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        checkbox_cell = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_cell)
        checkbox_layout.addWidget(checkbox)
        checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        
        # 设置单元格内容
        self.videos_table.setCellWidget(row, 0, checkbox_cell)
        self.videos_table.setItem(row, 1, QTableWidgetItem(os.path.basename(file_path)))
        
        # 获取视频信息
        try:
            video = cv2.VideoCapture(file_path)
            
            # 获取视频时长
            fps = video.get(cv2.CAP_PROP_FPS)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration_sec = total_frames / fps if fps > 0 else 0
            
            # 格式化时长为 时:分:秒
            hours = int(duration_sec // 3600)
            minutes = int((duration_sec % 3600) // 60)
            seconds = int(duration_sec % 60)
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            duration_item = QTableWidgetItem(duration_str)
            self.videos_table.setItem(row, 2, duration_item)
            
            # 获取视频格式
            _, ext = os.path.splitext(file_path)
            format_item = QTableWidgetItem(ext[1:].upper())
            self.videos_table.setItem(row, 3, format_item)
            
            # 获取分辨率
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            resolution_item = QTableWidgetItem(f"{width}x{height}")
            self.videos_table.setItem(row, 4, resolution_item)
            
            # 获取帧率
            fps_item = QTableWidgetItem(f"{fps:.2f} fps")
            self.videos_table.setItem(row, 5, fps_item)
            
            # 获取码率（估算值）
            # 使用文件大小和时长估算码率
            file_size = os.path.getsize(file_path)  # 字节
            bitrate = int((file_size * 8) / (duration_sec * 1000)) if duration_sec > 0 else 0  # kbps
            bitrate_item = QTableWidgetItem(f"{bitrate} kbps")
            self.videos_table.setItem(row, 6, bitrate_item)
            
            # 获取音频采样率
            # 注意：OpenCV不直接提供音频采样率，使用默认值
            # 实际应用中可以使用ffmpeg或其他库获取准确值
            audio_sample_rate = "44.1 kHz"  # 默认值
            audio_item = QTableWidgetItem(audio_sample_rate)
            self.videos_table.setItem(row, 7, audio_item)
            
            video.release()
            
        except Exception as e:
            # 如果无法获取视频信息，填充默认值
            self.videos_table.setItem(row, 2, QTableWidgetItem("未知"))
            self.videos_table.setItem(row, 3, QTableWidgetItem("未知"))
            self.videos_table.setItem(row, 4, QTableWidgetItem("未知"))
            self.videos_table.setItem(row, 5, QTableWidgetItem("未知"))
            self.videos_table.setItem(row, 6, QTableWidgetItem("未知"))
            self.videos_table.setItem(row, 7, QTableWidgetItem("未知"))
            
    def move_video_up(self):
        """将选中的视频向上移动"""
        current_row = self.videos_table.currentRow()
        if current_row > 0:
            # 交换表格行
            for col in range(1, self.videos_table.columnCount()):
                item1 = self.videos_table.item(current_row, col)
                item2 = self.videos_table.item(current_row - 1, col)
                
                if item1 and item2:
                    text1 = item1.text()
                    text2 = item2.text()
                    item1.setText(text2)
                    item2.setText(text1)
            
            # 交换复选框状态
            checkbox1 = self.videos_table.cellWidget(current_row, 0).findChild(QCheckBox)
            checkbox2 = self.videos_table.cellWidget(current_row - 1, 0).findChild(QCheckBox)
            
            if checkbox1 and checkbox2:
                state1 = checkbox1.isChecked()
                state2 = checkbox2.isChecked()
                checkbox1.setChecked(state2)
                checkbox2.setChecked(state1)
            
            # 交换视频文件列表中的位置
            self.video_files[current_row], self.video_files[current_row - 1] = \
                self.video_files[current_row - 1], self.video_files[current_row]
            
            # 选择移动后的行
            self.videos_table.setCurrentCell(current_row - 1, 0)
            
    def move_video_down(self):
        """将选中的视频向下移动"""
        current_row = self.videos_table.currentRow()
        if current_row < self.videos_table.rowCount() - 1 and current_row >= 0:
            # 交换表格行
            for col in range(1, self.videos_table.columnCount()):
                item1 = self.videos_table.item(current_row, col)
                item2 = self.videos_table.item(current_row + 1, col)
                
                if item1 and item2:
                    text1 = item1.text()
                    text2 = item2.text()
                    item1.setText(text2)
                    item2.setText(text1)
            
            # 交换复选框状态
            checkbox1 = self.videos_table.cellWidget(current_row, 0).findChild(QCheckBox)
            checkbox2 = self.videos_table.cellWidget(current_row + 1, 0).findChild(QCheckBox)
            
            if checkbox1 and checkbox2:
                state1 = checkbox1.isChecked()
                state2 = checkbox2.isChecked()
                checkbox1.setChecked(state2)
                checkbox2.setChecked(state1)
            
            # 交换视频文件列表中的位置
            self.video_files[current_row], self.video_files[current_row + 1] = \
                self.video_files[current_row + 1], self.video_files[current_row]
            
            # 选择移动后的行
            self.videos_table.setCurrentCell(current_row + 1, 0)
            
    def remove_selected_video(self):
        """删除选中的视频"""
        current_row = self.videos_table.currentRow()
        if current_row >= 0:
            self.videos_table.removeRow(current_row)
            self.video_files.pop(current_row)
            
            # 如果没有视频了，禁用控件
            if not self.video_files:
                self.set_controls_enabled(False)
                
    def get_selected_videos(self):
        """获取选中的视频文件列表"""
        selected_videos = []
        
        for row in range(self.videos_table.rowCount()):
            checkbox = self.videos_table.cellWidget(row, 0).findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                selected_videos.append(self.video_files[row])
                
        return selected_videos
        
    def check_video_formats(self, videos):
        """检查视频格式是否一致"""
        if not videos:
            return False
            
        formats = set()
        for video in videos:
            _, ext = os.path.splitext(video)
            formats.add(ext.lower())
            
        return len(formats) == 1
        
    def start_merging(self):
        """开始拼接视频"""
        # 获取选中的视频
        selected_videos = self.get_selected_videos()
        
        if not selected_videos:
            QMessageBox.warning(self, "错误", "请选择至少一个视频")
            return
            
        # 检查视频格式是否一致
        if not self.check_video_formats(selected_videos):
            QMessageBox.warning(self, "格式不一致", "选中的视频格式不一致，请选择相同格式的视频")
            return
            
        # 显示输出设置对话框
        dialog = OutputSettingsDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
            
        output_path = dialog.get_output_path()
        
        # 显示进度条
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # 禁用控件
        self.set_controls_enabled(False)
        self.add_videos_btn.setEnabled(False)
        
        # 创建并启动处理线程
        self.process_thread = VideoMergeThread(selected_videos, output_path)
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
        self.add_videos_btn.setEnabled(True)
        
        # 显示成功消息
        QMessageBox.information(self, "成功", f"视频拼接完成\n保存至: {output_file}")
        
    def on_process_error(self, error_msg):
        """处理错误回调"""
        self.progress_bar.setVisible(False)
        
        # 启用控件
        self.set_controls_enabled(True)
        self.add_videos_btn.setEnabled(True)
        
        # 显示错误消息
        QMessageBox.critical(self, "错误", f"视频拼接失败: {error_msg}") 