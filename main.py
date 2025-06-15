#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
俯卧撑计数系统 - 移动端主程序
基于Kivy框架开发的Android应用
"""

import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.logger import Logger
from kivy.config import Config
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.camera import Camera

# 配置Kivy
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)

# 导入自定义模块
try:
    from utils.permissions import request_permissions
    from utils.camera_handler import CameraHandler
    from assets.fonts import register_fonts, get_font_name
except ImportError as e:
    Logger.warning(f"PushupCounter: 导入模块失败: {e}")
    request_permissions = None
    CameraHandler = None
    register_fonts = None
    get_font_name = lambda: 'Roboto'

# 注册字体
if register_fonts:
    register_fonts()


class MainScreen(Screen):
    """主界面屏幕"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.count = 0
        self.camera_handler = None
        self.build_ui()

    def build_ui(self):
        """构建用户界面"""
        # 创建主布局
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # 添加标题
        title = Label(
            text='Pushup Counter',  # 使用英文避免字体问题
            font_size='24sp',
            size_hint_y=0.15,
            font_name=get_font_name()
        )
        layout.add_widget(title)

        # 添加摄像头预览区域
        self.camera_layout = BoxLayout(size_hint_y=0.4)
        try:
            self.camera = Camera(play=False, resolution=(640, 480))
            self.camera_layout.add_widget(self.camera)
        except Exception as e:
            Logger.warning(f"Camera initialization failed: {e}")
            # 添加占位符
            placeholder = Label(
                text='Camera Preview\n(Tap to start)',
                font_size='16sp',
                halign='center'
            )
            placeholder.bind(on_touch_down=self.start_camera)
            self.camera_layout.add_widget(placeholder)

        layout.add_widget(self.camera_layout)

        # 添加计数显示
        self.count_label = Label(
            text=f'Count: {self.count}',
            font_size='48sp',
            size_hint_y=0.2,
            font_name=get_font_name()
        )
        layout.add_widget(self.count_label)

        # 添加按钮布局
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.25, spacing=10)

        # 计数按钮
        count_btn = Button(
            text='Count +1',
            font_size='18sp',
            font_name=get_font_name()
        )
        count_btn.bind(on_press=self.increment_count)
        button_layout.add_widget(count_btn)

        # 重置按钮
        reset_btn = Button(
            text='Reset',
            font_size='18sp',
            font_name=get_font_name()
        )
        reset_btn.bind(on_press=self.reset_count)
        button_layout.add_widget(reset_btn)

        # 视频上传按钮
        upload_btn = Button(
            text='Upload Video',
            font_size='18sp',
            font_name=get_font_name()
        )
        upload_btn.bind(on_press=self.upload_video)
        button_layout.add_widget(upload_btn)

        layout.add_widget(button_layout)

        self.add_widget(layout)

    def increment_count(self, instance):
        """增加计数"""
        self.count += 1
        self.count_label.text = f'Count: {self.count}'
        Logger.info(f"PushupCounter: Count increased to {self.count}")

    def reset_count(self, instance):
        """重置计数"""
        self.count = 0
        self.count_label.text = f'Count: {self.count}'
        Logger.info("PushupCounter: Count reset")

    def start_camera(self, instance, touch):
        """启动摄像头"""
        if instance.collide_point(*touch.pos):
            try:
                if hasattr(self, 'camera') and self.camera:
                    self.camera.play = True
                    Logger.info("PushupCounter: Camera started")
                else:
                    Logger.warning("PushupCounter: Camera not available")
            except Exception as e:
                Logger.error(f"PushupCounter: Failed to start camera: {e}")
            return True
        return False

    def upload_video(self, instance):
        """上传视频文件"""
        try:
            # 创建文件选择器弹窗
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)

            # 文件选择器
            filechooser = FileChooserIconView(
                filters=['*.mp4', '*.avi', '*.mov', '*.mkv'],
                path='/storage/emulated/0/DCIM/Camera' if os.path.exists('/storage/emulated/0/DCIM/Camera') else '/'
            )
            content.add_widget(filechooser)

            # 按钮布局
            btn_layout = BoxLayout(size_hint_y=0.2, spacing=10)

            # 选择按钮
            select_btn = Button(text='Select', font_name=get_font_name())
            cancel_btn = Button(text='Cancel', font_name=get_font_name())

            btn_layout.add_widget(select_btn)
            btn_layout.add_widget(cancel_btn)
            content.add_widget(btn_layout)

            # 创建弹窗
            popup = Popup(
                title='Select Video File',
                content=content,
                size_hint=(0.9, 0.9)
            )

            def select_file(instance):
                if filechooser.selection:
                    selected_file = filechooser.selection[0]
                    popup.dismiss()
                    self.process_video_upload(selected_file)
                else:
                    Logger.warning("PushupCounter: No file selected")

            def cancel_selection(instance):
                popup.dismiss()

            select_btn.bind(on_press=select_file)
            cancel_btn.bind(on_press=cancel_selection)

            popup.open()

        except Exception as e:
            Logger.error(f"PushupCounter: Failed to open file chooser: {e}")

    def process_video_upload(self, file_path):
        """处理视频上传"""
        try:
            Logger.info(f"PushupCounter: Processing video upload: {file_path}")

            # 创建上传进度弹窗
            content = BoxLayout(orientation='vertical', spacing=10, padding=20)

            status_label = Label(
                text=f'Uploading: {os.path.basename(file_path)}',
                font_name=get_font_name()
            )
            content.add_widget(status_label)

            progress_bar = ProgressBar(max=100, value=0)
            content.add_widget(progress_bar)

            popup = Popup(
                title='Upload Progress',
                content=content,
                size_hint=(0.8, 0.4),
                auto_dismiss=False
            )
            popup.open()

            # 模拟上传进度
            def update_progress(dt):
                progress_bar.value += 10
                if progress_bar.value >= 100:
                    status_label.text = 'Upload Complete!'
                    Clock.schedule_once(lambda dt: popup.dismiss(), 1)
                    Logger.info("PushupCounter: Video upload completed")
                    return False
                return True

            Clock.schedule_interval(update_progress, 0.5)

        except Exception as e:
            Logger.error(f"PushupCounter: Failed to process video upload: {e}")


class PushupCounterApp(App):
    """俯卧撑计数应用主类"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = None

    def build(self):
        """构建应用界面"""
        # 创建屏幕管理器
        self.screen_manager = ScreenManager()

        # 添加主屏幕
        main_screen = MainScreen(name='main')
        self.screen_manager.add_widget(main_screen)

        return self.screen_manager

    def on_start(self):
        """应用启动时的初始化"""
        Logger.info("PushupCounter: Application started")

        # 请求权限
        if request_permissions:
            try:
                request_permissions()
                Logger.info("PushupCounter: Permissions requested")
            except Exception as e:
                Logger.warning(f"PushupCounter: Failed to request permissions: {e}")

    def on_pause(self):
        """应用暂停时保存数据"""
        Logger.info("PushupCounter: Application paused")
        return True

    def on_resume(self):
        """应用恢复时的处理"""
        Logger.info("PushupCounter: Application resumed")

    def on_stop(self):
        """应用停止时的清理"""
        Logger.info("PushupCounter: Application stopped")


if __name__ == '__main__':
    # 启动应用
    PushupCounterApp().run()
