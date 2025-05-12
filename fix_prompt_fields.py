#!/usr/bin/env python
"""
修正SystemPrompt模型的字段，确保字段名称一致
"""
import os
import sys
import re

def main():
    """主函数"""
    print("=== SystemPrompt模型字段修正工具 ===")
    
    # 1. 检查api/models.py文件
    models_file = 'api/models.py'
    if not os.path.exists(models_file):
        print(f"错误: 未找到{models_file}文件")
        sys.exit(1)
    
    # 2. 读取模型文件内容
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 3. 检查SystemPrompt模型的字段
    if 'prompt = models.TextField' in content:
        print("检测到字段: prompt")
        
        # 使用正则表达式检查是否有content字段
        content_field = re.search(r'content\s*=\s*models\.TextField', content)
        if content_field:
            print("检测到冲突字段: content")
            print("将修改add_system_prompts.py文件以使用prompt字段")
            
            # 修改add_system_prompts.py文件
            fix_add_system_prompts('prompt')
        else:
            print("模型字段名称一致，无需修改")
    elif 'content = models.TextField' in content:
        print("检测到字段: content")
        
        # 使用正则表达式检查是否有prompt字段
        prompt_field = re.search(r'prompt\s*=\s*models\.TextField', content)
        if prompt_field:
            print("检测到冲突字段: prompt")
            print("将修改add_system_prompts.py文件以使用content字段")
            
            # 修改add_system_prompts.py文件
            fix_add_system_prompts('content')
        else:
            print("模型字段名称一致，无需修改")
    else:
        print("警告: 未检测到SystemPrompt模型中的text字段")
        sys.exit(1)
    
    print("\n=== 字段检查完成 ===")

def fix_add_system_prompts(field_name):
    """修改add_system_prompts.py文件，使用正确的字段名"""
    script_file = 'add_system_prompts.py'
    if not os.path.exists(script_file):
        print(f"错误: 未找到{script_file}文件")
        return False
    
    with open(script_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否需要修改
    if field_name == 'prompt' and 'content=' in content:
        # 从content改为prompt
        content = content.replace('content_text', 'prompt_text')
        content = content.replace('content=', 'prompt=')
        content = content.replace('"content"', '"prompt"')
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已将{script_file}中的content字段修改为prompt")
        return True
    elif field_name == 'content' and 'prompt=' in content:
        # 从prompt改为content
        content = content.replace('prompt_text', 'content_text')
        content = content.replace('prompt=', 'content=')
        content = content.replace('"prompt"', '"content"')
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已将{script_file}中的prompt字段修改为content")
        return True
    
    print(f"{script_file}中的字段名已经正确，无需修改")
    return False

if __name__ == "__main__":
    main() 