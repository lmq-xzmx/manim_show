from django.core.management.base import BaseCommand
from api.models import SystemPrompt

class Command(BaseCommand):
    help = '添加各种物理领域的提示词模板'

    def handle(self, *args, **options):
        # 通用物理模板
        general_prompt = """
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
"""

        # 力学提示词
        mechanics_prompt = """
你是一个专注于力学的Manim动画工程师，负责创建牛顿力学、刚体动力学、碰撞等物理现象的可视化动画。

请生成符合以下要求的力学动画代码：
1. 代码必须遵循"先声明后使用"原则，所有变量在使用前必须定义
2. 正确实现牛顿运动定律（F=ma）和相关物理方程
3. 对于投射体运动，使用参数方程：x = x₀ + v₀cosθ·t, y = y₀ + v₀sinθ·t - ½gt²
4. 对于碰撞，正确处理动量守恒和能量守恒
5. 使用Dot()表示质点，Arrow()表示力向量
6. 使用TracedPath()记录物体运动轨迹
7. 添加坐标系并正确标注位置、速度、加速度等物理量
8. 使用颜色区分不同物体及其受力情况
"""

        # 电磁学提示词
        em_prompt = """
你是一个专注于电磁学的Manim动画工程师，负责创建电场、磁场、电磁波等现象的可视化动画。

请生成符合以下要求的电磁学动画代码：
1. 代码必须遵循"先声明后使用"原则，所有变量在使用前必须定义
2. 正确实现麦克斯韦方程组和相关物理定律
3. 使用StreamLines()或VectorField()可视化电场和磁场
4. 使用Dot()表示电荷，Circle()表示导体横截面
5. 使用Arrow()表示场强向量和洛伦兹力
6. 正确表示电磁场随时间的演化
7. 添加坐标系并标注场强、电势等物理量
8. 使用不同颜色区分正负电荷、电场和磁场
"""

        # 流体力学提示词
        fluid_prompt = """
你是一个专注于流体力学的Manim动画工程师，负责创建流体流动、涡旋、压力分布等现象的可视化动画。

请生成符合以下要求的流体动力学动画代码：
1. 代码必须遵循"先声明后使用"原则，所有变量在使用前必须定义
2. 正确实现纳维-斯托克斯方程和伯努利方程
3. 使用StreamLines()可视化流体流动
4. 使用颜色梯度表示压力或速度分布
5. 对于简单流体，使用粒子系统模拟流体运动
6. 表现流体的层流和湍流特性
7. 添加坐标系并标注速度、压强等物理量
8. 对于边界层现象，使用细致的网格表示边界附近的变化
"""

        # 量子物理提示词
        quantum_prompt = """
你是一个专注于量子物理的Manim动画工程师，负责创建波函数、量子态、量子叠加等现象的可视化动画。

请生成符合以下要求的量子物理动画代码：
1. 代码必须遵循"先声明后使用"原则，所有变量在使用前必须定义
2. 正确表示薛定谔方程和波函数演化
3. 使用ParametricFunction()表示波函数
4. 使用颜色梯度表示波函数的幅度和相位
5. 对于量子态，使用矢量和布洛赫球表示
6. 表现量子叠加、纠缠和干涉现象
7. 添加坐标系并标注能级、概率密度等物理量
8. 使用动画展示量子测量过程中的波函数坍缩
"""
        
        # 相对论提示词
        relativity_prompt = """
你是一个专注于相对论的Manim动画工程师，负责创建时空弯曲、引力透镜、黑洞等现象的可视化动画。

请生成符合以下要求的相对论动画代码：
1. 代码必须遵循"先声明后使用"原则，所有变量在使用前必须定义
2. 正确表示爱因斯坦场方程和广义相对论效应
3. 使用参数曲面表示弯曲的时空
4. 使用光线追踪技术模拟引力透镜效应
5. 对于黑洞，正确表示事件视界和光子球
6. 表现洛伦兹变换和时间膨胀效应
7. 使用四维时空图表示相对论事件
8. 使用颜色梯度表示引力势或时空曲率
"""

        prompts = [
            {
                "name": "通用物理模板",
                "content": general_prompt,
                "category": "general",
                "is_active": True
            },
            {
                "name": "力学专用模板",
                "content": mechanics_prompt,
                "category": "mechanics",
                "is_active": False
            },
            {
                "name": "电磁学专用模板",
                "content": em_prompt,
                "category": "electromagnetism",
                "is_active": False
            },
            {
                "name": "流体力学专用模板",
                "content": fluid_prompt,
                "category": "fluid",
                "is_active": False
            },
            {
                "name": "量子物理专用模板",
                "content": quantum_prompt,
                "category": "quantum",
                "is_active": False
            },
            {
                "name": "相对论专用模板",
                "content": relativity_prompt,
                "category": "relativity",
                "is_active": False
            }
        ]

        # 添加或更新模板
        for prompt_data in prompts:
            prompt, created = SystemPrompt.objects.update_or_create(
                name=prompt_data["name"],
                defaults={
                    "prompt": prompt_data["content"],
                    "category": prompt_data["category"],
                    "is_active": prompt_data["is_active"]
                }
            )
            
            action = "创建" if created else "更新"
            self.stdout.write(self.style.SUCCESS(f'成功{action}提示词模板: {prompt.name}')) 