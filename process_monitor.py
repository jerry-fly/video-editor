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

def find_video_editor_processes():
    """查找所有VideoEditor相关进程"""
    video_editor_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'create_time']):
        try:
            # 检查进程名称是否包含VideoEditor
            if 'VideoEditor' in proc.info['name']:
                video_editor_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return video_editor_processes

def kill_process(pid):
    """终止指定PID的进程"""
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        process.terminate()
        logger.info(f"已终止进程: {pid} ({process_name})")
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

def monitor_processes(max_processes=5, check_interval=5, auto_kill=False):
    """监控VideoEditor进程数量，如果超过阈值则发出警告或终止"""
    logger.info(f"开始监控VideoEditor进程 (最大允许数量: {max_processes}, 检查间隔: {check_interval}秒, 自动终止: {auto_kill})")
    
    while True:
        processes = find_video_editor_processes()
        process_count = len(processes)
        
        if process_count > 0:
            logger.info(f"当前VideoEditor进程数量: {process_count}")
            
            # 按创建时间排序，最新的在前面
            processes.sort(key=lambda x: x.info['create_time'], reverse=True)
            
            # 如果进程数量超过阈值
            if process_count > max_processes:
                logger.warning(f"VideoEditor进程数量 ({process_count}) 超过阈值 ({max_processes})")
                
                if auto_kill:
                    # 保留最新的max_processes个进程，终止其余进程
                    processes_to_kill = processes[max_processes:]
                    logger.warning(f"将终止 {len(processes_to_kill)} 个进程")
                    
                    for proc in processes_to_kill:
                        kill_process(proc.info['pid'])
                else:
                    logger.warning("自动终止已禁用，请手动检查进程")
                    
                    # 打印所有进程信息
                    for i, proc in enumerate(processes):
                        create_time = datetime.fromtimestamp(proc.info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                        logger.info(f"进程 {i+1}: PID={proc.info['pid']}, 名称={proc.info['name']}, 创建时间={create_time}")
        
        # 等待下一次检查
        time.sleep(check_interval)

def cleanup_processes():
    """清理所有VideoEditor进程"""
    processes = find_video_editor_processes()
    process_count = len(processes)
    
    if process_count > 0:
        logger.info(f"发现 {process_count} 个VideoEditor进程，准备清理...")
        
        for proc in processes:
            kill_process(proc.info['pid'])
        
        logger.info("清理完成")
    else:
        logger.info("未发现VideoEditor进程")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="VideoEditor进程监控工具")
    parser.add_argument("--monitor", action="store_true", help="持续监控进程")
    parser.add_argument("--cleanup", action="store_true", help="清理所有VideoEditor进程")
    parser.add_argument("--max", type=int, default=5, help="最大允许的进程数量 (默认: 5)")
    parser.add_argument("--interval", type=int, default=5, help="检查间隔，单位秒 (默认: 5)")
    parser.add_argument("--auto-kill", action="store_true", help="自动终止超出阈值的进程")
    
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup_processes()
    elif args.monitor:
        try:
            monitor_processes(args.max, args.interval, args.auto_kill)
        except KeyboardInterrupt:
            logger.info("监控已停止")
    else:
        # 默认行为：显示当前进程
        processes = find_video_editor_processes()
        process_count = len(processes)
        
        if process_count > 0:
            logger.info(f"当前有 {process_count} 个VideoEditor进程:")
            
            for i, proc in enumerate(processes):
                create_time = datetime.fromtimestamp(proc.info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"进程 {i+1}: PID={proc.info['pid']}, 名称={proc.info['name']}, 创建时间={create_time}")
        else:
            logger.info("未发现VideoEditor进程")

if __name__ == "__main__":
    main() 