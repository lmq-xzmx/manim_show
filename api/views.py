from django.shortcuts import render, redirect, get_object_or_404
import json
import os
import uuid
import subprocess
import requests
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from animations.models import Animation as AnimationModel
from django.contrib.auth.models import User
import sys
import traceback
import re
import time
import glob
from django.contrib import messages
from .models import SystemPrompt
from manim import (Scene, Circle, Square, Arrow, Dot, 
                  Axes, MathTex, Text, Create, Transform, 
                  FadeIn, FadeOut, TracedPath, Vector)
import numpy as np
from api.functions.autofix import autofix_manim_code

# 加载环境变量
load_dotenv(override=True)  # 强制重新加载环境变量

# Create your views here.

@csrf_exempt
@login_required  # 恢复登录要求
def generate_animation(request):
    """生成动画的API视图"""
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt')
        title = data.get('title', '未命名动画')
        description = data.get('description', '')
        
        if not prompt:
            return JsonResponse({'error': '提示词不能为空'}, status=400)
        
        # 创建动画记录
        animation = AnimationModel.objects.create(
            title=title,
            description=description,
            prompt=prompt,
            status='processing',
            user=request.user
        )
        
        # 调用大模型API生成Manim代码
        manim_code = generate_manim_code_from_llm(prompt, request)
        
        # 保存Manim代码
        animation.manim_code = manim_code
        animation.save()
        
        # 执行Manim代码并生成动画
        output_file = execute_manim_code(manim_code, animation.id)
        
        if output_file:
            animation.output_file = output_file
            animation.status = 'completed'
        else:
            animation.status = 'failed'
        
        animation.save()
        
        return JsonResponse({
            'id': animation.id,
            'status': animation.status,
            'output_url': animation.output_file.url if animation.output_file else None
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def generate_manim_code_from_llm(prompt, request=None):
    """生成专为物理场景优化的Manim代码"""
    # 获取当前活跃的系统提示词
    system_prompt = get_active_system_prompt_content()
    
    # 强化物理场景相关的提示词指导
    physics_prompt = f"""
    请生成一段Manim代码来可视化以下物理场景：
    {prompt}
    
    确保代码：
    1. 使用Manim v0.19.0兼容的API
    2. 先声明所有变量后使用
    3. 使用物理正确的方程和参数
    4. 添加适当的注释和标签
    """
    
    # 调用大模型生成代码...
    # 临时使用示例代码替代真实API调用
    manim_code = generate_sample_manim_code(prompt)
    
    # 使用自动修复工具修复代码中的潜在问题
    fixed_code, issues_fixed = autofix_manim_code(manim_code)
    
    if issues_fixed > 0:
        print(f"自动修复了{issues_fixed}个潜在问题")
    
    return fixed_code

def generate_sample_manim_code(prompt):
    """生成示例Manim代码（在实际项目中将被大模型API替代）"""
    # 这只是一个简单的示例，实际项目中将调用大模型API
    return """
from manim import *

class MathAnimation(Scene):
    def construct(self):
        # 创建标题
        title = Text("数学演示", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        
        # 创建基本形状
        circle = Circle(radius=1.0, color=BLUE)
        square = Square(side_length=2.0, color=GREEN)
        square.next_to(circle, RIGHT, buff=0.5)
        
        # 显示形状
        self.play(Create(circle), Create(square))
        self.wait()
        
        # 添加文字说明
        circle_text = Text("圆形", font_size=24).next_to(circle, DOWN)
        square_text = Text("正方形", font_size=24).next_to(square, DOWN)
        
        self.play(Write(circle_text), Write(square_text))
        self.wait()
        
        # 变换动画
        self.play(circle.animate.set_color(RED), square.animate.set_color(YELLOW))
        self.wait()
        
        # 移动动画
        self.play(circle.animate.shift(LEFT*2), square.animate.shift(RIGHT*2))
        self.wait()
        
        # 淡出
        self.play(
            FadeOut(circle), 
            FadeOut(square),
            FadeOut(circle_text),
            FadeOut(square_text),
            FadeOut(title)
        )
"""

def execute_manim_code(manim_code, animation_id):
    """执行Manim代码，特别优化物理场景的渲染"""
    # 清理和验证代码
    cleaned_code = clean_manim_code(manim_code)
    validation_result = validate_manim_code(cleaned_code)
    
    if validation_result.get("issues"):
        # 修复常见问题
        cleaned_code = fix_common_code_issues(cleaned_code, validation_result["issues"])
    
    # 添加物理场景常用的导入
    if "import numpy as np" not in cleaned_code:
        cleaned_code = "import numpy as np\n" + cleaned_code
    
    # 如果是3D物理场景，确保使用ThreeDScene
    if "3d" in manim_code.lower() or "三维" in manim_code:
        if "ThreeDScene" not in cleaned_code:
            cleaned_code = cleaned_code.replace("Scene):", "ThreeDScene):")
    
    # 执行代码...
    # ...

def clean_manim_code(code):
    """清理和验证Manim代码，确保它可以运行"""
    # 移除代码块标记
    cleaned_code = code
    
    # 如果代码包含markdown代码块，提取其中的代码部分
    if "```python" in code:
        parts = code.split("```python", 1)
        if len(parts) > 1:
            code_part = parts[1]
            if "```" in code_part:
                cleaned_code = code_part.split("```", 1)[0]
            else:
                cleaned_code = code_part
    elif "```" in code:
        parts = code.split("```", 1)
        if len(parts) > 1:
            code_part = parts[1]
            if "```" in code_part:
                cleaned_code = code_part.split("```", 1)[0]
            else:
                cleaned_code = code_part
    
    # 移除空行并计算代码总行数
    non_empty_lines = [line for line in cleaned_code.split('\n') if line.strip()]
    print(f"代码清理后的行数: {len(non_empty_lines)}")
    
    # 基本语法检查和变量验证
    validate_result = validate_manim_code(cleaned_code)
    if not validate_result["valid"]:
        print(f"代码验证警告: {validate_result['message']}")
        cleaned_code = fix_common_code_issues(cleaned_code, validate_result["issues"])
    
    return cleaned_code

def validate_manim_code(code):
    """验证并自动修复Manim代码中的常见问题"""
    lines = code.split('\n')
    fixed_lines = []
    
    # 检测未定义变量、API兼容性问题等
    defined_vars = set()
    potential_issues = []
    fixed_count = 0
    
    # 添加常见的Manim内置对象和方法
    predefined = {'self', 'Scene', 'Create', 'FadeIn', 'FadeOut', 'Transform', 
                 'Write', 'Wait', 'PI', 'RIGHT', 'LEFT', 'UP', 'DOWN', 'ORIGIN',
                 'RED', 'GREEN', 'BLUE', 'YELLOW', 'WHITE', 'BLACK', 'GRAY'}
    defined_vars.update(predefined)
    
    # 检测类定义并添加到预定义变量
    import re
    class_pattern = re.compile(r'class\s+(\w+)\s*\(')
    for line in lines:
        match = class_pattern.search(line)
        if match:
            defined_vars.add(match.group(1))
    
    # 第一遍：收集变量定义
    var_pattern = re.compile(r'(\w+)\s*=')
    for line in lines:
        # 跳过注释和空行
        if line.strip().startswith('#') or not line.strip():
            continue
            
        # 收集变量定义
        for match in var_pattern.finditer(line):
            var_name = match.group(1)
            if var_name not in ('self', 'if', 'elif', 'while', 'for'):
                defined_vars.add(var_name)
    
    # 第二遍：检查变量使用前是否定义
    for i, line in enumerate(lines):
        # 跳过注释和空行
        if line.strip().startswith('#') or not line.strip():
            fixed_lines.append(line)
            continue
            
        # 检查当前行使用的变量
        words = re.findall(r'\b([a-zA-Z_]\w*)\b', line)
        undefined_vars = []
        
        for word in words:
            # 排除Python关键字和常见语法结构
            if (word not in defined_vars and 
                word not in ('self', 'if', 'elif', 'else', 'for', 'in', 'while', 'def', 'class', 
                           'return', 'import', 'from', 'as', 'with', 'True', 'False', 'None')):
                undefined_vars.append(word)
                
        if undefined_vars and '=' not in line:  # 避免修复赋值语句左侧
            potential_issues.append(f"行 {i+1}: 使用了未定义的变量: {', '.join(undefined_vars)}")
            
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
                    fix_line = f"{var} = Title('Default Title')"
                else:
                    fix_line = f"{var} = 1  # 自动添加的默认值，请修改为正确的值"
                
                # 在未定义变量使用前插入定义
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * indent + fix_line)
                defined_vars.add(var)
                fixed_count += 1
        
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
                potential_issues.append(f"行 {i+1}: 替换已弃用API: {old_api} -> {new_api}")
                fixed_count += 1
    
    # 打印验证结果
    print(f"代码清理后的行数: {len(fixed_lines)}")
    if potential_issues:
        print(f"代码验证警告: 发现{len(potential_issues)}个潜在问题")
        #for issue in potential_issues:
        #    print(f"- {issue}")
    
    return '\n'.join(fixed_lines)

def fix_common_code_issues(code, issues):
    """修复常见代码问题"""
    # 检测并修复add_points_smoothly
    if "add_points_smoothly" in code:
        code = code.replace("add_points_smoothly", "add_points_as_corners")
    
    # 检测并修复其他API兼容性问题
    # ...
    
    return code

def _create_fallback_video(animation_id, animations_dir, output_path, full_output_path, error_message="执行失败", error_details=""):
    """创建一个备选的视频文件，当Manim执行失败时使用"""
    try:
        # 使用PIL创建图像
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # 创建一个简单的彩色图像
        width, height = 640, 480
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        # 添加一些暗红色背景以表示错误
        img_array[:, :, 0] = 60  # R通道
        img_array[:, :, 1] = 10  # G通道
        img_array[:, :, 2] = 10  # B通道
        
        # 在中心绘制文字
        img = Image.fromarray(img_array)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("Arial", 30)
            small_font = ImageFont.truetype("Arial", 18)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        # 主要错误信息
        title = f"Manim执行错误 #{animation_id}"
        error_msg = f"{error_message}\n{error_details}"
        note = "请检查代码并重试"
        
        # 处理不同版本PIL的文本尺寸计算
        if hasattr(draw, 'textsize'):
            title_width, title_height = draw.textsize(title, font=font)
            error_width, error_height = draw.textsize(error_msg, font=small_font)
            note_width, note_height = draw.textsize(note, font=small_font)
        else:
            # PIL 9.2.0+使用textbbox或textlength
            try:
                left, top, right, bottom = draw.textbbox((0, 0), title, font=font)
                title_width, title_height = right - left, bottom - top
                
                left, top, right, bottom = draw.textbbox((0, 0), error_msg, font=small_font)
                error_width, error_height = right - left, bottom - top
                
                left, top, right, bottom = draw.textbbox((0, 0), note, font=small_font)
                note_width, note_height = right - left, bottom - top
            except:
                title_width, title_height = 300, 30
                error_width, error_height = 300, 20
                note_width, note_height = 200, 20
        
        # 绘制三行文本
        y_title = height // 2 - 50
        y_error = height // 2
        y_note = height // 2 + 40
        
        draw.text(((width - title_width) // 2, y_title), title, fill=(220, 50, 50), font=font)
        draw.text(((width - error_width) // 2, y_error), error_msg, fill=(255, 200, 200), font=small_font)
        draw.text(((width - note_width) // 2, y_note), note, fill=(200, 200, 200), font=small_font)
        
        # 保存为图像文件
        img_path = os.path.join(animations_dir, f"frame_{animation_id}.png")
        img.save(img_path)
        print(f"已生成备选图像文件: {img_path}")
        
        # 使用ffmpeg生成视频
        try:
            ffmpeg_cmd = [
                'ffmpeg', 
                '-y',                    # 覆盖已有文件
                '-loop', '1',            # 循环图像
                '-i', img_path,          # 输入图像
                '-t', '5',               # 持续5秒
                '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',  # 确保尺寸是偶数
                '-c:v', 'libx264',       # 使用H.264编码
                '-pix_fmt', 'yuv420p',   # 兼容性格式
                '-preset', 'medium',     # 压缩速度
                '-movflags', '+faststart', # Web优化
                full_output_path         # 输出文件
            ]
            
            print(f"执行ffmpeg命令: {' '.join(ffmpeg_cmd)}")
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"ffmpeg成功生成视频: {full_output_path}")
            return output_path
        except Exception as ffmpeg_error:
            print(f"ffmpeg也失败了: {ffmpeg_error}")
            # 如果视频生成失败，使用图像文件作为输出
            return os.path.join('animations', f"frame_{animation_id}.png")
            
    except Exception as e:
        print(f"创建备选视频失败，错误: {str(e)}")
        print(traceback.format_exc())
        return None

# 系统提示词相关视图
@login_required
def system_prompt_list(request):
    """系统提示词列表页面"""
    if not request.user.is_staff:
        messages.error(request, "您没有访问此页面的权限")
        return redirect('core:home')
        
    prompts = SystemPrompt.objects.all().order_by('-is_active', '-updated_at')
    active_prompt = SystemPrompt.get_active()
    
    return render(request, 'api/system_prompt_list.html', {
        'prompts': prompts,
        'active_prompt': active_prompt
    })

@login_required
def add_system_prompt(request):
    """添加系统提示词"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': '权限不足'}, status=403)
        
    if request.method == 'POST':
        name = request.POST.get('name')
        prompt = request.POST.get('prompt')
        is_active = request.POST.get('is_active') == 'true'
        
        if not name or not prompt:
            return JsonResponse({'success': False, 'message': '名称和提示词内容不能为空'}, status=400)
        
        new_prompt = SystemPrompt(
            name=name,
            prompt=prompt,
            is_active=is_active
        )
        new_prompt.save()
        
        return JsonResponse({
            'success': True, 
            'prompt': {
                'id': new_prompt.id,
                'name': new_prompt.name,
                'is_active': new_prompt.is_active,
                'created_at': new_prompt.created_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
    
    return JsonResponse({'success': False, 'message': '不支持此请求方法'}, status=405)

@login_required
def toggle_system_prompt(request, prompt_id):
    """切换系统提示词状态"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': '权限不足'}, status=403)
        
    prompt = get_object_or_404(SystemPrompt, id=prompt_id)
    
    if request.method == 'POST':
        # 设置为活跃状态，会自动将其他提示词设为非活跃
        prompt.is_active = True
        prompt.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'已将"{prompt.name}"设为活跃状态'
        })
    
    return JsonResponse({'success': False, 'message': '不支持此请求方法'}, status=405)

@login_required
def get_active_system_prompt(request):
    """获取当前活跃的系统提示词API视图"""
    active_prompt = SystemPrompt.get_active()
    
    if active_prompt:
        return JsonResponse({
            'success': True,
            'prompt': {
                'id': active_prompt.id,
                'name': active_prompt.name,
                'content': active_prompt.prompt,
                'category': active_prompt.category,
                'updated_at': active_prompt.updated_at.strftime('%Y-%m-%d %H:%M')
            }
        })
    return JsonResponse({
        'success': False,
        'message': '未找到活跃的系统提示词'
    })

def get_active_system_prompt_content():
    """获取当前活跃的系统提示词内容（非API视图）"""
    active_prompt = SystemPrompt.get_active()
    if active_prompt:
        return active_prompt.prompt
    return ""

physics_template = """
你是一个专业的物理Manim动画工程师，负责将用户自然语言描述的物理现象转化为可视化动画。

请生成符合以下严格要求的Manim代码：
1. 代码必须遵循"先声明后使用"原则，所有变量在使用前必须定义
2. 使用符合物理规律的方程（如牛顿运动方程、欧拉方程等）
3. 使用物理正确的参数和单位
4. 为物理量添加适当的标签和单位
5. 使用Manim v0.19.0兼容的API（不使用已弃用方法）
6. 添加坐标系并正确标注物理量
7. 使用TracedPath()记录运动轨迹
8. 动画中使用颜色和形状突出表现关键物理效应

可以应用的物理模型示例：
- 投射运动：结合重力加速度和初速度
- 简谐振动：使用正弦/余弦函数
- 波动传播：使用波动方程
- 电磁场：使用向量场和流线
- 流体动力学：使用粒子系统和矢量场
"""

def get_physics_template(template_name):
    """获取物理场景模板代码"""
    templates = {
        '抛体运动': """
from manim import *

class ProjectileMotion(Scene):
    def construct(self):
        # 参数设置
        g = 9.81  # 重力加速度，单位：m/s²
        v0 = 10   # 初速度，单位：m/s
        theta = PI/4  # 发射角度，45度
        
        # 创建坐标系
        axes = Axes(
            x_range=[0, 15, 1],
            y_range=[0, 10, 1],
            axis_config={"color": BLUE},
            x_axis_config={"numbers_to_include": np.arange(0, 15, 2)},
            y_axis_config={"numbers_to_include": np.arange(0, 10, 2)},
        )
        axes_labels = axes.get_axis_labels(x_label="x (m)", y_label="y (m)")
        
        # 计算抛体轨迹
        def trajectory(t):
            x = v0 * np.cos(theta) * t
            y = v0 * np.sin(theta) * t - 0.5 * g * t**2
            return axes.c2p(x, y)
        
        # 创建轨迹
        path = ParametricFunction(trajectory, t_range=[0, 2*v0*np.sin(theta)/g, 0.01], color=YELLOW)
        
        # 添加物体
        ball = Dot(axes.c2p(0, 0), color=RED)
        velocity_arrow = Arrow(start=axes.c2p(0, 0), end=axes.c2p(v0*np.cos(theta), v0*np.sin(theta)), color=GREEN, buff=0)
        velocity_label = MathTex("\\vec{v}_0", color=GREEN).next_to(velocity_arrow, UP)
        
        # 添加标题
        title = Title("抛体运动", color=WHITE)
        
        # 显示场景
        self.add(title, axes, axes_labels)
        self.play(Create(path), run_time=2)
        self.play(FadeIn(ball), Create(velocity_arrow), Write(velocity_label))
        
        # 物体沿轨迹运动
        self.play(MoveAlongPath(ball, path), rate_func=linear, run_time=3)
        
        # 轨迹标签
        formula = MathTex(
            "y = y_0 + v_0\\sin\\theta\\cdot t - \\frac{1}{2}gt^2",
            font_size=36
        ).to_edge(DOWN)
        self.play(Write(formula))
        
        self.wait(1)
""",
        '简谐振动': """
from manim import *

class SimpleHarmonicMotion(Scene):
    def construct(self):
        # 参数设置
        amplitude = 2  # 振幅
        k = 1.5        # 弹性系数
        m = 1.0        # 质量
        
        # 创建坐标系
        axes = Axes(
            x_range=[-0.5, 4.5, 1],
            y_range=[-3, 3, 1],
            axis_config={"color": BLUE},
        )
        axes_labels = axes.get_axis_labels(x_label="t (s)", y_label="x (m)")
        
        # 创建弹簧和质量
        spring_start = axes.c2p(0, 0)
        mass = Circle(radius=0.3, color=RED, fill_opacity=0.8)
        
        # 定义简谐运动公式
        def oscillation(t):
            omega = np.sqrt(k/m)
            return axes.c2p(t, amplitude * np.cos(omega * t))
        
        # 创建运动轨迹
        path = ParametricFunction(
            lambda t: axes.c2p(t, amplitude * np.cos(np.sqrt(k/m) * t)),
            t_range=[0, 4, 0.01],
            color=YELLOW
        )
        
        # 创建弹簧
        def get_spring(x):
            return Line(spring_start, axes.c2p(0, x), color=BLUE)
        
        # 添加标题
        title = Title("简谐振动", color=WHITE)
        
        # 显示场景
        self.add(title, axes, axes_labels)
        self.play(Create(path), run_time=2)
        
        # 初始化弹簧和质量位置
        spring = get_spring(amplitude)
        mass.move_to(axes.c2p(0, amplitude))
        
        self.play(Create(spring), FadeIn(mass))
        
        # 质量运动动画
        def update_mass(mob, dt):
            t = self.renderer.time
            omega = np.sqrt(k/m)
            x = amplitude * np.cos(omega * t)
            mob.move_to(axes.c2p(0, x))
            
        def update_spring(mob, dt):
            t = self.renderer.time
            omega = np.sqrt(k/m)
            x = amplitude * np.cos(omega * t)
            mob.become(get_spring(x))
        
        # 轨迹指示点
        dot = Dot(color=RED)
        def update_dot(mob, dt):
            t = self.renderer.time
            mob.move_to(oscillation(t))
        
        # 添加公式
        formula = MathTex(
            "x = A\\cos(\\omega t), \\omega = \\sqrt{\\frac{k}{m}}",
            font_size=36
        ).to_edge(DOWN)
        
        self.play(Write(formula))
        
        # 运动动画
        mass.add_updater(update_mass)
        spring.add_updater(update_spring)
        dot.add_updater(update_dot)
        self.add(dot)
        
        self.wait(4)
        
        # 移除更新器
        mass.remove_updater(update_mass)
        spring.remove_updater(update_spring)
        dot.remove_updater(update_dot)
        
        self.wait(1)
""",
        # 其他模板...
    }
    
    return templates.get(template_name, "")

# 根据物理场景类型自动选择最佳的渲染参数
def get_optimal_render_settings(physics_type):
    settings = {
        "default": ["-ql"],  # 低质量，快速预览
        "mechanics": ["-qh", "--fps", "60"],  # 高质量，高帧率，适合力学仿真
        "electromagnetism": ["-qm", "--fps", "30"],  # 中等质量，适合电磁场可视化
        "fluid": ["-qk", "--fps", "60", "--background_opacity", "0.3"],  # 4K，高帧率，透明背景
        "quantum": ["-qh", "--fps", "30", "--background_color", "BLACK"],  # 高质量，黑色背景
    }
    
    return settings.get(physics_type, settings["default"])

@login_required
def get_prompts_by_category(request, category):
    """根据类别获取系统提示词列表"""
    prompts = SystemPrompt.get_by_category(category)
    
    return JsonResponse({
        'success': True,
        'category': category,
        'prompts': [
            {
                'id': prompt.id,
                'name': prompt.name,
                'content': prompt.prompt,
                'is_active': prompt.is_active,
                'category': prompt.category,
                'updated_at': prompt.updated_at.strftime('%Y-%m-%d %H:%M')
            }
            for prompt in prompts
        ]
    })

@login_required
def get_physics_template_api(request, template_name):
    """API端点：获取物理场景模板代码"""
    template_code = get_physics_template(template_name)
    
    if not template_code:
        return JsonResponse({
            'success': False,
            'message': f'未找到模板: {template_name}'
        })
    
    return JsonResponse({
        'success': True,
        'template': {
            'name': template_name,
            'code': template_code
        }
    })
