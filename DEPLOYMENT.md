# 俯卧撑计数器 Android 应用部署指南

## 📋 概述

本文档详细说明如何将基于 Kivy 的俯卧撑计数器应用打包为 Android APK 文件。

## 🛠️ 环境要求

### 系统要求
- **操作系统**: Ubuntu 18.04+ / macOS 10.14+ / Windows 10+
- **内存**: 至少 8GB RAM（推荐 16GB）
- **存储**: 至少 20GB 可用空间
- **网络**: 稳定的互联网连接（用于下载 SDK）

### 软件依赖

#### 1. Python 环境
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS (使用 Homebrew)
brew install python3

# Windows
# 从 https://python.org 下载并安装 Python 3.8+
```

#### 2. Java 开发环境
```bash
# Ubuntu/Debian
sudo apt install openjdk-8-jdk

# macOS
brew install openjdk@8

# Windows
# 下载并安装 Oracle JDK 8 或 OpenJDK 8
```

#### 3. Android 开发工具（可选）
```bash
# 如果需要手动管理 SDK，可以安装 Android Studio
# Buildozer 会自动下载所需的 SDK 和 NDK
```

#### 4. 系统依赖（Linux）
```bash
# Ubuntu/Debian
sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# 对于 32 位支持
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install -y build-essential ccache git libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 python2.7 python2.7-dev openjdk-8-jdk unzip zlib1g-dev zlib1g:i386
```

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd pushup_counter_mobile
```

### 2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
pip install buildozer
```

### 4. 构建 APK
```bash
# 使用提供的脚本
chmod +x build_apk.sh
./build_apk.sh all

# 或手动执行
buildozer android debug
```

## 📱 详细构建步骤

### 步骤 1: 环境检查
```bash
./build_apk.sh check
```

### 步骤 2: 安装 Python 依赖
```bash
./build_apk.sh deps
```

### 步骤 3: 构建调试版本
```bash
./build_apk.sh debug
```

### 步骤 4: 安装到设备（可选）
```bash
# 确保设备已连接并启用 USB 调试
./build_apk.sh install
```

## 🔧 配置说明

### buildozer.spec 关键配置

#### 应用信息
```ini
title = 俯卧撑计数器
package.name = pushup_counter
package.domain = com.pushup.counter
version = 1.0
```

#### 依赖包
```ini
requirements = python3,kivy==2.1.0,kivymd==1.1.1,opencv-python==4.5.5.64,mediapipe==0.8.11,numpy==1.21.6,pillow==9.5.0,pyjnius==1.4.2,plyer==2.1.0
```

#### Android 权限
```ini
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK
```

#### API 级别
```ini
android.api = 31
android.minapi = 21
android.ndk = 23b
android.ndk_api = 21
```

## 🐛 常见问题解决

### 1. 构建失败：找不到 Java
```bash
# 设置 JAVA_HOME 环境变量
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
echo 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64' >> ~/.bashrc
```

### 2. 构建失败：NDK 下载问题
```bash
# 手动下载 NDK 并设置路径
# 在 buildozer.spec 中设置：
# android.ndk_path = /path/to/android-ndk-r23b
```

### 3. 构建失败：内存不足
```bash
# 增加交换空间（Linux）
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 4. OpenCV 编译问题
```bash
# 如果 OpenCV 编译失败，可以尝试使用预编译版本
# 修改 requirements 为：
# opencv-python-headless==4.5.5.64
```

### 5. MediaPipe 兼容性问题
```bash
# 确保使用兼容的 MediaPipe 版本
# 可能需要降级到 0.8.9 或更早版本
```

## 📋 构建输出

### 成功构建后的文件结构
```
bin/
├── pushup_counter-1.0-armeabi-v7a-debug.apk      # 调试版本
└── pushup_counter-1.0-armeabi-v7a-release.apk    # 发布版本（如果构建）
```

### APK 信息
- **文件大小**: 约 50-80 MB
- **支持架构**: armeabi-v7a, arm64-v8a
- **最低 Android 版本**: Android 5.0 (API 21)
- **目标 Android 版本**: Android 12 (API 31)

## 🔐 发布版本签名

### 1. 生成签名密钥
```bash
keytool -genkey -v -keystore pushup-counter.keystore -alias pushup-counter -keyalg RSA -keysize 2048 -validity 10000
```

### 2. 签名 APK
```bash
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore pushup-counter.keystore bin/pushup_counter-1.0-armeabi-v7a-release-unsigned.apk pushup-counter
```

### 3. 对齐 APK
```bash
zipalign -v 4 bin/pushup_counter-1.0-armeabi-v7a-release-unsigned.apk bin/pushup_counter-1.0-armeabi-v7a-release.apk
```

## 📱 安装和测试

### 1. 通过 ADB 安装
```bash
adb install bin/pushup_counter-1.0-armeabi-v7a-debug.apk
```

### 2. 手动安装
1. 将 APK 文件传输到 Android 设备
2. 在设备上启用"未知来源"安装
3. 点击 APK 文件进行安装

### 3. 测试功能
- [ ] 用户注册和登录
- [ ] 摄像头权限申请
- [ ] 实时俯卧撑检测
- [ ] 视频文件上传处理
- [ ] 数据保存和统计
- [ ] 界面响应和稳定性

## 🔄 持续集成

### GitHub Actions 示例
```yaml
name: Build APK
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: |
        pip install buildozer
        sudo apt update
        sudo apt install -y openjdk-8-jdk
    - name: Build APK
      run: buildozer android debug
    - name: Upload APK
      uses: actions/upload-artifact@v2
      with:
        name: pushup-counter-apk
        path: bin/*.apk
```

## 📞 支持和反馈

如果在构建过程中遇到问题，请：

1. 检查错误日志：`.buildozer/android/platform/build-*/logs/`
2. 查看 Buildozer 文档：https://buildozer.readthedocs.io/
3. 搜索相关问题：https://github.com/kivy/buildozer/issues

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。
