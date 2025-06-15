#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体管理模块
处理字体注册和配置
"""

import os
from kivy.logger import Logger
from kivy.core.text import LabelBase


def register_fonts():
    """注册字体"""
    try:
        # Android系统字体路径
        android_font_paths = [
            '/system/fonts/DroidSansFallback.ttf',
            '/system/fonts/NotoSansCJK-Regular.ttc',
            '/system/fonts/Roboto-Regular.ttf',
            '/system/fonts/DroidSans.ttf'
        ]
        
        # 尝试注册中文字体
        chinese_font_registered = False
        for font_path in android_font_paths:
            if os.path.exists(font_path):
                try:
                    LabelBase.register(name='Chinese', fn_regular=font_path)
                    Logger.info(f"Fonts: Successfully registered Chinese font: {font_path}")
                    chinese_font_registered = True
                    break
                except Exception as e:
                    Logger.warning(f"Fonts: Failed to register font {font_path}: {e}")
                    continue
        
        if not chinese_font_registered:
            Logger.warning("Fonts: No Chinese font found, using default font")
            # 使用默认字体
            LabelBase.register(name='Chinese', fn_regular=None)
        
        # 注册默认字体
        try:
            if os.path.exists('/system/fonts/Roboto-Regular.ttf'):
                LabelBase.register(name='Default', fn_regular='/system/fonts/Roboto-Regular.ttf')
                Logger.info("Fonts: Successfully registered default font")
            else:
                Logger.info("Fonts: Using system default font")
        except Exception as e:
            Logger.warning(f"Fonts: Failed to register default font: {e}")
        
        return True
        
    except Exception as e:
        Logger.error(f"Fonts: Font registration failed: {e}")
        return False


def get_font_name(prefer_chinese=False):
    """获取字体名称"""
    if prefer_chinese and 'Chinese' in LabelBase._fonts:
        return 'Chinese'
    elif 'Default' in LabelBase._fonts:
        return 'Default'
    else:
        return 'Roboto'  # Kivy默认字体


def is_chinese_font_available():
    """检查中文字体是否可用"""
    return 'Chinese' in LabelBase._fonts
