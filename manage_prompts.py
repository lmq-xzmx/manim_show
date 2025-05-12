#!/usr/bin/env python
"""
系统提示词管理工具
用法:
  python manage_prompts.py [选项]
选项:
  1 - 清除所有提示词并添加默认提示词
  2 - 保留现有提示词，仅添加新提示词
  如果不提供选项，将启动交互式菜单
"""
import sys
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manim_edu.settings')
django.setup()

# 导入提示词管理功能
from add_system_prompts import (
    add_system_prompts_with_clear,
    add_system_prompts_keep_existing,
    show_menu
)

def main():
    """主函数，处理命令行参数并执行相应操作"""
    # 检查命令行参数
    if len(sys.argv) > 1:
        choice = sys.argv[1]
        
        if choice == '1':
            print("执行: 清除所有提示词并添加默认提示词")
            add_system_prompts_with_clear()
        elif choice == '2':
            print("执行: 保留现有提示词，仅添加新提示词")
            add_system_prompts_keep_existing()
        else:
            print(f"错误: 无效的选项 '{choice}'")
            print("有效选项: 1=清除并添加, 2=保留并添加")
            return 1
    else:
        # 交互式菜单模式
        while True:
            choice = show_menu()
            
            if choice == '1':
                add_system_prompts_with_clear()
            elif choice == '2':
                add_system_prompts_keep_existing()
            elif choice == '0':
                print("退出程序")
                break
            else:
                print("无效选项，请重新选择")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 