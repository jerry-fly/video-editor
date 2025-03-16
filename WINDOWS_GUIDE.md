# Windows 使用指南

本文档提供了在 Windows 系统上运行和构建视频编辑器应用程序的详细说明。

## 前提条件

在开始之前，请确保您的系统满足以下要求：

1. 已安装 Python 3.8 或更高版本
2. Python 已添加到系统 PATH 环境变量中
3. 具有管理员权限（某些操作可能需要）

## 批处理文件说明

本项目包含以下批处理文件，用于简化在 Windows 上的操作：

### 1. run_app_en.bat

用于运行视频编辑器应用程序。此批处理文件将：
- 检查 Python 环境
- 安装必要的依赖项
- 确保 NumPy 版本兼容性
- 启动应用程序

使用方法：双击 `run_app_en.bat` 文件

### 2. safe_run_en.bat

安全模式启动应用程序，包含进程监控功能。此批处理文件将：
- 检查 Python 环境
- 安装 psutil 库（用于进程监控）
- 清理可能存在的 VideoEditor 进程
- 启动进程监控（限制最多 2 个实例）
- 启动应用程序（优先使用已构建的可执行文件）

使用方法：双击 `safe_run_en.bat` 文件

### 3. cleanup_en.bat

清理所有 VideoEditor 相关进程。当应用程序出现异常或无法正常关闭时使用。

使用方法：双击 `cleanup_en.bat` 文件

### 4. build_debug_en.bat

构建带有控制台窗口的调试版本。此版本在运行时会显示控制台输出，便于诊断问题。

使用方法：双击 `build_debug_en.bat` 文件

### 5. build_release_en.bat

构建不带控制台窗口的发布版本。此版本适合正常使用。

使用方法：双击 `build_release_en.bat` 文件

## 常见问题解决

### 1. 应用程序无法启动

如果应用程序无法启动，请尝试以下步骤：

1. 运行 `cleanup_en.bat` 清理所有相关进程
2. 确保已安装所有依赖项：`pip install -r requirements.txt`
3. 确保 NumPy 版本兼容：`pip install "numpy<2.0.0" --upgrade`
4. 使用 `safe_run_en.bat` 启动应用程序

### 2. 构建失败

如果构建过程失败，请尝试以下步骤：

1. 确保已安装 PyInstaller：`pip install pyinstaller==6.1.0`
2. 确保 NumPy 版本兼容：`pip install "numpy<2.0.0" --upgrade`
3. 确保已安装所有依赖项：`pip install -r requirements.txt`
4. 尝试使用管理员权限运行批处理文件

### 3. 多个进程问题

如果发现应用程序创建了多个进程，请：

1. 立即运行 `cleanup_en.bat` 清理所有进程
2. 使用 `safe_run_en.bat` 启动应用程序，它会自动监控和限制进程数量

## 高级用法

### 使用 process_monitor.py

`process_monitor.py` 脚本提供了更多高级选项：

```
python process_monitor.py --help
```

常用选项：
- `--cleanup`：清理所有 VideoEditor 进程
- `--monitor`：持续监控进程
- `--max N`：设置最大允许的进程数量
- `--interval N`：设置检查间隔（秒）
- `--auto-kill`：自动终止超出阈值的进程

例如：
```
python process_monitor.py --monitor --max 3 --interval 2 --auto-kill
```

## 注意事项

1. 所有批处理文件都使用 UTF-8 编码，以确保正确显示所有字符
2. 如果您的系统语言不是英文，可能需要调整系统编码设置
3. 请确保在运行批处理文件之前，没有其他程序锁定相关文件 