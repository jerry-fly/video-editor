# Windows 使用指南

本文档提供了在 Windows 系统上运行和构建视频编辑器应用程序的详细说明。

## 前提条件

在开始之前，请确保您的系统满足以下要求：

1. 已安装 Python 3.8 或更高版本
2. Python 已添加到系统 PATH 环境变量中
3. 具有管理员权限（某些操作可能需要）
4. **至少 2GB 的可用磁盘空间**（构建可执行文件时需要）

## 重要提示：磁盘空间和进程问题

我们发现在某些 Windows 系统上，应用程序可能会出现以下问题：

1. **进程异常增殖**：应用程序可能会创建大量进程并耗尽系统资源
2. **磁盘空间耗尽**：构建过程或运行时可能会消耗大量磁盘空间

我们已经实施了多项措施来解决这些问题：

1. 增强的单实例检查机制
2. 严格的进程监控和自动终止
3. 紧急清理工具
4. 磁盘空间检查和清理工具

**如果您遇到"no space left on device"错误或应用程序创建大量进程，请立即运行 `disk_cleanup_en.bat` 和 `emergency_cleanup_en.bat` 进行清理。**

## 批处理文件说明

本项目包含以下批处理文件，用于简化在 Windows 上的操作：

### 1. safe_run_en.bat (推荐使用)

安全模式启动应用程序，包含增强的进程监控功能。此批处理文件将：
- 检查 Python 环境
- 安装 psutil 库（用于进程监控）
- 执行紧急清理，终止所有现有的 VideoEditor 进程
- 启动增强的进程监控（限制最多 1 个实例，监控 CPU 和内存使用）
- 启动应用程序（优先使用已构建的可执行文件）

使用方法：双击 `safe_run_en.bat` 文件

### 2. emergency_cleanup_en.bat

紧急清理工具，用于强制终止所有 VideoEditor 相关进程。当应用程序出现异常增殖或无法正常关闭时使用。

使用方法：双击 `emergency_cleanup_en.bat` 文件

### 3. disk_cleanup_en.bat (新增)

磁盘清理工具，用于释放磁盘空间。当遇到"no space left on device"错误或磁盘空间不足时使用。

使用方法：双击 `disk_cleanup_en.bat` 文件

### 4. run_app_en.bat

基本运行模式，用于运行视频编辑器应用程序。此批处理文件将：
- 检查 Python 环境
- 安装必要的依赖项
- 确保 NumPy 版本兼容性
- 启动应用程序

使用方法：双击 `run_app_en.bat` 文件

### 5. build_debug_en.bat

构建带有控制台窗口的调试版本。此版本在运行时会显示控制台输出，便于诊断问题。

使用方法：双击 `build_debug_en.bat` 文件

### 6. build_release_en.bat

构建不带控制台窗口的发布版本。此版本适合正常使用。

使用方法：双击 `build_release_en.bat` 文件

## 常见问题解决

### 1. "No space left on device" 错误

如果您遇到"no space left on device"错误：

1. 立即运行 `disk_cleanup_en.bat` 清理磁盘空间
2. 运行 `emergency_cleanup_en.bat` 终止所有相关进程
3. 检查系统磁盘空间是否至少有 2GB 可用
4. 使用 Windows 磁盘清理工具 (cleanmgr) 释放更多空间
5. 重新尝试操作

### 2. 应用程序创建大量进程

如果应用程序创建大量进程并导致系统变慢或崩溃：

1. 立即运行 `emergency_cleanup_en.bat` 强制终止所有相关进程
2. 检查 `logs` 目录中的日志文件，查找可能的错误原因
3. 使用 `safe_run_en.bat` 重新启动应用程序，它会启用增强的进程监控

### 3. 应用程序无法启动

如果应用程序无法启动，请尝试以下步骤：

1. 运行 `emergency_cleanup_en.bat` 清理所有相关进程
2. 确保已安装所有依赖项：`pip install -r requirements.txt`
3. 确保 NumPy 版本兼容：`pip install "numpy<2.0.0" --upgrade`
4. 使用 `safe_run_en.bat` 启动应用程序

### 4. 构建失败

如果构建过程失败，请尝试以下步骤：

1. 运行 `disk_cleanup_en.bat` 清理磁盘空间
2. 确保已安装 PyInstaller：`pip install pyinstaller==6.1.0`
3. 确保 NumPy 版本兼容：`pip install "numpy<2.0.0" --upgrade`
4. 确保已安装所有依赖项：`pip install -r requirements.txt`
5. 尝试使用管理员权限运行批处理文件

## 高级用法

### 使用 process_monitor.py

`process_monitor.py` 脚本提供了更多高级选项：

```
python process_monitor.py --help
```

常用选项：
- `--cleanup`：清理所有 VideoEditor 进程（正常终止）
- `--emergency`：紧急清理所有进程（强制终止）
- `--monitor`：持续监控进程
- `--max N`：设置最大允许的进程数量
- `--interval N`：设置检查间隔（秒）
- `--auto-kill`：自动终止超出阈值的进程
- `--cpu N`：设置 CPU 使用率阈值（百分比）
- `--memory N`：设置内存使用率阈值（百分比）

例如，启动严格的进程监控：
```
python process_monitor.py --monitor --max 1 --interval 1 --auto-kill --cpu 70 --memory 70
```

## 注意事项

1. 所有批处理文件都使用 UTF-8 编码，以确保正确显示所有字符
2. 如果您的系统语言不是英文，可能需要调整系统编码设置
3. 请确保在运行批处理文件之前，没有其他程序锁定相关文件
4. 构建可执行文件需要至少 2GB 的可用磁盘空间
5. 如果应用程序仍然出现问题，请尝试以下操作：
   - 检查系统防病毒软件是否阻止了某些操作
   - 尝试以管理员身份运行批处理文件
   - 检查 Python 环境是否正确安装 