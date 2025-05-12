#!/bin/bash

# 数据库重置脚本
# 此脚本会自动确认并运行reset_db.py

echo "=== 开始重置数据库 ==="
echo "将自动删除现有数据库并重建"

# 运行Python重置脚本并自动确认
echo "y" | python reset_db.py

# 检查执行结果
if [ $? -ne 0 ]; then
  echo "数据库重置失败，请检查错误信息"
  exit 1
fi

echo "=== 数据库重置成功 ==="
echo "您现在可以启动应用程序了" 