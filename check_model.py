#!/usr/bin/env python
"""
检查SystemPrompt模型的字段
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manim_edu.settings')
django.setup()

try:
    from api.models import SystemPrompt
    
    # 打印模型字段
    print("SystemPrompt模型字段:")
    for field in SystemPrompt._meta.get_fields():
        print(f"- {field.name}")
    
    # 获取所有提示词
    prompts = SystemPrompt.objects.all()
    print(f"\n当前有 {prompts.count()} 个提示词:")
    
    for prompt in prompts:
        print(f"ID: {prompt.id}, 名称: {prompt.name}")
        # 尝试获取所有字段值
        for field in SystemPrompt._meta.get_fields():
            if hasattr(prompt, field.name):
                value = getattr(prompt, field.name)
                if field.name not in ['id', 'name']:
                    print(f"  {field.name}: {value if len(str(value)) < 50 else str(value)[:50] + '...'}")
    
except ImportError as e:
    print(f"导入错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc() 