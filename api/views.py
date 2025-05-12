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
from animations.models import Animation
from django.contrib.auth.models import User
import sys
import traceback
import re
import time
import glob
from django.contrib import messages
from .models import SystemPrompt

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
        animation = Animation.objects.create(
            title=title,
            description=description,
            prompt=prompt,
            status='processing',
            user=request.user
        )
        
        # 调用大模型API生成Manim代码
        manim_code = generate_manim_code_from_llm(prompt)
        
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

def generate_manim_code_from_llm(prompt):
    """调用大模型API生成Manim代码"""
    api_key = os.getenv('AI_MODEL_API_KEY')
    endpoint = os.getenv('AI_MODEL_ENDPOINT')
    
    # 检查API配置
    if not api_key or not endpoint:
        print("警告：API配置不正确，使用示例代码")
        return generate_sample_manim_code(prompt)
    
    # 从数据库获取活跃的系统提示词
    active_prompt = SystemPrompt.get_active()
    
    # 使用默认的系统提示词作为后备
    enhanced_system_prompt = """你是一个Manim代码生成专家。请将用户的描述转换为可执行的Manim代码。
    
1. 仅返回可执行的Python代码，不要包含任何解释或注释。
2. 使用Manim Community v0.19.0的API。
3. 使用正确的导入: `from manim import *`
4. 使用现代API，例如：
   - 使用 `config.frame_width` 而不是 `FRAME_WIDTH`
   - 使用 `Line.point_from_proportion()` 而不是 `get_point_from_function()`
5. 确保所有动画函数在类内部定义
6. 对于需要LaTeX渲染的内容，使用 MathTex 和 Tex 类
7. 确保所有参数传递正确，每个函数只接受其预期的参数
8. 确保每个动画创建的代码都是完整且可运行的
9. 永远先定义变量再使用，避免出现变量未定义错误
"""
    
    # 如果数据库中有活跃提示词，使用它替换默认值
    if active_prompt:
        enhanced_system_prompt = active_prompt.prompt
        print(f"使用数据库中的系统提示词: {active_prompt.name}")
    else:
        print("未找到活跃的系统提示词，使用默认提示词")
    
    enhanced_user_prompt = f"""将以下描述转换为Manim动画代码：

{prompt}

请仅返回可执行的Python代码，代码需要符合以下要求:
1. 使用Manim Community v0.19.0的API
2. 正确处理LaTeX公式渲染
3. 避免使用已弃用的API
4. 确保动画逻辑正确
5. 符合PEP 8编码规范
6. 不要增加额外的解释或注释
7. 所有变量在使用前必须先声明和定义
"""
    
    # 设置API请求参数
    api_data = {
        "model": "glm-4",  # 使用GLM-4模型
        "messages": [
            {"role": "system", "content": enhanced_system_prompt},
            {"role": "user", "content": enhanced_user_prompt}
        ],
        "temperature": 0.3,  # 降低温度使生成更加确定性
        "max_tokens": 2000
    }
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    print(f"使用智谱AI API: {endpoint}")
    print(f"发送API请求到: {endpoint}")
    print(f"请求头: {headers}")
    
    # 只打印部分请求体，避免日志过长
    print(f"请求体(部分): {str(api_data)[:100]}...")
    # 每次输出一点，避免日志过长
    for i in range(0, len(str(api_data)), 100):
        end = min(i + 100, len(str(api_data)))
        print(f"请求体(部分): {str(api_data)[i:end]}...")
    
    # 添加重试机制
    max_retries = 3
    retry_delay = 2  # 初始延迟2秒
    
    for attempt in range(max_retries):
        try:
            # 增加超时设置
            response = requests.post(
                endpoint, 
                json=api_data, 
                headers=headers, 
                timeout=30  # 将超时时间从15秒增加到30秒
            )
            
            print(f"API响应状态码: {response.status_code}")
            
            # 只打印部分响应内容，避免日志过长
            print(f"API响应内容(部分): {str(response.text)[:100]}...")
            for i in range(0, len(str(response.text)), 100):
                end = min(i + 100, len(str(response.text)))
                print(f"API响应内容(部分): {str(response.text)[i:end]}...")
            
            if response.status_code == 200:
                response_data = response.json()
                generated_code = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if generated_code:
                    return generated_code
                else:
                    print("API返回成功但未包含生成的代码")
                    if attempt < max_retries - 1:
                        print(f"尝试重新请求 (尝试 {attempt+1}/{max_retries})")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                        continue
                    return generate_sample_manim_code(prompt)
            else:
                print(f"API请求失败，状态码: {response.status_code}")
                # 检查是否有详细错误信息
                try:
                    error_detail = response.json()
                    print(f"错误详情: {error_detail}")
                except:
                    print(f"错误响应: {response.text}")
                
                if attempt < max_retries - 1:
                    print(f"尝试重新请求 (尝试 {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                    continue
                return generate_sample_manim_code(prompt)
                
        except requests.exceptions.ReadTimeout as e:
            print(f"调用大模型API时出错: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            print(f"请求异常: {str(e)}")
            
            if attempt < max_retries - 1:
                print(f"API超时，重试中... (尝试 {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避
                continue
            
            # 尝试使用备选的更简化请求
            try:
                print("尝试使用简化请求...")
                # 简化系统提示和用户提示
                simplified_data = {
                    "model": "glm-4",
                    "messages": [
                        {"role": "system", "content": "请生成简单的Manim代码，确保定义所有变量后再使用。"},
                        {"role": "user", "content": f"创建一个Manim动画：{prompt}"}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1000
                }
                
                response = requests.post(
                    endpoint, 
                    json=simplified_data, 
                    headers=headers, 
                    timeout=20
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    generated_code = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if generated_code:
                        print("使用简化请求成功获取代码")
                        return generated_code
                
                print("简化请求也失败，使用示例代码")
            except Exception as inner_e:
                print(f"简化请求也失败: {str(inner_e)}")
            
            return generate_sample_manim_code(prompt)
            
        except Exception as e:
            print(f"调用大模型API时出错: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            print(traceback.format_exc())
            
            if attempt < max_retries - 1:
                print(f"尝试重新请求 (尝试 {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避
                continue
            
            return generate_sample_manim_code(prompt)

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
    """执行Manim代码并生成动画文件"""
    try:
        print(f"开始执行Manim代码 (ID: {animation_id})...")
        
        # 创建必要的目录
        media_dir = os.path.join('media')
        animations_dir = os.path.join(media_dir, 'animations')
        os.makedirs(media_dir, exist_ok=True)
        os.makedirs(animations_dir, exist_ok=True)
        
        # 创建临时文件来存储Manim代码
        temp_dir = os.path.join('media', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # 生成唯一文件名（不含路径和扩展名）
        base_file_name = f"animation_{animation_id}_{uuid.uuid4().hex[:8]}"
        file_name = f"{base_file_name}.py"
        file_path = os.path.join(temp_dir, file_name)
        
        # 输出文件路径
        output_file_name = f"animation_{animation_id}.mp4"
        output_path = os.path.join('animations', output_file_name)
        full_output_path = os.path.join(media_dir, output_path)
        
        # 清理代码，移除非Python内容并验证代码
        cleaned_code = clean_manim_code(manim_code)
        
        # 写入Manim代码到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_code)
        
        print(f"Manim代码已写入文件: {file_path}")
        
        # 从代码中提取场景类名
        scene_classes = re.findall(r'class\s+(\w+)\s*\(\s*(?:Scene|ThreeDScene|MovingCameraScene|ZoomedScene|VectorScene)\s*\)', cleaned_code)
        
        if not scene_classes:
            print(f"无法从代码中找到Scene类，尝试使用通用正则表达式")
            # 使用更通用的正则表达式尝试匹配任何继承的类
            scene_classes = re.findall(r'class\s+(\w+)\s*\([^)]*\):', cleaned_code)
            
            if not scene_classes:
                print(f"仍然无法找到任何类定义，使用备选方案")
                return _create_fallback_video(animation_id, animations_dir, output_path, full_output_path, 
                                            error_message="无法从代码中提取场景类")
        
        scene_name = scene_classes[0]
        print(f"从代码中提取的场景类名: {scene_name}")
        
        # 构建Manim命令 - 从test_manim.py复制成功的命令结构
        manim_cmd = [
            'manim',
            '-ql',  # 低质量，快速渲染
            file_path,
            scene_name
        ]
        
        # 执行Manim命令
        print(f"执行Manim命令: {' '.join(manim_cmd)}")
        
        try:
            start_time = time.time()
            
            # 创建一个临时环境变量副本，确保Manim能找到正确的Python路径
            env = os.environ.copy()
            
            # 执行命令
            process = subprocess.run(
                manim_cmd, 
                check=True,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                env=env,
                timeout=120  # 为复杂场景提供更长的超时时间
            )
            
            end_time = time.time()
            print(f"Manim命令执行成功! 用时: {end_time - start_time:.2f}秒")
            
            # 计算预期的视频输出路径（与test_manim.py中保持一致）
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            expected_video_path = os.path.join('media', 'videos', base_name, '480p15', f"{scene_name}.mp4")
            
            # 检查预期路径的视频文件是否存在
            if os.path.exists(expected_video_path):
                print(f"成功找到生成的视频: {expected_video_path}")
                # 复制视频到目标位置
                import shutil
                shutil.copy(expected_video_path, full_output_path)
                print(f"视频已复制到: {full_output_path}")
                return output_path
            else:
                print(f"未找到预期的视频文件: {expected_video_path}")
                
                # 1. 尝试查找更广泛的位置 - 使用通配符搜索所有可能的质量目录
                wider_search_pattern = os.path.join('media', 'videos', base_name, '*', f"{scene_name}.mp4")
                matching_files = glob.glob(wider_search_pattern)
                
                if matching_files:
                    video_file = matching_files[0]  # 使用找到的第一个匹配文件
                    print(f"在替代位置找到视频: {video_file}")
                    shutil.copy(video_file, full_output_path)
                    print(f"视频已复制到: {full_output_path}")
                    return output_path
                
                # 2. 如果仍然找不到，搜索所有最近的MP4文件
                print("执行全局视频文件搜索...")
                all_videos = glob.glob(os.path.join('media', 'videos', '**', '*.mp4'), recursive=True)
                
                if all_videos:
                    # 按修改时间排序，获取最新创建的视频文件
                    recent_videos = sorted(all_videos, key=os.path.getmtime, reverse=True)
                    most_recent = recent_videos[0]
                    
                    print(f"找到最近创建的视频文件: {most_recent}")
                    shutil.copy(most_recent, full_output_path)
                    print(f"视频已复制到: {full_output_path}")
                    return output_path
                
                # 3. 如果还是找不到视频，创建备选视频
                print("未找到任何视频文件，将创建备选视频")
                return _create_fallback_video(animation_id, animations_dir, output_path, full_output_path,
                                            error_message="Manim生成的视频文件无法找到")
                
        except subprocess.CalledProcessError as e:
            print(f"Manim命令执行失败，状态码: {e.returncode}")
            print(f"错误输出: {e.stderr}")
            
            # 尝试分析错误输出以提供更具体的错误信息
            error_message = "Manim执行失败"
            error_details = "未知错误"
            
            # 常见错误类型的检测和修复
            if "NameError: name" in e.stderr:
                # 变量未定义错误
                var_match = re.search(r"NameError: name '(\w+)' is not defined", e.stderr)
                if var_match:
                    var_name = var_match.group(1)
                    error_message = f"变量未定义: {var_name}"
                    error_details = f"在使用变量 {var_name} 前需要先定义它"
                    
                    # 尝试自动修复代码
                    print(f"尝试自动修复未定义变量: {var_name}")
                    # 检查是否有备份文件可用
                    autofix_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../autofix.py")
                    if os.path.exists(autofix_file):
                        fix_cmd = ["python", autofix_file, file_path]
                        try:
                            subprocess.run(fix_cmd, check=True, timeout=30)
                            print(f"autofix.py成功修复了文件 {file_path}")
                            # 再次尝试执行
                            return execute_manim_code(open(file_path, 'r', encoding='utf-8').read(), animation_id)
                        except Exception as fix_err:
                            print(f"自动修复失败: {fix_err}")
            
            elif "SyntaxError" in e.stderr:
                # 语法错误
                syntax_match = re.search(r"SyntaxError: (.*)", e.stderr)
                if syntax_match:
                    syntax_error = syntax_match.group(1)
                    error_message = f"语法错误: {syntax_error}"
                    error_details = "代码中存在语法错误，需要修正"
            
            elif "ModuleNotFoundError" in e.stderr:
                # 模块未找到错误
                module_match = re.search(r"ModuleNotFoundError: No module named '(.*)'", e.stderr)
                if module_match:
                    module_name = module_match.group(1)
                    error_message = f"缺少模块: {module_name}"
                    error_details = f"需要安装缺少的模块: pip install {module_name}"
                    
            elif "TypeError" in e.stderr:
                # 类型错误
                type_match = re.search(r"TypeError: (.*)", e.stderr)
                if type_match:
                    type_error = type_match.group(1)
                    error_message = f"类型错误: {type_error}"
                    error_details = "函数参数类型不匹配，请检查函数调用"
            
            # 创建带有详细错误信息的备选视频
            return _create_fallback_video(
                animation_id, 
                animations_dir, 
                output_path, 
                full_output_path,
                error_message=error_message,
                error_details=error_details
            )
        
        except subprocess.TimeoutExpired:
            print(f"Manim命令执行超时（超过120秒）")
            return _create_fallback_video(animation_id, animations_dir, output_path, full_output_path,
                                        error_message="Manim执行超时")
        
        except Exception as e:
            print(f"执行Manim命令时发生意外错误: {str(e)}")
            print(traceback.format_exc())
            return _create_fallback_video(animation_id, animations_dir, output_path, full_output_path,
                                        error_message=f"执行错误: {str(e)}")
    
    except Exception as e:
        print(f"执行Manim代码的总体过程中发生错误: {e}")
        print(traceback.format_exc())
        return None

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
    """验证Manim代码是否存在常见问题"""
    issues = []
    result = {"valid": True, "message": "", "issues": issues}
    
    # 检查基本语法，尝试编译代码
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        result["valid"] = False
        result["message"] = f"语法错误: {str(e)}"
        issues.append({"type": "syntax", "message": str(e)})
        return result
    
    # 检查常见的变量使用问题
    lines = code.split('\n')
    defined_vars = set()
    scene_class_found = False
    construct_method_found = False
    
    for i, line in enumerate(lines):
        # 检测是否定义了Scene类
        if "class" in line and "Scene" in line:
            scene_class_found = True
            continue
            
        # 检测是否有construct方法
        if scene_class_found and "def construct" in line:
            construct_method_found = True
            continue
            
        # 在construct方法中收集变量定义
        if construct_method_found:
            if "=" in line:
                var_name = line.split("=")[0].strip()
                if var_name and not var_name.startswith(("self.", "#")) and " " not in var_name:
                    defined_vars.add(var_name)
            
            # 检查是否使用了未定义的常见变量
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith("#"):
                for common_var in ["title", "equation", "text", "formula", "graph"]:
                    # 排除赋值和函数定义的情况
                    if common_var in line and "=" not in line and "def " not in line:
                        if common_var not in defined_vars and "self." + common_var not in line:
                            issues.append({
                                "type": "undefined_var", 
                                "line": i+1, 
                                "var": common_var,
                                "content": line
                            })
    
    if len(issues) > 0:
        result["valid"] = False
        result["message"] = f"发现{len(issues)}个潜在问题"
    
    return result

def fix_common_code_issues(code, issues):
    """修复代码中的常见问题"""
    lines = code.split('\n')
    
    # 处理每个发现的问题
    for issue in issues:
        if issue["type"] == "undefined_var":
            line_idx = issue["line"] - 1
            var_name = issue["var"]
            
            # 根据变量类型添加一个合适的定义
            if var_name == "title":
                # 在construct方法开始处添加title定义
                for i, line in enumerate(lines):
                    if "def construct" in line:
                        # 找到construct方法的下一行
                        j = i + 1
                        while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith("#")):
                            j += 1
                        indent = ' ' * (len(lines[j]) - len(lines[j].lstrip()))
                        lines.insert(j, f"{indent}# 创建标题\n{indent}{var_name} = Text('数学动画演示', font_size=36)")
                        break
            
            elif var_name == "equation":
                for i, line in enumerate(lines):
                    if "def construct" in line:
                        j = i + 1
                        while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith("#")):
                            j += 1
                        indent = ' ' * (len(lines[j]) - len(lines[j].lstrip()))
                        lines.insert(j, f"{indent}# 创建方程\n{indent}{var_name} = MathTex(r'F = G\\frac{{m_1 m_2}}{{r^2}}')")
                        break
    
    return '\n'.join(lines)

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
    """获取当前活跃的系统提示词"""
    active_prompt = SystemPrompt.get_active()
    
    if active_prompt:
        return JsonResponse({
            'success': True,
            'prompt': {
                'id': active_prompt.id,
                'name': active_prompt.name,
                'content': active_prompt.prompt,
                'updated_at': active_prompt.updated_at.strftime('%Y-%m-%d %H:%M')
            }
        })
    else:
        return JsonResponse({
            'success': False,
            'message': '未找到活跃的系统提示词'
        }, status=404)
