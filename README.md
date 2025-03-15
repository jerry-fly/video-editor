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

#### 前提条件

- Python 3.7 或更高版本
- pip（Python包管理器）
- Git（可选，用于克隆仓库）

#### 所有系统通用步骤

1. 克隆仓库：
   ```
   git clone https://github.com/jerry-fly/video-editor.git
   cd video-editor
   ```
   
   或者直接下载ZIP压缩包并解压。

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

3. 运行应用：
   ```
   python run.py
   ```

#### Windows 特定步骤

1. 安装Python：
   - 从[Python官网](https://www.python.org/downloads/windows/)下载安装程序
   - 安装时勾选"Add Python to PATH"选项
   - 完成安装后，打开命令提示符(CMD)验证：`python --version`

2. 安装FFmpeg（视频处理所需）：
   - 从[FFmpeg官网](https://ffmpeg.org/download.html)下载Windows版本
   - 解压到任意目录，如`C:\ffmpeg`
   - 将FFmpeg的bin目录添加到系统PATH环境变量：`C:\ffmpeg\bin`
   - 重启命令提示符，验证安装：`ffmpeg -version`

3. 安装其他依赖：
   ```
   pip install PyQt5 opencv-python moviepy ffmpeg-python numpy
   ```

#### macOS 特定步骤

1. 安装Python（使用Homebrew）：
   ```
   brew install python
   ```

2. 安装FFmpeg：
   ```
   brew install ffmpeg
   ```

3. 安装PyQt5和其他依赖：
   ```
   pip3 install PyQt5 PyQt5-Qt5 PyQt5-sip
   pip3 install opencv-python moviepy ffmpeg-python numpy
   ```

#### Linux (Ubuntu/Debian) 特定步骤

1. 安装Python和相关工具：
   ```
   sudo apt update
   sudo apt install python3 python3-pip python3-dev
   ```

2. 安装FFmpeg和Qt依赖：
   ```
   sudo apt install ffmpeg
   sudo apt install qt5-default python3-pyqt5
   ```

3. 安装其他依赖：
   ```
   pip3 install opencv-python moviepy ffmpeg-python numpy
   ```

### 方法二：使用可执行文件

我们提供了打包好的可执行文件，可以直接下载使用：

- **Windows**: 
  - 下载 `视频编辑器.exe`
  - 双击运行即可，无需安装Python环境
  - 如遇到安全警告，点击"更多信息"然后"仍要运行"

- **macOS**: 
  - 下载 `视频编辑器.app`
  - 将应用拖到Applications文件夹
  - 首次运行时，右键点击应用图标，选择"打开"
  - 如提示未验证的开发者，前往"系统偏好设置 > 安全性与隐私"允许应用运行

- **Linux**: 
  - 下载 `视频编辑器`
  - 添加执行权限：`chmod +x 视频编辑器`
  - 运行：`./视频编辑器`

## 自定义构建

如果您想自行打包应用程序，我们提供了构建脚本：

### 构建前准备

1. 安装PyInstaller：
   ```
   pip install pyinstaller
   ```

2. 确保已安装所有依赖：
   ```
   pip install -r requirements.txt
   ```

### 各系统构建步骤

#### Windows

```
python build_app.py
```
构建完成后，可执行文件将位于 `dist\视频编辑器\视频编辑器.exe`

#### macOS

```
python build_app.py
```
构建完成后，应用程序将位于 `dist/视频编辑器.app`

如需创建DMG安装包：
```
hdiutil create -volname "视频编辑器" -srcfolder dist/视频编辑器.app -ov -format UDZO 视频编辑器.dmg
```

#### Linux

```
python build_app.py
```
构建完成后，可执行文件将位于 `dist/视频编辑器/视频编辑器`

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

#### 各系统图标要求

- **Windows**: 需要ICO格式，推荐包含16x16到256x256多种尺寸
- **macOS**: 需要ICNS格式，可使用iconutil命令从iconset生成
- **Linux**: 通常使用PNG或SVG格式，推荐512x512像素

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

## 系统要求

- **操作系统**：Windows 7+, macOS 10.13+, 或 Linux
- **Python**：3.7 或更高版本
- **内存**：至少 4GB RAM
- **存储**：至少 200MB 可用空间
- **处理器**：推荐多核处理器，以提高视频处理速度

## 技术栈

- **UI框架**：PyQt5
- **视频处理**：OpenCV, FFmpeg, MoviePy
- **多线程**：Python threading

## 常见问题解答

1. **Q: 应用程序无法启动怎么办？**  
   A: 确保已安装所有依赖，特别是PyQt5和FFmpeg。Windows用户需确保FFmpeg在系统PATH中。

2. **Q: 视频处理速度很慢怎么办？**  
   A: 视频处理是计算密集型任务，处理速度取决于视频大小和计算机性能。可以尝试降低输出视频分辨率或使用更高性能的计算机。

3. **Q: 支持哪些视频格式？**  
   A: 支持大多数常见格式，包括MP4, AVI, MOV, MKV, WMV, FLV等。

4. **Q: 在macOS上提示"无法打开，因为开发者无法验证"怎么办？**  
   A: 右键点击应用，选择"打开"，然后在弹出的对话框中再次点击"打开"。

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