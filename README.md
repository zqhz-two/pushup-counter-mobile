# 俯卧撑计数器 - 移动应用

基于Kivy框架开发的简单俯卧撑计数应用。

## ✅ 项目完成状态

### 已完成功能
- ✅ 基于Kivy的移动应用界面
- ✅ 俯卧撑计数功能（手动点击）
- ✅ 重置计数功能
- ✅ 移动设备适配
- ✅ Android开发环境配置
- ✅ 应用生命周期管理

### 技术栈
- **Python 3.11+**
- **Kivy 2.3.1**
- **Buildozer**
- **Android SDK/NDK**

## 🚀 快速开始

### 桌面运行

```bash
# 激活虚拟环境
source buildozer_env/bin/activate

# 运行应用
python main.py
```

### Android构建

由于pyjnius兼容性问题，推荐使用以下方法：

#### 方法1：GitHub Actions（推荐）
1. 将代码推送到GitHub
2. 使用提供的`.github/workflows/build.yml`
3. 自动构建APK

#### 方法2：Docker构建
```bash
docker run --rm -v "$PWD":/home/user/hostcwd kivy/buildozer android debug
```

## 📱 应用界面

- **标题**: 俯卧撑计数器
- **计数显示**: 大字体显示当前计数
- **计数按钮**: 点击增加计数
- **重置按钮**: 清零计数

## 🔧 开发环境

项目已配置完整的Android开发环境：
- Java 11 OpenJDK
- Android SDK (API 30)
- Android NDK r25b
- Python虚拟环境
- 所有必要的系统依赖

## 📋 构建配置

`buildozer.spec`已配置：
- 应用名称和版本
- 最小API级别 (21)
- 目标架构 (arm64-v8a)
- 必要权限设置

## ⚠️ 已知问题

1. **pyjnius编译错误**: 当前版本存在兼容性问题
2. **解决方案**: 使用GitHub Actions或Docker进行构建

## 📄 许可证

MIT License
