#!/usr/bin/env python
"""
重置数据库和迁移文件，并重新创建数据库结构
"""
import os
import sys
import shutil
import sqlite3
import subprocess

DB_FILE = 'db.sqlite3'

def run_command(cmd, desc=None):
    """运行命令并显示结果"""
    if desc:
        print(f"\n=== {desc} ===")
    
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("命令执行成功")
        if result.stdout.strip():
            print("输出:")
            print(result.stdout)
    else:
        print("命令执行失败")
        print("错误输出:")
        print(result.stderr)
        sys.exit(1)
    
    return result

def main():
    # 1. 检查环境
    print("=== 数据库重置工具 ===")
    
    if not os.path.exists('manage.py'):
        print("错误: 未找到manage.py文件，请确保在Django项目根目录运行此脚本")
        sys.exit(1)
    
    # 2. 询问用户确认
    confirm = input("此操作将删除所有数据和迁移文件，是否继续? (y/n): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        sys.exit(0)
    
    # 3. 删除数据库文件
    if os.path.exists(DB_FILE):
        try:
            print(f"删除数据库文件: {DB_FILE}")
            os.remove(DB_FILE)
        except Exception as e:
            print(f"删除数据库文件失败: {e}")
            sys.exit(1)
    
    # 4. 删除迁移文件
    migration_dirs = [
        'api/migrations',
        'animations/migrations',
        'core/migrations'
    ]
    
    for directory in migration_dirs:
        if os.path.exists(directory):
            try:
                print(f"清理迁移目录: {directory}")
                # 保留 __init__.py 文件
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    if filename != '__init__.py' and os.path.isfile(filepath):
                        os.remove(filepath)
            except Exception as e:
                print(f"清理迁移目录失败: {e}")
                sys.exit(1)
    
    # 5. 运行字段修正脚本
    if os.path.exists('fix_prompt_fields.py'):
        print("\n=== 运行字段修正脚本 ===")
        run_command(['python', 'fix_prompt_fields.py'], "修正SystemPrompt模型字段")
    else:
        print("警告: 未找到fix_prompt_fields.py脚本，将跳过字段修正步骤")
    
    # 6. 重新创建迁移文件
    apps = ['api', 'animations', 'core']
    for app in apps:
        run_command(['python', 'manage.py', 'makemigrations', app], f"为 {app} 创建迁移文件")
    
    # 7. 应用迁移
    run_command(['python', 'manage.py', 'migrate'], "应用迁移")
    
    # 8. 添加系统提示词
    run_command(['python', 'manage_prompts.py', '1'], "添加默认系统提示词")
    
    print("\n=== 数据库重置完成 ===")
    print("数据库已重置，迁移文件已重新创建，并添加了默认系统提示词")
    
if __name__ == "__main__":
    main() 