# Manim教学演示工具

一款专为中小学教师设计的教学辅助工具，支持通过自然语言描述生成数学和科学可视化动画，简化教学演示过程。

## 项目概述

Manim教学演示工具结合了先进的人工智能技术和Manim动画引擎，使教师无需编程知识，仅通过自然语言描述即可生成专业级别的教学动画。本工具旨在提升课堂教学效果，使复杂的数学和科学概念更加直观易懂。

## 功能特性

- **自然语言生成动画**：输入简单的文字描述，生成完整的Manim动画代码
- **Web界面展示**：动画直接在浏览器中呈现，无需额外软件
- **代码透明化**：自动生成的代码可查看和编辑，便于学习和自定义
- **动画管理系统**：保存、分类和重用已生成的动画
- **用户友好界面**：直观的操作流程，专为教育工作者设计

## 技术架构

- **前端**：HTML, CSS, JavaScript, Bootstrap 5
- **后端**：Django (Python)
- **动画引擎**：Manim
- **AI引擎**：大型语言模型（API集成）

## 当前完成功能

- [x] 项目基础架构搭建
- [x] Django应用设计与创建
  - [x] core应用：核心功能
  - [x] api应用：API接口
  - [x] animations应用：动画管理
- [x] 数据模型设计
  - [x] Animation模型
- [x] 基本视图和URL配置
- [x] 前端界面模板
  - [x] 首页（输入自然语言描述）
  - [x] 动画列表页
  - [x] 动画详情页
  - [x] 关于页面
- [x] API基础结构
  - [x] 动画生成接口 

## 待完成功能

- [ ] 集成大型语言模型API
- [ ] 实现Manim代码的安全执行
- [ ] 用户认证和权限管理
- [ ] 动画模板系统
- [ ] 优化移动端体验
- [ ] 性能优化和安全加固
- [ ] 单元测试和集成测试

## 安装指南

1. 克隆项目
```bash
git clone [repository-url]
cd manim-edu
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行数据库迁移
```bash
python manage.py migrate
```

5. 创建超级用户
```bash
python manage.py createsuperuser
```

6. 启动开发服务器
```bash
python manage.py runserver
```

7. 访问项目
```
http://127.0.0.1:8000/
```

## 使用说明

1. 登录系统（或使用超级用户账号）
2. 在首页输入您想要创建的动画的自然语言描述
3. 点击"生成动画"按钮
4. 系统将处理您的请求并生成动画
5. 在"我的动画"页面查看和管理您创建的所有动画
6. 点击具体动画可查看详情、下载或分享

## 集成大模型API指南

我们已经预配置了智谱AI的API接口。您也可以使用其他大模型API，按照以下步骤进行集成：

1. 在项目根目录创建或修改`.env`文件，添加API密钥和端点信息：
```
# 智谱AI配置示例
AI_MODEL_API_KEY=your_api_key_here
AI_MODEL_ENDPOINT=https://open.bigmodel.cn/api/paas/v4/chat/completions

# OpenAI配置示例
# AI_MODEL_API_KEY=sk-your-openai-key-here
# AI_MODEL_ENDPOINT=https://api.openai.com/v1/chat/completions
```

2. 系统会自动基于API端点类型识别并使用正确的请求格式和参数。支持的API类型包括：
   - 智谱AI (GLM-4)
   - OpenAI (GPT-3.5/GPT-4)
   - 其他通用API格式

3. 安全配置：确保`.env`文件已添加到`.gitignore`中，防止API密钥泄露。

4. 重启Django服务器使配置生效：
```bash
python manage.py runserver
```

5. 测试系统：
   - 在首页尝试生成一个简单的动画以测试API连接
   - 查看服务器日志了解API请求和响应详情

## 贡献指南

欢迎贡献代码、报告问题或提出改进建议。请遵循以下步骤：

1. Fork项目
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个Pull Request

## 联系方式

如有任何问题或建议，请联系项目维护者：contact@manim-edu.example.com 