#!/usr/bin/env python
"""
Django服务器管理工具 - 用于启动、停止和重新启动服务器
支持端口检查和数据库修复
"""
import os
import sys
import argparse
import subprocess
import signal
import time
import psutil
import socket

DEFAULT_PORT = 8000
DEFAULT_HOST = '127.0.0.1'

def check_port(host, port):
    """检查指定端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0  # 如果端口已被占用，则返回True

def find_process_by_port(port):
    """找到占用指定端口的进程"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    return proc
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    return None

def kill_process(pid):
    """结束指定PID的进程"""
    try:
        process = psutil.Process(pid)
        process.terminate()
        
        # 等待进程终止
        for _ in range(10):  # 最多等待10秒
            if not process.is_running():
                return True
            time.sleep(1)
        
        # 如果进程仍在运行，强制终止
        process.kill()
        return True
    except psutil.NoSuchProcess:
        print(f"进程 {pid} 已经不存在")
        return True
    except Exception as e:
        print(f"终止进程 {pid} 时出错: {e}")
        return False

def start_server(host=DEFAULT_HOST, port=DEFAULT_PORT, fix_db=False):
    """启动Django服务器"""
    # 检查端口是否已被占用
    if check_port(host, port):
        print(f"错误: 端口 {port} 已被占用")
        proc = find_process_by_port(port)
        
        if proc:
            print(f"端口被进程占用: PID={proc.pid}, 名称={proc.name()}")
            choice = input(f"是否终止该进程以释放端口? (y/n): ")
            if choice.lower() == 'y':
                if kill_process(proc.pid):
                    print(f"已终止进程 {proc.pid}")
                else:
                    print(f"无法终止进程 {proc.pid}, 请手动终止")
                    return False
            else:
                print("操作已取消")
                return False
        else:
            print("无法找到占用该端口的进程, 请手动检查")
            return False
    
    # 修复数据库(如果需要)
    if fix_db:
        print("执行数据库修复...")
        try:
            result = subprocess.run(["python", "quick_fix.py"], check=True)
            if result.returncode != 0:
                print("数据库修复失败，请检查错误信息")
                return False
        except Exception as e:
            print(f"数据库修复失败: {e}")
            return False
    
    # 启动服务器
    cmd = ["python", "manage.py", "runserver", f"{host}:{port}"]
    
    print(f"启动服务器: {' '.join(cmd)}")
    try:
        # 使用Popen启动为后台进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # 创建PID文件
        with open(".server.pid", "w") as f:
            f.write(str(process.pid))
        
        print(f"服务器已启动, PID: {process.pid}")
        print(f"访问地址: http://{host}:{port}")
        print("使用 'python server.py stop' 命令停止服务器")
        
        # 显示前几行输出以确认服务器已启动
        print("\n=== 服务器输出 ===")
        start_time = time.time()
        line_count = 0
        
        while time.time() - start_time < 5 and line_count < 10:  # 最多等待5秒或10行输出
            line = process.stdout.readline()
            if line:
                print(line.strip())
                line_count += 1
                if "Starting development server" in line:
                    break
            else:
                # 没有更多输出
                break
        
        print("=== 服务器已在后台运行 ===")
        return True
        
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        return False

def stop_server():
    """停止Django服务器"""
    # 检查PID文件
    if not os.path.exists(".server.pid"):
        print("找不到服务器PID文件，服务器可能未运行")
        
        # 检查是否有任何Django服务器进程在运行
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.name() == 'python' and any('runserver' in cmd for cmd in proc.cmdline()):
                    pid = proc.pid
                    print(f"找到Django服务器进程: PID={pid}")
                    choice = input(f"是否终止该进程? (y/n): ")
                    if choice.lower() == 'y':
                        if kill_process(pid):
                            print(f"已终止进程 {pid}")
                            return True
                        else:
                            print(f"无法终止进程 {pid}")
                            return False
                    else:
                        print("操作已取消")
                        return False
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
        
        print("未找到运行中的Django服务器进程")
        return False
    
    # 读取PID
    with open(".server.pid", "r") as f:
        try:
            pid = int(f.read().strip())
        except ValueError:
            print("PID文件内容无效")
            os.remove(".server.pid")
            return False
    
    # 尝试终止进程
    if kill_process(pid):
        print(f"已停止服务器 (PID: {pid})")
        os.remove(".server.pid")
        return True
    else:
        print(f"无法停止服务器 (PID: {pid})")
        return False

def restart_server(host=DEFAULT_HOST, port=DEFAULT_PORT, fix_db=False):
    """重启Django服务器"""
    # 先停止服务器
    stop_server()
    # 然后启动服务器
    return start_server(host, port, fix_db)

def status():
    """检查服务器状态"""
    # 检查PID文件
    if os.path.exists(".server.pid"):
        with open(".server.pid", "r") as f:
            try:
                pid = int(f.read().strip())
                try:
                    proc = psutil.Process(pid)
                    if proc.is_running() and 'python' in proc.name().lower():
                        cmdline = ' '.join(proc.cmdline())
                        if 'runserver' in cmdline:
                            print(f"服务器正在运行，PID: {pid}")
                            print(f"命令行: {cmdline}")
                            
                            # 检查占用的端口
                            for conn in proc.connections(kind='inet'):
                                if conn.status == 'LISTEN':
                                    print(f"监听地址: {conn.laddr.ip}:{conn.laddr.port}")
                            
                            # 显示进程运行时间
                            uptime = time.time() - proc.create_time()
                            hours, remainder = divmod(uptime, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            print(f"运行时间: {int(hours)}小时 {int(minutes)}分钟 {int(seconds)}秒")
                            
                            return True
                        else:
                            print(f"PID {pid} 是Python进程，但不是Django服务器")
                    else:
                        print(f"PID {pid} 不是有效的Django服务器进程")
                except psutil.NoSuchProcess:
                    print(f"PID {pid} 的进程不存在")
            except ValueError:
                print("PID文件内容无效")
        
        # 如果PID文件存在但进程不存在，删除PID文件
        os.remove(".server.pid")
    
    # 检查是否有任何Django服务器进程在运行
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.name() == 'python' and any('runserver' in cmd for cmd in proc.cmdline()):
                pid = proc.pid
                print(f"找到Django服务器进程: PID={pid} (PID文件不存在或已损坏)")
                
                # 创建新的PID文件
                with open(".server.pid", "w") as f:
                    f.write(str(pid))
                print(f"已创建新的PID文件")
                
                # 显示命令行和监听端口
                cmdline = ' '.join(proc.cmdline())
                print(f"命令行: {cmdline}")
                
                for conn in proc.connections(kind='inet'):
                    if conn.status == 'LISTEN':
                        print(f"监听地址: {conn.laddr.ip}:{conn.laddr.port}")
                
                return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    
    print("Django服务器未运行")
    return False

def main():
    parser = argparse.ArgumentParser(description="Django服务器管理工具")
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status'], 
                      help='要执行的操作: start=启动服务器, stop=停止服务器, restart=重启服务器, status=显示状态')
    parser.add_argument('--host', default=DEFAULT_HOST, help=f'服务器主机地址 (默认: {DEFAULT_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'服务器端口 (默认: {DEFAULT_PORT})')
    parser.add_argument('--fix-db', action='store_true', help='启动前修复数据库')
    
    args = parser.parse_args()
    
    if args.action == 'start':
        start_server(args.host, args.port, args.fix_db)
    elif args.action == 'stop':
        stop_server()
    elif args.action == 'restart':
        restart_server(args.host, args.port, args.fix_db)
    elif args.action == 'status':
        status()

if __name__ == "__main__":
    main() 