#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复后的俯卧撑计数应用测试版本
用于验证字体、摄像头和视频上传功能
"""

import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.progressbar import ProgressBar
from kivy.logger import Logger
from kivy.config import Config
from kivy.clock import Clock

# 配置Kivy
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)

# 导入字体管理
try:
    from assets.fonts import register_fonts, get_font_name
    register_fonts()
except ImportError:
    Logger.warning("TestApp: Font management not available")
    get_font_name = lambda: 'Roboto'

# 导入权限管理
try:
    from utils.permissions import request_permissions
except ImportError:
    Logger.warning("TestApp: Permission management not available")
    request_permissions = lambda: True


class TestPushupApp(App):
    """测试版俯卧撑计数应用"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.count = 0
        self.camera = None
    
    def build(self):
        """构建应用界面"""
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        title = Label(
            text='Pushup Counter - Fixed Version',
            font_size='20sp',
            size_hint_y=0.1,
            font_name=get_font_name()
        )
        main_layout.add_widget(title)
        
        # 摄像头区域
        camera_layout = BoxLayout(size_hint_y=0.4)
        try:
            self.camera = Camera(play=False, resolution=(640, 480))
            camera_layout.add_widget(self.camera)
        except Exception as e:
            Logger.warning(f"TestApp: Camera initialization failed: {e}")
            placeholder = Label(
                text='Camera Preview\n(Tap Start Camera)',
                font_size='16sp',
                halign='center',
                font_name=get_font_name()
            )
            camera_layout.add_widget(placeholder)
        
        main_layout.add_widget(camera_layout)
        
        # 计数显示
        self.count_label = Label(
            text=f'Count: {self.count}',
            font_size='36sp',
            size_hint_y=0.2,
            font_name=get_font_name()
        )
        main_layout.add_widget(self.count_label)
        
        # 按钮区域
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3, spacing=5)
        
        # 计数按钮
        count_btn = Button(
            text='Count +1',
            font_size='16sp',
            font_name=get_font_name()
        )
        count_btn.bind(on_press=self.increment_count)
        button_layout.add_widget(count_btn)
        
        # 重置按钮
        reset_btn = Button(
            text='Reset',
            font_size='16sp',
            font_name=get_font_name()
        )
        reset_btn.bind(on_press=self.reset_count)
        button_layout.add_widget(reset_btn)
        
        # 摄像头按钮
        camera_btn = Button(
            text='Start Camera',
            font_size='16sp',
            font_name=get_font_name()
        )
        camera_btn.bind(on_press=self.toggle_camera)
        button_layout.add_widget(camera_btn)
        
        # 上传按钮
        upload_btn = Button(
            text='Upload',
            font_size='16sp',
            font_name=get_font_name()
        )
        upload_btn.bind(on_press=self.upload_video)
        button_layout.add_widget(upload_btn)
        
        main_layout.add_widget(button_layout)
        
        return main_layout
    
    def increment_count(self, instance):
        """增加计数"""
        self.count += 1
        self.count_label.text = f'Count: {self.count}'
        Logger.info(f"TestApp: Count increased to {self.count}")
    
    def reset_count(self, instance):
        """重置计数"""
        self.count = 0
        self.count_label.text = f'Count: {self.count}'
        Logger.info("TestApp: Count reset")
    
    def toggle_camera(self, instance):
        """切换摄像头状态"""
        try:
            if self.camera:
                if self.camera.play:
                    self.camera.play = False
                    instance.text = 'Start Camera'
                    Logger.info("TestApp: Camera stopped")
                else:
                    self.camera.play = True
                    instance.text = 'Stop Camera'
                    Logger.info("TestApp: Camera started")
            else:
                Logger.warning("TestApp: Camera not available")
        except Exception as e:
            Logger.error(f"TestApp: Camera toggle failed: {e}")
    
    def upload_video(self, instance):
        """模拟视频上传"""
        try:
            # 创建简单的上传弹窗
            content = BoxLayout(orientation='vertical', spacing=10, padding=20)
            
            status_label = Label(
                text='Simulating video upload...',
                font_name=get_font_name()
            )
            content.add_widget(status_label)
            
            progress_bar = ProgressBar(max=100, value=0)
            content.add_widget(progress_bar)
            
            close_btn = Button(
                text='Close',
                size_hint_y=0.3,
                font_name=get_font_name()
            )
            content.add_widget(close_btn)
            
            popup = Popup(
                title='Upload Progress',
                content=content,
                size_hint=(0.8, 0.6),
                auto_dismiss=False
            )
            
            def close_popup(instance):
                popup.dismiss()
            
            close_btn.bind(on_press=close_popup)
            
            # 模拟上传进度
            def update_progress(dt):
                progress_bar.value += 20
                if progress_bar.value >= 100:
                    status_label.text = 'Upload Complete!'
                    Logger.info("TestApp: Upload simulation completed")
                    return False
                return True
            
            popup.open()
            Clock.schedule_interval(update_progress, 0.5)
            
        except Exception as e:
            Logger.error(f"TestApp: Upload simulation failed: {e}")
    
    def on_start(self):
        """应用启动"""
        Logger.info("TestApp: Application started")
        
        # 请求权限
        if request_permissions:
            try:
                request_permissions()
                Logger.info("TestApp: Permissions requested")
            except Exception as e:
                Logger.warning(f"TestApp: Permission request failed: {e}")
    
    def on_pause(self):
        """应用暂停"""
        Logger.info("TestApp: Application paused")
        return True
    
    def on_resume(self):
        """应用恢复"""
        Logger.info("TestApp: Application resumed")
    
    def on_stop(self):
        """应用停止"""
        Logger.info("TestApp: Application stopped")
        if self.camera and self.camera.play:
            self.camera.play = False


if __name__ == '__main__':
    TestPushupApp().run()
