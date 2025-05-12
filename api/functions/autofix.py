import re

def autofix_manim_code(code):
    """
    自动修复Manim代码中的常见错误
    
    主要修复：
    1. 未定义变量使用问题（特别是title等常见变量）
    2. 替换已弃用的API
    3. 添加必要的导入
    
    返回: (修复后的代码, 修复的问题数量)
    """
    lines = code.split('\n')
    fixed_lines = []
    
    # 收集已定义的变量
    defined_vars = set([
        'self', 'Scene', 'Create', 'FadeIn', 'FadeOut', 'Transform', 
        'Write', 'Wait', 'PI', 'RIGHT', 'LEFT', 'UP', 'DOWN', 'ORIGIN',
        'RED', 'GREEN', 'BLUE', 'YELLOW', 'WHITE', 'BLACK', 'GRAY'
    ])
    
    # 检测类定义并添加到已定义变量
    class_pattern = re.compile(r'class\s+(\w+)')
    for line in lines:
        match = class_pattern.search(line)
        if match:
            defined_vars.add(match.group(1))
    
    # 第一遍：收集变量定义
    var_pattern = re.compile(r'(\w+)\s*=')
    for line in lines:
        if line.strip().startswith('#') or not line.strip():
            continue
            
        for match in var_pattern.finditer(line):
            var_name = match.group(1)
            if var_name not in ('self', 'if', 'elif', 'while', 'for'):
                defined_vars.add(var_name)
    
    # 第二遍：检查变量使用并修复
    issues_fixed = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('#') or not line.strip():
            fixed_lines.append(line)
            continue
            
        # 检查当前行使用的变量
        words = re.findall(r'\b([a-zA-Z_]\w*)\b', line)
        undefined_vars = []
        
        for word in words:
            if (word not in defined_vars and 
                word not in ('if', 'elif', 'else', 'for', 'in', 'while', 'def', 'class', 
                           'return', 'import', 'from', 'as', 'with', 'True', 'False', 'None')):
                undefined_vars.append(word)
                
        if undefined_vars and '=' not in line:  # 避免修复赋值语句左侧
            # 尝试自动修复：为未定义变量添加默认定义
            for var in undefined_vars:
                # 根据变量名猜测可能的类型和默认值
                if var.endswith('_text') or var.endswith('Text'):
                    fix_line = f"{var} = Text('Default Text')"
                elif var.endswith('_circle') or var.endswith('Circle'):
                    fix_line = f"{var} = Circle()"
                elif var.endswith('_arrow') or var.endswith('Arrow'):
                    fix_line = f"{var} = Arrow(ORIGIN, RIGHT)"
                elif var.endswith('_dot') or var.endswith('Dot'):
                    fix_line = f"{var} = Dot()"
                elif var == 'title':
                    fix_line = f"title = Title('Default Title')"
                else:
                    fix_line = f"{var} = 1  # 自动添加的默认值，请修改为正确的值"
                
                # 在未定义变量使用前插入定义
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * indent + fix_line)
                defined_vars.add(var)
                issues_fixed += 1
        
        fixed_lines.append(line)
    
    # 检查并替换已弃用的API
    deprecated_apis = {
        'add_background_rectangle': 'add_background_rectangle()',
        'container_align': 'arrange',
        'get_center_of_mass': 'get_center()',
        'arrange_submobjects': 'arrange',
        'add_points_as_corners': 'set_points_as_corners',
    }
    
    for old_api, new_api in deprecated_apis.items():
        for i, line in enumerate(fixed_lines):
            if old_api in line:
                fixed_lines[i] = line.replace(old_api, new_api)
                issues_fixed += 1
    
    # 确保导入了numpy
    if any('np.' in line for line in fixed_lines) and not any('import numpy as np' in line for line in fixed_lines):
        for i, line in enumerate(fixed_lines):
            if 'import' in line:
                fixed_lines.insert(i+1, 'import numpy as np')
                issues_fixed += 1
                break
        else:
            fixed_lines.insert(0, 'import numpy as np')
            issues_fixed += 1
    
    return '\n'.join(fixed_lines), issues_fixed 