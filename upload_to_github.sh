#!/bin/bash

# 俯卧撑计数器移动应用 - GitHub上传脚本

echo "🚀 准备上传项目到GitHub..."

# 检查是否已经是Git仓库
if [ ! -d ".git" ]; then
    echo "📦 初始化Git仓库..."
    git init
    git branch -M main
else
    echo "✅ Git仓库已存在"
fi

# 添加文件到Git
echo "📁 添加文件到Git..."
git add .

# 提交更改
echo "💾 提交更改..."
git commit -m "Initial commit: 俯卧撑计数器移动应用

- 基于Kivy的跨平台移动应用
- 简单的俯卧撑计数功能
- 完整的Android构建配置
- GitHub Actions自动构建工作流"

echo "
🎯 下一步操作：

1. 在GitHub上创建新仓库：
   - 访问 https://github.com/new
   - 仓库名称：pushup-counter-mobile
   - 描述：俯卧撑计数器移动应用
   - 选择 Public（免费用户需要公开仓库才能使用Actions）

2. 连接到远程仓库（替换YOUR_USERNAME为你的GitHub用户名）：
   git remote add origin https://github.com/YOUR_USERNAME/pushup-counter-mobile.git

3. 推送代码：
   git push -u origin main

4. 在GitHub仓库页面查看Actions构建状态

📋 重要文件说明：
- main.py: 应用主文件
- buildozer.spec: Android构建配置
- .github/workflows/build.yml: GitHub Actions工作流
- requirements.txt: Python依赖
- README.md: 项目说明

🔧 GitHub Actions将自动：
- 安装所有必要的依赖
- 配置Android开发环境
- 构建APK文件
- 上传APK作为构建产物

⏱️ 构建时间：约15-30分钟
📦 输出：pushup-counter-debug-apk.apk
"

echo "✅ Git仓库准备完成！"
