# 视频编辑器

一个简单易用的视频编辑工具，基于PyQt5和OpenCV开发。

## 功能特点

- **视频剪辑**：精确剪辑视频片段
- **视频合并**：将多个视频文件合并为一个
- **格式转换**：支持多种视频格式之间的转换
- **简洁界面**：直观易用的用户界面
- **高效处理**：多线程处理，提高效率

## 安装说明

### 方法一：从源代码运行

1. 克隆仓库：
   ```
   git clone https://github.com/jerry-fly/video-editor.git
   cd video-editor
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

3. 运行应用：
   ```
   python run.py
   ```

### 方法二：使用可执行文件

我们提供了打包好的可执行文件，可以直接下载使用：

- **Windows**: 下载 `视频编辑器.exe`
- **macOS**: 下载 `视频编辑器.app`
- **Linux**: 下载 `视频编辑器`

## 使用指南

### 视频剪辑

1. 点击"添加视频"按钮或拖放视频到界面中
2. 设置起始时间和结束时间
3. 点击"剪辑"按钮
4. 选择保存位置

### 视频合并

1. 点击"添加视频"按钮添加多个视频文件
2. 调整视频顺序（可选）
3. 点击"合并"按钮
4. 选择保存位置

### 格式转换

1. 添加需要转换的视频文件
2. 选择目标格式
3. 设置编码参数（可选）
4. 点击"转换"按钮
5. 选择保存位置

## 自定义构建

如果您想自行打包应用程序，我们提供了构建脚本：

```
python build_app.py
```

构建完成后，可执行文件将位于 `dist` 目录中。

### 自定义应用图标

应用程序使用了自定义图标，图标文件位于 `resources` 目录：

- `icon.png` - PNG格式图标
- `icon.ico` - Windows图标
- `icon.icns` - macOS图标

如果您想创建自己的图标，可以使用 `resources/icon.py` 脚本：

```
python resources/icon.py
```

这将生成所有必要的图标文件。

## 系统要求

- **操作系统**：Windows 7+, macOS 10.13+, 或 Linux
- **Python**：3.7 或更高版本
- **内存**：至少 4GB RAM
- **存储**：至少 200MB 可用空间

## 技术栈

- **UI框架**：PyQt5
- **视频处理**：OpenCV, FFmpeg, MoviePy
- **多线程**：Python threading

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件

## 贡献

欢迎贡献代码、报告问题或提出建议。请遵循以下步骤：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 联系方式

如有任何问题或建议，请通过以下方式联系我们：

- GitHub Issues：[https://github.com/jerry-fly/video-editor/issues](https://github.com/jerry-fly/video-editor/issues) 