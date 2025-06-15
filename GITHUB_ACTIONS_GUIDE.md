# GitHub Actions APK构建完整指南

## 🎯 概述

本指南将详细说明如何使用GitHub Actions自动构建俯卧撑计数器Android APK。

## 📋 前置条件

1. **GitHub账户**：免费账户即可
2. **公开仓库**：免费用户需要公开仓库才能使用GitHub Actions
3. **项目文件**：确保所有必要文件已准备好

## 🚀 步骤一：创建GitHub仓库

### 1. 访问GitHub
- 打开 https://github.com
- 登录你的GitHub账户

### 2. 创建新仓库
- 点击右上角的 "+" 按钮
- 选择 "New repository"
- 填写仓库信息：
  ```
  Repository name: pushup-counter-mobile
  Description: 俯卧撑计数器移动应用 - 基于Kivy的跨平台应用
  Visibility: Public (重要：免费用户必须选择公开)
  ```
- 不要勾选 "Add a README file"（我们已经有了）
- 点击 "Create repository"

## 📤 步骤二：上传代码

### 方法1：使用提供的脚本（推荐）

```bash
# 在项目目录中运行
./upload_to_github.sh

# 然后按照脚本提示操作
```

### 方法2：手动操作

```bash
# 1. 初始化Git仓库
git init
git branch -M main

# 2. 添加文件
git add .

# 3. 提交
git commit -m "Initial commit: 俯卧撑计数器移动应用"

# 4. 连接远程仓库（替换YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/pushup-counter-mobile.git

# 5. 推送代码
git push -u origin main
```

## 🔧 步骤三：启动GitHub Actions

### 1. 自动触发
代码推送后，GitHub Actions会自动开始构建：
- 访问你的仓库页面
- 点击 "Actions" 标签
- 你会看到 "Build Android APK" 工作流正在运行

### 2. 手动触发
如果需要手动触发构建：
- 在 "Actions" 页面
- 选择 "Build Android APK" 工作流
- 点击 "Run workflow" 按钮
- 选择分支（通常是main）
- 点击 "Run workflow"

## ⏱️ 步骤四：监控构建过程

### 构建阶段说明

1. **Checkout code** (1分钟)
   - 下载项目代码

2. **Set up Python** (1分钟)
   - 安装Python 3.9环境

3. **Install system dependencies** (3-5分钟)
   - 安装Ubuntu系统依赖
   - 包括Java、构建工具等

4. **Setup Android SDK** (5-8分钟)
   - 下载并配置Android SDK
   - 安装NDK和构建工具

5. **Install Python dependencies** (2-3分钟)
   - 安装Buildozer、Kivy等

6. **Build APK with Buildozer** (15-25分钟)
   - 这是最耗时的步骤
   - 下载Android依赖
   - 编译Python代码
   - 生成APK文件

### 查看构建日志
- 点击正在运行的工作流
- 点击 "build" 作业
- 展开各个步骤查看详细日志

## 📦 步骤五：下载APK

### 构建成功后
1. 在Actions页面找到完成的构建
2. 向下滚动到 "Artifacts" 部分
3. 点击 "pushup-counter-debug-apk" 下载
4. 解压下载的zip文件获得APK

### APK文件信息
- 文件名：类似 `pushup_counter-0.1-arm64-v8a-debug.apk`
- 大小：约20-50MB
- 架构：arm64-v8a（支持现代Android设备）

## 🔍 故障排除

### 常见问题

#### 1. 构建失败 - 依赖问题
**症状**：在安装依赖阶段失败
**解决**：
- 检查requirements.txt格式
- 确保buildozer.spec配置正确

#### 2. 构建失败 - 内存不足
**症状**：构建过程中出现内存错误
**解决**：
- GitHub Actions提供7GB内存，通常足够
- 如果仍然失败，可以简化依赖

#### 3. 构建失败 - 网络问题
**症状**：下载Android组件时超时
**解决**：
- 重新运行工作流（通常是临时网络问题）
- GitHub会自动重试

#### 4. 权限问题
**症状**：无法访问Actions
**解决**：
- 确保仓库是公开的
- 检查GitHub账户权限

### 查看详细错误
1. 进入失败的构建
2. 点击红色的X标记
3. 展开失败的步骤
4. 查看错误日志

## 🎛️ 高级配置

### 自定义构建触发条件

编辑 `.github/workflows/build.yml`：

```yaml
on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]  # 标签推送时也构建
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # 每周日构建
```

### 多架构构建

```yaml
strategy:
  matrix:
    arch: [arm64-v8a, armeabi-v7a]
```

### 发布到GitHub Releases

添加发布步骤：

```yaml
- name: Create Release
  if: startsWith(github.ref, 'refs/tags/')
  uses: actions/create-release@v1
  with:
    tag_name: ${{ github.ref }}
    release_name: Release ${{ github.ref }}
    draft: false
    prerelease: false
```

## 📊 构建统计

### 典型构建时间
- **总时间**：15-30分钟
- **缓存命中**：可减少到10-15分钟
- **首次构建**：可能需要35-45分钟

### 资源使用
- **CPU**：2核心
- **内存**：7GB
- **存储**：14GB SSD

## 🔄 持续集成最佳实践

### 1. 版本管理
```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0
```

### 2. 分支策略
- `main`：稳定版本
- `develop`：开发版本
- `feature/*`：功能分支

### 3. 自动化测试
在构建前添加测试步骤：

```yaml
- name: Run tests
  run: |
    python -m pytest tests/
```

## 📞 获取帮助

### 官方文档
- [GitHub Actions文档](https://docs.github.com/en/actions)
- [Buildozer文档](https://buildozer.readthedocs.io/)
- [Kivy文档](https://kivy.org/doc/stable/)

### 社区支持
- GitHub Issues
- Kivy Discord
- Stack Overflow

---

**构建成功后，你就可以在Android设备上安装和测试你的俯卧撑计数器应用了！** 🎉
