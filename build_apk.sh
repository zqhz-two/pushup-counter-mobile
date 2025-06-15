#!/bin/bash

# 俯卧撑计数器 APK 打包脚本
# 使用 Buildozer 将 Kivy 应用打包为 Android APK

echo "=========================================="
echo "俯卧撑计数器 APK 打包脚本"
echo "=========================================="

# 检查是否安装了必要的工具
check_dependencies() {
    echo "检查依赖项..."
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo "错误: 未找到 Python3"
        exit 1
    fi
    
    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        echo "错误: 未找到 pip3"
        exit 1
    fi
    
    # 检查 Java
    if ! command -v java &> /dev/null; then
        echo "错误: 未找到 Java"
        echo "请安装 OpenJDK 8 或更高版本"
        exit 1
    fi
    
    # 检查 Buildozer
    if ! command -v buildozer &> /dev/null; then
        echo "警告: 未找到 Buildozer，正在安装..."
        pip3 install buildozer
    fi
    
    echo "依赖项检查完成"
}

# 安装 Python 依赖
install_python_deps() {
    echo "安装 Python 依赖项..."
    pip3 install -r requirements.txt
    echo "Python 依赖项安装完成"
}

# 初始化 Buildozer
init_buildozer() {
    echo "初始化 Buildozer..."
    
    if [ ! -f "buildozer.spec" ]; then
        echo "错误: 未找到 buildozer.spec 文件"
        exit 1
    fi
    
    # 清理之前的构建
    if [ -d ".buildozer" ]; then
        echo "清理之前的构建文件..."
        rm -rf .buildozer
    fi
    
    echo "Buildozer 初始化完成"
}

# 构建 APK
build_apk() {
    echo "开始构建 APK..."
    echo "注意: 首次构建可能需要很长时间（下载 Android SDK/NDK）"
    
    # 构建调试版本
    buildozer android debug
    
    if [ $? -eq 0 ]; then
        echo "APK 构建成功！"
        echo "APK 文件位置: bin/pushup_counter-1.0-armeabi-v7a-debug.apk"
    else
        echo "APK 构建失败！"
        echo "请检查错误信息并重试"
        exit 1
    fi
}

# 构建发布版本
build_release() {
    echo "构建发布版本..."
    echo "注意: 发布版本需要签名密钥"
    
    buildozer android release
    
    if [ $? -eq 0 ]; then
        echo "发布版本构建成功！"
        echo "APK 文件位置: bin/pushup_counter-1.0-armeabi-v7a-release-unsigned.apk"
        echo "请使用 jarsigner 或 apksigner 对 APK 进行签名"
    else
        echo "发布版本构建失败！"
        exit 1
    fi
}

# 安装到设备
install_apk() {
    echo "安装 APK 到设备..."
    
    # 检查是否有连接的设备
    if ! command -v adb &> /dev/null; then
        echo "错误: 未找到 adb 工具"
        echo "请安装 Android SDK Platform Tools"
        exit 1
    fi
    
    # 检查设备连接
    devices=$(adb devices | grep -v "List of devices" | grep "device$" | wc -l)
    if [ $devices -eq 0 ]; then
        echo "错误: 未找到连接的 Android 设备"
        echo "请确保设备已连接并启用 USB 调试"
        exit 1
    fi
    
    # 安装 APK
    apk_file="bin/pushup_counter-1.0-armeabi-v7a-debug.apk"
    if [ -f "$apk_file" ]; then
        adb install "$apk_file"
        echo "APK 安装完成"
    else
        echo "错误: 未找到 APK 文件: $apk_file"
        echo "请先构建 APK"
        exit 1
    fi
}

# 清理构建文件
clean_build() {
    echo "清理构建文件..."
    rm -rf .buildozer
    rm -rf bin
    echo "清理完成"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  check     检查依赖项"
    echo "  deps      安装 Python 依赖项"
    echo "  debug     构建调试版本 APK"
    echo "  release   构建发布版本 APK"
    echo "  install   安装 APK 到设备"
    echo "  clean     清理构建文件"
    echo "  all       执行完整构建流程（检查依赖 -> 安装依赖 -> 构建调试版本）"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 all        # 完整构建流程"
    echo "  $0 debug      # 只构建调试版本"
    echo "  $0 install    # 安装到设备"
}

# 主函数
main() {
    case "$1" in
        "check")
            check_dependencies
            ;;
        "deps")
            install_python_deps
            ;;
        "debug")
            check_dependencies
            init_buildozer
            build_apk
            ;;
        "release")
            check_dependencies
            init_buildozer
            build_release
            ;;
        "install")
            install_apk
            ;;
        "clean")
            clean_build
            ;;
        "all")
            check_dependencies
            install_python_deps
            init_buildozer
            build_apk
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        "")
            echo "错误: 请指定操作"
            show_help
            exit 1
            ;;
        *)
            echo "错误: 未知选项 '$1'"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
