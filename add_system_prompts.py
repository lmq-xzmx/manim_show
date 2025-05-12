#!/usr/bin/env python
"""
脚本用于添加默认系统提示词到数据库
运行方式：
  - 交互式菜单: python add_system_prompts.py
  - 命令行参数: python add_system_prompts.py --mode [1|2]
    - 1: 清除所有提示词并重新添加
    - 2: 保留现有提示词，仅添加新提示词
"""
import os
import django
import argparse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manim_edu.settings')
django.setup()

from api.models import SystemPrompt

def create_system_prompt(name, prompt_text, is_active=False):
    """创建系统提示词，如果已存在同名提示词则跳过"""
    # 检查是否已存在同名提示词
    if SystemPrompt.objects.filter(name=name).exists():
        print(f"提示词 '{name}' 已存在，跳过创建")
        return None
    
    # 创建新的提示词
    prompt = SystemPrompt(
        name=name,
        prompt=prompt_text,
        is_active=is_active
    )
    prompt.save()
    print(f"已添加: {prompt.name}")
    return prompt

def get_default_prompts():
    """获取默认提示词列表"""
    return [
        {
            "name": "默认Manim提示词", 
            "prompt": """你是一个专业的数学动画制作助手，擅长使用Manim库创建数学和教育相关的动画。

请基于用户的请求，生成可执行的Manim代码。代码需要满足以下要求：
1. 遵循PEP 8规范，代码整洁有序
2. 使用注释说明关键步骤和复杂逻辑
3. 使用合适的颜色、动画效果和转场效果使视觉呈现更加生动
4. 确保代码可以独立运行，不依赖于外部资源

请输出完整的Python代码，包括必要的导入语句和Scene类定义。
代码应该是可以直接复制粘贴运行的，不需要用户进行额外修改。

请注意，代码将在Python环境中执行，该环境已安装了manim库。""",
            "is_active": True
        },
        {
            "name": "高级Manim动画提示词", 
            "prompt": """你是一个专业的数学动画制作专家，精通使用Manim库创建复杂、精美的数学和教育相关动画。

请根据用户的要求，生成高质量的Manim代码。代码需要满足以下要求：
1. 使用Manim的高级特性，包括自定义动画、复杂变换和精细控制
2. 代码结构清晰，使用面向对象的方式组织代码
3. 提供详细的注释，解释关键算法和视觉效果的实现方式
4. 使用丰富的色彩、精心设计的布局和流畅的动画转场
5. 优化性能，避免不必要的计算和渲染

请输出完整且可执行的Python代码，包括所有必要的导入语句和类定义。
代码应当遵循最佳实践，易于理解和维护。""",
            "is_active": False
        },
        {
            "name": "原始Manim提示词", 
            "prompt": """你是一个Manim代码生成专家。请将用户的描述转换为可执行的Manim代码。
    
1. 仅返回可执行的Python代码，不要包含任何解释或注释。
2. 使用Manim Community v0.19.0的API。
3. 使用正确的导入: `from manim import *`
4. 使用现代API，例如：
   - 使用 `config.frame_width` 而不是 `FRAME_WIDTH`
   - 使用 `Line.point_from_proportion()` 而不是 `get_point_from_function()`
5. 确保所有动画函数在类内部定义
6. 对于需要LaTeX渲染的内容，使用 MathTex 和 Tex 类
7. 确保所有参数传递正确，每个函数只接受其预期的参数
8. 确保每个动画创建的代码都是完整且可运行的""",
            "is_active": False
        }
    ]

def add_system_prompts_with_clear():
    """清除所有提示词后添加默认提示词"""
    print("==== 模式：清除所有现有提示词并添加默认提示词 ====")
    # 清除所有现有提示词
    print("删除所有现有系统提示词...")
    SystemPrompt.objects.all().delete()
    
    # 添加默认提示词
    print("添加默认系统提示词...")
    for prompt_data in get_default_prompts():
        prompt = SystemPrompt(
            name=prompt_data["name"],
            prompt=prompt_data["prompt"],
            is_active=prompt_data["is_active"]
        )
        prompt.save()
        print(f"已添加: {prompt.name}")

    print("系统提示词添加完成！")

def add_system_prompts_keep_existing():
    """保留现有提示词，仅添加新的提示词"""
    print("==== 模式：保留现有提示词，仅添加新提示词 ====")
    
    # 获取当前是否有活跃提示词
    has_active = SystemPrompt.objects.filter(is_active=True).exists()
    
    # 添加默认提示词，仅当不存在同名提示词时
    print("添加默认系统提示词（如果不存在）...")
    for prompt_data in get_default_prompts():
        # 如果没有活跃提示词且此提示词应该是活跃的
        if not has_active and prompt_data["is_active"]:
            create_system_prompt(
                prompt_data["name"],
                prompt_data["prompt"],
                True  # 设为活跃
            )
        else:
            create_system_prompt(
                prompt_data["name"],
                prompt_data["prompt"],
                False  # 不活跃
            )

    print("系统提示词添加完成！")

def show_menu():
    """显示交互式菜单"""
    print("\n==== Manim教学演示工具 - 系统提示词管理 ====")
    print("请选择操作：")
    print("1. 清除所有提示词并添加默认提示词")
    print("2. 保留现有提示词，仅添加新提示词")
    print("0. 退出")
    choice = input("请输入选项 [0-2]: ")
    return choice

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='添加系统提示词到数据库')
    parser.add_argument('--mode', type=str, choices=['1', '2'], 
                        help='操作模式：1=清除所有并添加默认，2=保留现有并添加新提示词')
    
    args = parser.parse_args()
    
    if args.mode:
        # 命令行模式
        if args.mode == '1':
            add_system_prompts_with_clear()
        elif args.mode == '2':
            add_system_prompts_keep_existing()
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