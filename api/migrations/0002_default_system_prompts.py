from django.db import migrations

def create_default_system_prompts(apps, schema_editor):
    """创建默认系统提示词"""
    SystemPrompt = apps.get_model('api', 'SystemPrompt')
    
    # 如果没有任何系统提示词，创建默认系统提示词
    if SystemPrompt.objects.count() == 0:
        default_prompt = SystemPrompt(
            name="默认Manim提示词", 
            prompt="""你是一个专业的数学动画制作助手，擅长使用Manim库创建数学和教育相关的动画。

请基于用户的请求，生成可执行的Manim代码。代码需要满足以下要求：
1. 遵循PEP 8规范，代码整洁有序
2. 使用注释说明关键步骤和复杂逻辑
3. 使用合适的颜色、动画效果和转场效果使视觉呈现更加生动
4. 确保代码可以独立运行，不依赖于外部资源

请输出完整的Python代码，包括必要的导入语句和Scene类定义。
代码应该是可以直接复制粘贴运行的，不需要用户进行额外修改。

请注意，代码将在Python环境中执行，该环境已安装了manim库。""",
            is_active=True
        )
        default_prompt.save()
        
        # 添加一个额外的提示词模板
        advanced_prompt = SystemPrompt(
            name="高级Manim动画提示词", 
            prompt="""你是一个专业的数学动画制作专家，精通使用Manim库创建复杂、精美的数学和教育相关动画。

请根据用户的要求，生成高质量的Manim代码。代码需要满足以下要求：
1. 使用Manim的高级特性，包括自定义动画、复杂变换和精细控制
2. 代码结构清晰，使用面向对象的方式组织代码
3. 提供详细的注释，解释关键算法和视觉效果的实现方式
4. 使用丰富的色彩、精心设计的布局和流畅的动画转场
5. 优化性能，避免不必要的计算和渲染

请输出完整且可执行的Python代码，包括所有必要的导入语句和类定义。
代码应当遵循最佳实践，易于理解和维护。""",
            is_active=False
        )
        advanced_prompt.save()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_system_prompts),
    ] 