import os
import subprocess
import sys

def run_manim(python_file, scene_name):
    """
    运行Manim命令来生成动画
    
    参数:
    python_file - 包含Manim场景的Python文件
    scene_name - 要渲染的场景名称
    """
    # 检查文件是否存在
    if not os.path.exists(python_file):
        print(f"错误: 文件 {python_file} 不存在")
        return False
        
    # 构建命令 - 使用 -pql 标志 (预览, 质量低)
    cmd = ["manim", "-pql", python_file, scene_name]
    
    # 打印执行的命令
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行命令
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print("命令执行成功!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"发生错误: {e}")
        return False

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) < 3:
        print("用法: python run_manim.py <python文件> <场景名称>")
        print("示例: python run_manim.py manim_example.py SquareToCircleExample")
        sys.exit(1)
    
    # 获取参数
    python_file = sys.argv[1]
    scene_name = sys.argv[2]
    
    # 运行Manim
    success = run_manim(python_file, scene_name)
    
    # 退出状态
    sys.exit(0 if success else 1) 