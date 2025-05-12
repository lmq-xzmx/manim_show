#!/usr/bin/env python
"""
快速修复数据库和迁移问题，重建数据库
"""
import os
import sys
import subprocess
import shutil

# 确保在Django环境中运行
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manim_edu.settings')

DB_FILE = 'db.sqlite3'
MIGRATION_DIRS = [
    'api/migrations',
    'animations/migrations',
    'core/migrations'
]

def run_command(cmd, desc=None):
    """运行命令并输出结果"""
    if desc:
        print(f"\n>>> {desc}")
    
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ 成功")
        if result.stdout.strip():
            print(result.stdout)
    else:
        print("✗ 失败")
        print(f"错误: {result.stderr}")
        sys.exit(1)
    
    return result

def main():
    """主程序"""
    print("=== 数据库快速修复工具 ===")
    
    # 1. 删除数据库文件
    if os.path.exists(DB_FILE):
        print(f"删除数据库文件: {DB_FILE}")
        os.remove(DB_FILE)
    
    # 2. 清理迁移文件(保留__init__.py)
    for directory in MIGRATION_DIRS:
        if os.path.exists(directory):
            print(f"清理迁移目录: {directory}")
            for filename in os.listdir(directory):
                if filename != '__init__.py' and os.path.isfile(os.path.join(directory, filename)):
                    os.remove(os.path.join(directory, filename))
    
    # 3. 创建新的迁移
    for app in ['api', 'animations', 'core']:
        run_command(['python', 'manage.py', 'makemigrations', app], f"为{app}创建迁移")
    
    # 4. 应用迁移
    run_command(['python', 'manage.py', 'migrate'], "应用迁移")
    
    # 5. 添加默认系统提示词
    run_command(['python', 'add_default_prompts.py'], "添加默认系统提示词")
    
    print("\n=== 修复完成 ===")
    print("数据库已重新创建，迁移文件已更新，默认系统提示词已添加")
    print("现在您可以重新启动应用程序了")

if __name__ == "__main__":
    main() 