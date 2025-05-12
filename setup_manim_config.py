#!/usr/bin/env python3
"""
自动设置Manim配置文件，优化对LaTeX的支持
"""

import os
import sys
import shutil
from pathlib import Path

def create_config():
    """创建或更新Manim配置文件"""
    # 确定配置文件路径
    home_dir = Path.home()
    manim_dir = home_dir / ".manim"
    config_file = manim_dir / "manim.cfg"
    
    # 创建目录（如果不存在）
    manim_dir.mkdir(exist_ok=True)
    
    # 配置文件内容
    config_content = """
[CLI]
verbosity = INFO

[TeX]
tex_compiler = xelatex
text_to_replace = \\usepackage{amsmath,amssymb,amsthm,mathtools}
replace_text_with = \\usepackage{amsmath,amssymb,amsthm,mathtools,physics}

[output]
png_quality = 90
preview = True
"""
    
    # 检查是否已存在配置文件
    if config_file.exists():
        backup_file = config_file.with_suffix(".cfg.bak")
        print(f"配置文件已存在，创建备份: {backup_file}")
        shutil.copy2(config_file, backup_file)
    
    # 写入新配置
    with open(config_file, "w") as f:
        f.write(config_content)
    
    print(f"Manim配置文件已创建/更新: {config_file}")
    print("配置已设置为使用XeLaTeX作为TeX编译器，增强对数学符号的支持")

def check_latex_installation():
    """检查LaTeX安装情况"""
    latex_commands = ["latex", "xelatex", "pdflatex"]
    installed = False
    
    for cmd in latex_commands:
        exit_code = os.system(f"which {cmd} > /dev/null 2>&1")
        if exit_code == 0:
            installed = True
            print(f"检测到LaTeX命令: {cmd}")
    
    if not installed:
        print("警告: 未检测到LaTeX安装")
        print("请安装TeX Live或MacTeX:")
        print("  brew install --cask mactex")
        print("或访问: https://www.latex-project.org/get/")
        return False
    
    return True

def create_test_file():
    """创建测试文件验证LaTeX和Manim配置"""
    test_file = "test_manim_latex.py"
    test_content = """from manim import *

class LatexTest(Scene):
    def construct(self):
        # 基础Tex示例
        tex = Tex(r"这是一个测试: $E=mc^2$")
        self.play(Write(tex))
        self.wait()
        
        # MathTex示例
        equation = MathTex(
            r"\\frac{d}{dx}f(x) = \\lim_{h\\to 0}\\frac{f(x+h) - f(x)}{h}"
        )
        self.play(ReplacementTransform(tex, equation))
        self.wait()
        
        # 添加标注
        explanation = Tex("这是导数的定义", font_size=24)
        explanation.next_to(equation, DOWN)
        self.play(FadeIn(explanation))
        self.wait(2)

if __name__ == "__main__":
    print("运行以下命令查看渲染结果:")
    print("  manim -pql test_manim_latex.py LatexTest")
"""
    
    with open(test_file, "w") as f:
        f.write(test_content)
    
    print(f"测试文件已创建: {test_file}")
    print("运行以下命令测试LaTeX渲染:")
    print(f"  manim -pql {test_file} LatexTest")

def main():
    print("===== Manim LaTeX配置工具 =====")
    
    # 检查LaTeX安装
    has_latex = check_latex_installation()
    if not has_latex:
        if input("是否继续创建配置文件？(y/n): ").lower() != 'y':
            print("退出配置")
            return
    
    # 创建配置文件
    create_config()
    
    # 创建测试文件
    create_test_file()
    
    print("\n配置和测试文件设置完成！")
    if has_latex:
        print("您的系统已配置好LaTeX和Manim，可以开始创建包含公式的动画。")

if __name__ == "__main__":
    main() 