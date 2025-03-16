# 视频编辑器

一个简单易用的视频编辑工具，支持视频剪辑、合并和格式转换功能。

## 功能特点

- 视频剪辑：设置起始点和结束点，裁剪视频片段
- 视频合并：将多个视频文件合并为一个
- 视频转换：转换视频格式，调整分辨率和码率

## 系统要求

- Windows 7/8/10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+)

## 安装方法

### 从预编译版本安装

1. 从[Releases](https://github.com/yourusername/video-editor/releases)页面下载适合您系统的预编译版本
2. 解压缩下载的文件
3. 运行可执行文件

### 从源代码安装

1. 克隆仓库：`git clone https://github.com/yourusername/video-editor.git`
2. 安装依赖：`pip install -r requirements.txt`
3. 运行应用：`python run.py`

## 在Windows上使用

为了方便Windows用户，我们提供了两个批处理文件：

- `run_app.bat` - 运行应用程序（会自动检查并安装依赖）
- `build_windows.bat` - 构建独立可执行文件

只需双击这些批处理文件即可执行相应的操作。

## 开发与测试

### 在Windows上构建应用程序

1. 确保已安装Python 3.8或更高版本
2. 安装所需依赖：
   ```
   pip install -r requirements.txt
   ```
3. 运行应用程序进行测试：
   ```
   python run.py
   ```
   或者双击 `run_app.bat`
4. 构建独立可执行文件：
   ```
   python build_app_unified.py
   ```
   或者双击 `build_windows.bat`
5. 构建完成后，可执行文件将位于`dist`目录中

### 在Windows上测试构建

可以使用提供的测试脚本来验证构建环境和构建过程：

```
python test_windows_build.py
```

此脚本将检查所需的依赖是否已安装，并尝试构建应用程序。

### 发布前的测试清单

在发布应用程序之前，请确保完成以下测试：

- [ ] 在本地环境中运行应用程序，测试所有功能
- [ ] 使用PyInstaller构建本地可执行文件并测试
- [ ] 检查所有平台上的UI是否正确显示
- [ ] 验证所有功能在打包后的应用程序中是否正常工作

## 项目结构

```
video-editor/
├── run.py                  # 应用程序入口点
├── run_app.bat             # Windows运行脚本
├── build_app_unified.py    # 构建脚本
├── build_windows.bat       # Windows构建脚本
├── test_windows_build.py   # Windows构建测试脚本
├── test_local.py           # 本地测试脚本
├── requirements.txt        # 依赖列表
├── README.md               # 项目说明
├── LICENSE                 # 许可证
├── RELEASE_NOTES.md        # 发布说明
├── resources/              # 资源文件
└── video_editor_app/       # 应用程序源代码
    ├── __init__.py
    ├── main.py             # 主窗口
    ├── clip_tab.py         # 视频剪辑功能
    ├── merge_tab.py        # 视频合并功能
    └── convert_tab.py      # 视频转换功能
```

## 贡献指南

1. Fork本仓库
2. 创建您的特性分支：`git checkout -b feature/amazing-feature`
3. 提交您的更改：`git commit -m 'Add some amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 提交Pull Request

## 许可证

本项目采用MIT许可证 - 详情请参阅[LICENSE](LICENSE)文件 