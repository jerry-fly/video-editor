#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
进程监控脚本
用于检测和终止异常的VideoEditor进程
"""

import os
import sys
import time
import psutil
import logging
import argparse
import signal
import tempfile
from datetime import datetime

# 设置日志记录
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
    except Exception:
        log_dir = os.path.dirname(os.path.abspath(__file__))

log_file = os.path.join(log_dir, f"process_monitor_{time.strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ProcessMonitor")

# 锁文件路径
LOCK_FILE_PATH = os.path.join(tempfile.gettempdir(), "video_editor_lock.pid")

def find_video_editor_processes():
    """查找所有VideoEditor相关进程"""
    video_editor_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            # 检查进程名称是否包含VideoEditor
            proc_name = proc.info['name'].lower()
            
            # 检查是否是VideoEditor相关进程
            is_video_editor = False
            
            # 检查进程名称
            if "videoeditor" in proc_name:
                is_video_editor = True
            
            # 检查命令行参数
            if not is_video_editor and "python" in proc_name:
                cmdline = proc.info['cmdline']
                if cmdline:
                    cmdline_str = " ".join([str(cmd) for cmd in cmdline if cmd])
                    if "run.py" in cmdline_str or "video_editor" in cmdline_str.lower():
                        is_video_editor = True
            
            if is_video_editor:
                # 获取更多进程信息
                try:
                    proc_info = proc.as_dict(attrs=['pid', 'name', 'cmdline', 'create_time', 'cpu_percent', 'memory_percent', 'status'])
                    video_editor_processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # 如果无法获取详细信息，至少保留基本信息
                    video_editor_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return video_editor_processes

def kill_process(pid, force=False):
    """终止指定PID的进程"""
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        
        if force:
            # 强制终止进程
            process.kill()
            logger.info(f"已强制终止进程: {pid} ({process_name})")
        else:
            # 正常终止进程
            process.terminate()
            
            # 等待进程终止
            try:
                process.wait(timeout=3)
                logger.info(f"已终止进程: {pid} ({process_name})")
            except psutil.TimeoutExpired:
                # 如果等待超时，强制终止
                process.kill()
                logger.warning(f"进程未响应终止信号，已强制终止: {pid} ({process_name})")
        
        return True
    except psutil.NoSuchProcess:
        logger.warning(f"进程不存在: {pid}")
        return False
    except psutil.AccessDenied:
        logger.error(f"无权限终止进程: {pid}")
        return False
    except Exception as e:
        logger.error(f"终止进程时出错: {pid}, 错误: {str(e)}")
        return False

def find_main_process():
    """查找主VideoEditor进程"""
    # 检查锁文件
    if os.path.exists(LOCK_FILE_PATH):
        try:
            with open(LOCK_FILE_PATH, 'r') as f:
                pid = int(f.read().strip())
            
            # 检查PID是否存在
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                proc_name = process.name().lower()
                
                # 检查是否是VideoEditor相关进程
                if "videoeditor" in proc_name or "python" in proc_name:
                    return pid
        except:
            pass
    
    # 如果锁文件不存在或无效，查找最早创建的进程
    processes = find_video_editor_processes()
    if processes:
        # 按创建时间排序
        processes.sort(key=lambda x: x.get('create_time', 0))
        return processes[0]['pid']
    
    return None

def monitor_processes(max_processes=2, check_interval=3, auto_kill=True, cpu_threshold=90, memory_threshold=90):
    """监控VideoEditor进程数量，如果超过阈值则发出警告或终止"""
    logger.info(f"开始监控VideoEditor进程 (最大允许数量: {max_processes}, 检查间隔: {check_interval}秒, 自动终止: {auto_kill})")
    logger.info(f"资源阈值: CPU {cpu_threshold}%, 内存 {memory_threshold}%")
    
    # 记录异常次数
    consecutive_high_count = 0
    max_consecutive_high = 5  # 连续5次高资源使用将触发紧急清理
    
    while True:
        processes = find_video_editor_processes()
        process_count = len(processes)
        
        if process_count > 0:
            # 计算资源使用情况
            total_cpu = 0
            total_memory = 0
            high_resource_procs = []
            
            for proc in processes:
                cpu_percent = proc.get('cpu_percent', 0)
                memory_percent = proc.get('memory_percent', 0)
                
                # 更新CPU使用率
                if cpu_percent == 0:
                    try:
                        p = psutil.Process(proc['pid'])
                        cpu_percent = p.cpu_percent(interval=0.1)
                        proc['cpu_percent'] = cpu_percent
                    except:
                        pass
                
                total_cpu += cpu_percent
                total_memory += memory_percent
                
                # 检查是否有进程使用过高资源
                if cpu_percent > cpu_threshold or memory_percent > memory_threshold:
                    high_resource_procs.append(proc)
            
            # 记录进程信息
            logger.info(f"当前VideoEditor进程数量: {process_count}, 总CPU: {total_cpu:.1f}%, 总内存: {total_memory:.1f}%")
            
            # 检查是否有资源使用过高的情况
            if high_resource_procs:
                logger.warning(f"发现 {len(high_resource_procs)} 个高资源占用进程")
                for proc in high_resource_procs:
                    logger.warning(f"进程 {proc['pid']} ({proc['name']}): CPU {proc.get('cpu_percent', 0):.1f}%, 内存 {proc.get('memory_percent', 0):.1f}%")
                
                consecutive_high_count += 1
                if consecutive_high_count >= max_consecutive_high:
                    logger.critical(f"连续 {consecutive_high_count} 次检测到高资源占用，执行紧急清理")
                    cleanup_processes(force=True, except_main=True)
                    consecutive_high_count = 0
            else:
                consecutive_high_count = 0
            
            # 按创建时间排序，最新的在前面
            processes.sort(key=lambda x: x.get('create_time', 0), reverse=True)
            
            # 如果进程数量超过阈值
            if process_count > max_processes:
                logger.warning(f"VideoEditor进程数量 ({process_count}) 超过阈值 ({max_processes})")
                
                if auto_kill:
                    # 查找主进程
                    main_pid = find_main_process()
                    
                    # 保留主进程和最新的几个进程，终止其余进程
                    pids_to_keep = [main_pid] if main_pid else []
                    
                    # 添加最新的进程到保留列表
                    for proc in processes[:max_processes]:
                        if proc['pid'] not in pids_to_keep:
                            pids_to_keep.append(proc['pid'])
                    
                    # 终止其余进程
                    for proc in processes:
                        if proc['pid'] not in pids_to_keep:
                            logger.warning(f"终止多余进程: {proc['pid']} ({proc['name']})")
                            kill_process(proc['pid'])
                else:
                    logger.warning("自动终止已禁用，请手动检查进程")
                    
                    # 打印所有进程信息
                    for i, proc in enumerate(processes):
                        create_time = datetime.fromtimestamp(proc.get('create_time', 0)).strftime('%Y-%m-%d %H:%M:%S')
                        logger.info(f"进程 {i+1}: PID={proc['pid']}, 名称={proc['name']}, 创建时间={create_time}")
        
        # 等待下一次检查
        time.sleep(check_interval)

def cleanup_processes(force=False, except_main=False):
    """清理所有VideoEditor进程"""
    processes = find_video_editor_processes()
    process_count = len(processes)
    
    if process_count > 0:
        logger.info(f"发现 {process_count} 个VideoEditor进程，准备清理...")
        
        # 如果需要保留主进程
        main_pid = None
        if except_main:
            main_pid = find_main_process()
            if main_pid:
                logger.info(f"将保留主进程: {main_pid}")
        
        for proc in processes:
            if except_main and proc['pid'] == main_pid:
                logger.info(f"保留主进程: {proc['pid']} ({proc['name']})")
                continue
                
            kill_process(proc['pid'], force=force)
        
        logger.info("清理完成")
    else:
        logger.info("未发现VideoEditor进程")

def emergency_cleanup():
    """紧急清理所有VideoEditor进程，包括主进程"""
    logger.critical("执行紧急清理，终止所有VideoEditor进程")
    
    # 强制终止所有进程
    cleanup_processes(force=True, except_main=False)
    
    # 清理锁文件
    if os.path.exists(LOCK_FILE_PATH):
        try:
            os.remove(LOCK_FILE_PATH)
            logger.info(f"已删除锁文件: {LOCK_FILE_PATH}")
        except:
            logger.error(f"删除锁文件失败: {LOCK_FILE_PATH}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="VideoEditor进程监控工具")
    parser.add_argument("--monitor", action="store_true", help="持续监控进程")
    parser.add_argument("--cleanup", action="store_true", help="清理所有VideoEditor进程")
    parser.add_argument("--emergency", action="store_true", help="紧急清理所有进程，包括主进程")
    parser.add_argument("--max", type=int, default=2, help="最大允许的进程数量 (默认: 2)")
    parser.add_argument("--interval", type=int, default=3, help="检查间隔，单位秒 (默认: 3)")
    parser.add_argument("--auto-kill", action="store_true", help="自动终止超出阈值的进程")
    parser.add_argument("--cpu", type=float, default=90, help="CPU使用率阈值，百分比 (默认: 90)")
    parser.add_argument("--memory", type=float, default=90, help="内存使用率阈值，百分比 (默认: 90)")
    
    args = parser.parse_args()
    
    if args.emergency:
        emergency_cleanup()
    elif args.cleanup:
        cleanup_processes()
    elif args.monitor:
        try:
            monitor_processes(
                args.max, 
                args.interval, 
                args.auto_kill,
                args.cpu,
                args.memory
            )
        except KeyboardInterrupt:
            logger.info("监控已停止")
    else:
        # 默认行为：显示当前进程
        processes = find_video_editor_processes()
        process_count = len(processes)
        
        if process_count > 0:
            logger.info(f"当前有 {process_count} 个VideoEditor进程:")
            
            # 按创建时间排序
            processes.sort(key=lambda x: x.get('create_time', 0))
            
            for i, proc in enumerate(processes):
                create_time = datetime.fromtimestamp(proc.get('create_time', 0)).strftime('%Y-%m-%d %H:%M:%S')
                cmdline = " ".join([str(cmd) for cmd in proc.get('cmdline', []) if cmd])
                logger.info(f"进程 {i+1}: PID={proc['pid']}, 名称={proc['name']}, 创建时间={create_time}")
                logger.info(f"  命令行: {cmdline[:100]}{'...' if len(cmdline) > 100 else ''}")
        else:
            logger.info("未发现VideoEditor进程")

if __name__ == "__main__":
    main() 