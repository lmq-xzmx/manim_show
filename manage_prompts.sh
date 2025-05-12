#!/bin/bash

# 系统提示词管理脚本
# 用法: ./manage_prompts.sh [选项]
# 选项:
#   1 - 清除所有提示词并添加默认提示词
#   2 - 保留现有提示词，仅添加新提示词
#   如果不提供选项，将启动交互式菜单

# 设置Python路径（如果需要）
# PYTHON=python3  # 取消注释并根据需要调整

# 使用默认的Python命令
PYTHON=${PYTHON:-python}

# 检查Python脚本是否存在
if [ ! -f "add_system_prompts.py" ]; then
    echo "错误: 找不到 add_system_prompts.py 脚本"
    exit 1
fi

# 根据命令行参数执行操作
if [ "$1" = "1" ]; then
    echo "执行: 清除所有提示词并添加默认提示词"
    $PYTHON add_system_prompts.py --mode 1
elif [ "$1" = "2" ]; then
    echo "执行: 保留现有提示词，仅添加新提示词"
    $PYTHON add_system_prompts.py --mode 2
else
    # 如果没有参数，启动交互式模式
    $PYTHON add_system_prompts.py
fi 