import os
import subprocess
import sys
import shutil

def check_command(command):
    """检查命令是否存在并可执行"""
    try:
        result = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            shell=True
        )
        return True, result.stdout
    except Exception as e:
        return False, str(e)

def main():
    print("=== LaTeX 检查工具 ===")
    print("检查您的系统中是否正确配置了LaTeX和Manim...\n")
    
    # 检查LaTeX相关命令
    latex_cmds = [
        "latex --version",
        "pdflatex --version",
        "xelatex --version",
        "lualatex --version"
    ]
    
    print("1. 检查LaTeX安装:")
    latex_installed = False
    for cmd in latex_cmds:
        success, output = check_command(cmd)
        cmd_name = cmd.split()[0]
        if success and output:
            print(f"  ✓ {cmd_name} 已安装")
            latex_installed = True
            # 只显示第一行版本信息
            version = output.strip().split('\n')[0]
            print(f"    版本: {version}")
        else:
            print(f"  ✗ {cmd_name} 未安装或无法执行")
    
    if not latex_installed:
        print("\n❌ 未检测到LaTeX安装。请安装TeX Live或MacTeX。")
        print("   推荐命令: brew install --cask mactex")
    else:
        print("\n✓ LaTeX已安装")
    
    # 检查Manim版本
    print("\n2. 检查Manim安装:")
    success, output = check_command("pip show manim")
    if success and "Version:" in output:
        for line in output.strip().split('\n'):
            if line.startswith("Version:"):
                version = line.split("Version:")[1].strip()
                print(f"  ✓ Manim已安装，版本: {version}")
    else:
        print("  ✗ 未检测到Manim安装或无法获取版本信息")
    
    # 检查PATH环境变量
    print("\n3. 检查环境变量:")
    path = os.environ.get('PATH', '')
    tex_paths = [p for p in path.split(os.pathsep) if 'tex' in p.lower()]
    
    if tex_paths:
        print("  ✓ PATH中包含以下TeX相关路径:")
        for p in tex_paths:
            print(f"    - {p}")
    else:
        print("  ✗ PATH中未发现TeX相关路径")
    
    # 尝试创建一个简单的LaTeX文件并编译
    print("\n4. 尝试编译简单的LaTeX文件:")
    test_dir = "latex_test"
    os.makedirs(test_dir, exist_ok=True)
    
    test_file = os.path.join(test_dir, "test.tex")
    with open(test_file, "w") as f:
        f.write(r"""
\documentclass{article}
\begin{document}
Hello, \LaTeX!
\begin{equation}
    e^{i\pi} + 1 = 0
\end{equation}
\end{document}
""")
    
    success, output = check_command(f"cd {test_dir} && pdflatex -interaction=nonstopmode test.tex")
    if success and os.path.exists(os.path.join(test_dir, "test.pdf")):
        print("  ✓ 成功编译LaTeX文档!")
    else:
        print("  ✗ 编译LaTeX文档失败")
        print(f"    错误信息: {output}")
    
    # 最后建议
    print("\n=== 总结 ===")
    if latex_installed:
        print("LaTeX已正确安装，Manim应能正常使用LaTeX渲染数学公式。")
        print("\n为改善Manim与LaTeX的配合，建议:")
        print("1. 确保使用最新版本的Manim (v0.19.0)")
        print("2. 修改Manim配置以使用最佳的LaTeX引擎:")
        print("   - 创建或编辑文件 ~/.manim/manim.cfg")
        print("   - 添加以下内容:")
        print("""
        [TeX]
        tex_compiler = xelatex  # 或 lualatex，它们对Unicode支持更好
        text_to_replace = \\usepackage{amsmath,amssymb,amsthm,mathtools}
        replace_text_with = \\usepackage{amsmath,amssymb,amsthm,mathtools,physics}
        
        [CLI]
        verbosity = INFO  # 更多调试信息
        """)
    else:
        print("需要安装LaTeX才能让Manim正确渲染数学公式。")
        print("推荐使用以下命令安装MacTeX:")
        print("  brew install --cask mactex")
        print("安装后重启终端，确保LaTeX命令在PATH中。")

if __name__ == "__main__":
    main() 