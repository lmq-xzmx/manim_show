#!/usr/bin/env python3
"""
设置Manim配置文件，避免使用LaTeX
"""

import os
from pathlib import Path

def create_config():
    """创建Manim配置文件，禁用LaTeX渲染"""
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
text_to_replace = \\usepackage{amsmath,amssymb}
replace_text_with = \\usepackage{amsmath,amssymb,physics}

# 下面是关键设置 - 使用png避免dvisvgm
output_format = png
use_ctex = False

[output]
png_quality = 90
preview = True
"""
    
    # 写入新配置
    with open(config_file, "w") as f:
        f.write(config_content)
    
    print(f"Manim配置文件已创建/更新: {config_file}")
    print("已配置为使用PNG渲染，避免dvisvgm问题")

if __name__ == "__main__":
    print("===== Manim 无LaTeX配置工具 =====")
    create_config()
    print("\n配置完成！")
    print("现在Manim将避免使用需要dvisvgm的LaTeX渲染路径。")
    print("重启应用后生效。") 