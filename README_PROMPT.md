# 系统提示词管理

本文档介绍如何管理Manim教学演示工具的系统提示词。系统提示词用于指导AI生成Manim代码，影响生成代码的风格和质量。

## 可用的提示词模板

系统默认提供三种提示词模板：

1. **默认Manim提示词** - 提供全面的Manim代码生成指导，包含注释和清晰的代码结构
2. **高级Manim动画提示词** - 提供更复杂、精美的动画生成指导，使用高级特性
3. **原始Manim提示词** - 简洁的代码生成指导，专注于生成无注释的纯代码

## 管理提示词的方法

### 1. 使用Web界面管理

可以通过以下两个界面管理系统提示词：

- **Django管理界面**: http://127.0.0.1:8000/admin/api/systemprompt/
- **自定义管理界面**: http://127.0.0.1:8000/api/system-prompts/

这两个界面都支持查看、添加、编辑和删除系统提示词。

### 2. 使用命令行工具管理

#### 使用Python脚本(推荐)

使用`manage_prompts.py`脚本可以最简单地管理系统提示词：

```bash
# 清除所有提示词并添加默认提示词
python manage_prompts.py 1

# 保留现有提示词，仅添加缺失的默认提示词
python manage_prompts.py 2

# 启动交互式菜单
python manage_prompts.py
```

#### 使用Shell脚本

也可以使用Shell脚本进行管理：

```bash
# 清除所有提示词并添加默认提示词
./manage_prompts.sh 1

# 保留现有提示词，仅添加缺失的默认提示词
./manage_prompts.sh 2

# 启动交互式菜单
./manage_prompts.sh
```

#### 或直接使用原始Python脚本

也可以直接运行原始Python脚本：

```bash
# 启动交互式菜单
python add_system_prompts.py

# 使用命令行参数
python add_system_prompts.py --mode 1  # 清除并添加默认提示词
python add_system_prompts.py --mode 2  # 保留并添加新提示词
```

## 切换当前使用的提示词

在任何一个管理界面，都可以设置某个提示词为"活跃"状态，系统会使用当前活跃的提示词来生成代码。

每次只能有一个提示词处于活跃状态，设置一个提示词为活跃会自动将其他提示词设为非活跃。 