#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主功能界面
包含摄像头检测、视频上传、实时显示等功能
"""

import cv2
import numpy as np
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.logger import Logger

from core.pose_detector import PoseDetector
from utils.camera_handler import CameraHandler
from utils.permissions import permission_manager


class MainScreen(Screen):
    """主功能界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 初始化组件
        self.pose_detector = None
        self.camera_handler = None
        self.is_detecting = False
        self.current_frame = None
        
        # 统计信息
        self.session_start_time = None
        self.session_counter = 0
        
        self.build_ui()
    
    def build_ui(self):
        """构建用户界面"""
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 顶部信息栏
        self.build_top_bar(main_layout)
        
        # 视频显示区域
        self.build_video_area(main_layout)
        
        # 控制按钮区域
        self.build_control_buttons(main_layout)
        
        # 统计信息区域
        self.build_stats_area(main_layout)
        
        self.add_widget(main_layout)
    
    def build_top_bar(self, parent_layout):
        """构建顶部信息栏"""
        top_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        # 用户信息
        app = self.get_app()
        username = app.current_user if app else "未知用户"
        
        self.user_label = Label(
            text=f'用户: {username}',
            font_size=dp(16),
            color=(0.2, 0.2, 0.2, 1),
            text_size=(None, None),
            halign='left'
        )
        top_layout.add_widget(self.user_label)
        
        # 登出按钮
        logout_button = Button(
            text='登出',
            size_hint_x=None,
            width=dp(80),
            font_size=dp(14),
            background_color=(0.8, 0.3, 0.3, 1)
        )
        logout_button.bind(on_press=self.on_logout_press)
        top_layout.add_widget(logout_button)
        
        parent_layout.add_widget(top_layout)
    
    def build_video_area(self, parent_layout):
        """构建视频显示区域"""
        # 视频显示
        self.video_image = Image(
            size_hint_y=None,
            height=dp(300),
            allow_stretch=True,
            keep_ratio=True
        )
        
        # 设置默认图像
        self.set_default_image()
        
        parent_layout.add_widget(self.video_image)
    
    def build_control_buttons(self, parent_layout):
        """构建控制按钮区域"""
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10)
        )
        
        # 开始/停止检测按钮
        self.start_button = Button(
            text='开始检测',
            font_size=dp(16),
            background_color=(0.3, 0.7, 0.3, 1)
        )
        self.start_button.bind(on_press=self.on_start_detection)
        button_layout.add_widget(self.start_button)
        
        # 上传视频按钮
        upload_button = Button(
            text='上传视频',
            font_size=dp(16),
            background_color=(0.3, 0.5, 0.7, 1)
        )
        upload_button.bind(on_press=self.on_upload_video)
        button_layout.add_widget(upload_button)
        
        # 切换摄像头按钮
        switch_button = Button(
            text='切换摄像头',
            font_size=dp(16),
            background_color=(0.7, 0.5, 0.3, 1)
        )
        switch_button.bind(on_press=self.on_switch_camera)
        button_layout.add_widget(switch_button)
        
        parent_layout.add_widget(button_layout)

    def build_stats_area(self, parent_layout):
        """构建统计信息区域"""
        stats_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(80),
            spacing=dp(10)
        )

        # 当前计数
        self.counter_label = Label(
            text='计数: 0',
            font_size=dp(18),
            color=(0.2, 0.2, 0.2, 1),
            bold=True
        )
        stats_layout.add_widget(self.counter_label)

        # 当前状态
        self.stage_label = Label(
            text='状态: 准备',
            font_size=dp(16),
            color=(0.4, 0.4, 0.4, 1)
        )
        stats_layout.add_widget(self.stage_label)

        # 重置按钮
        reset_button = Button(
            text='重置',
            size_hint_x=None,
            width=dp(80),
            font_size=dp(14),
            background_color=(0.6, 0.6, 0.6, 1)
        )
        reset_button.bind(on_press=self.on_reset_counter)
        stats_layout.add_widget(reset_button)

        parent_layout.add_widget(stats_layout)

    def get_app(self):
        """获取应用实例"""
        try:
            from main import get_app
            return get_app()
        except:
            return None

    def set_default_image(self):
        """设置默认图像"""
        # 创建一个简单的默认图像
        default_image = np.zeros((240, 320, 3), dtype=np.uint8)
        default_image.fill(128)  # 灰色背景

        # 添加文字
        cv2.putText(default_image, 'Camera Ready', (80, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        self.update_video_display(default_image)

    def update_video_display(self, frame):
        """更新视频显示"""
        if frame is None:
            return

        try:
            # 转换颜色格式
            if len(frame.shape) == 3:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                frame_rgb = frame

            # 创建纹理
            height, width = frame_rgb.shape[:2]
            texture = Texture.create(size=(width, height))
            texture.blit_buffer(frame_rgb.flatten(), colorfmt='rgb', bufferfmt='ubyte')
            texture.flip_vertical()

            # 更新图像
            self.video_image.texture = texture

        except Exception as e:
            Logger.error(f"MainScreen: 更新视频显示失败: {e}")

    def on_frame_callback(self, frame, counter, stage, arm_angle, leg_angle):
        """帧处理回调函数"""
        # 更新显示
        self.update_video_display(frame)

        # 更新统计信息
        self.counter_label.text = f'计数: {counter}'
        self.stage_label.text = f'状态: {stage if stage else "准备"}'

        # 检查是否有新的俯卧撑完成
        if counter > self.session_counter:
            self.session_counter = counter
            Logger.info(f"MainScreen: 完成第 {counter} 个俯卧撑")

    def on_start_detection(self, instance):
        """开始/停止检测按钮事件"""
        if not self.is_detecting:
            self.start_detection()
        else:
            self.stop_detection()

    def start_detection(self):
        """开始检测"""
        # 检查摄像头权限
        if not permission_manager.check_camera_permission():
            self.show_message('错误', '需要摄像头权限才能开始检测')
            permission_manager.request_camera_permission()
            return

        try:
            # 初始化姿态检测器
            self.pose_detector = PoseDetector(callback=self.on_frame_callback)

            # 初始化摄像头
            self.camera_handler = CameraHandler()
            self.camera_handler.set_frame_callback(self.on_camera_frame)

            if self.camera_handler.start_capture():
                self.is_detecting = True
                self.start_button.text = '停止检测'
                self.start_button.background_color = (0.8, 0.3, 0.3, 1)

                # 重置计数器
                self.session_counter = 0

                Logger.info("MainScreen: 开始俯卧撑检测")
            else:
                self.show_message('错误', '无法启动摄像头')

        except Exception as e:
            Logger.error(f"MainScreen: 启动检测失败: {e}")
            self.show_message('错误', f'启动检测失败: {str(e)}')

    def stop_detection(self):
        """停止检测"""
        try:
            self.is_detecting = False

            # 停止摄像头
            if self.camera_handler:
                self.camera_handler.stop_capture()
                self.camera_handler = None

            # 保存结果
            if self.pose_detector and self.session_counter > 0:
                self.save_session_result()

            # 清理资源
            if self.pose_detector:
                self.pose_detector.cleanup()
                self.pose_detector = None

            # 更新UI
            self.start_button.text = '开始检测'
            self.start_button.background_color = (0.3, 0.7, 0.3, 1)
            self.set_default_image()

            Logger.info("MainScreen: 停止俯卧撑检测")

        except Exception as e:
            Logger.error(f"MainScreen: 停止检测失败: {e}")

    def on_camera_frame(self, frame):
        """摄像头帧回调"""
        if self.pose_detector and frame is not None:
            processed_frame, detected = self.pose_detector.process_frame(frame)
            if not detected:
                # 如果没有检测到姿态，直接显示原始帧
                self.update_video_display(frame)

    def save_session_result(self):
        """保存本次训练结果"""
        try:
            app = self.get_app()
            if app and app.current_user:
                # 保存到用户管理器
                app.user_manager.add_pushup_record(app.current_user, self.session_counter)

                # 显示结果
                self.show_session_result()

                Logger.info(f"MainScreen: 保存训练结果: {self.session_counter} 个俯卧撑")

        except Exception as e:
            Logger.error(f"MainScreen: 保存结果失败: {e}")

    def show_session_result(self):
        """显示训练结果"""
        message = f'本次训练完成！\n\n俯卧撑次数: {self.session_counter}'
        self.show_message('训练结果', message)

    def on_upload_video(self, instance):
        """上传视频按钮事件"""
        self.show_file_chooser()

    def show_file_chooser(self):
        """显示文件选择器"""
        content = BoxLayout(orientation='vertical', spacing=dp(10))

        # 文件选择器
        filechooser = FileChooserIconView(
            filters=['*.mp4', '*.avi', '*.mov', '*.mkv'],
            size_hint_y=0.8
        )
        content.add_widget(filechooser)

        # 按钮布局
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        cancel_button = Button(text='取消')
        select_button = Button(text='选择')

        button_layout.add_widget(cancel_button)
        button_layout.add_widget(select_button)
        content.add_widget(button_layout)

        # 创建弹窗
        popup = Popup(
            title='选择视频文件',
            content=content,
            size_hint=(0.9, 0.8)
        )

        def on_cancel(instance):
            popup.dismiss()

        def on_select(instance):
            if filechooser.selection:
                video_path = filechooser.selection[0]
                popup.dismiss()
                self.process_uploaded_video(video_path)
            else:
                self.show_message('提示', '请选择一个视频文件')

        cancel_button.bind(on_press=on_cancel)
        select_button.bind(on_press=on_select)

        popup.open()

    def process_uploaded_video(self, video_path):
        """处理上传的视频"""
        try:
            Logger.info(f"MainScreen: 开始处理视频: {video_path}")

            # 初始化姿态检测器
            self.pose_detector = PoseDetector(callback=self.on_frame_callback)

            # 打开视频文件
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                self.show_message('错误', '无法打开视频文件')
                return

            # 重置计数器
            self.session_counter = 0
            self.is_detecting = True

            # 处理视频帧
            Clock.schedule_interval(lambda dt: self.process_video_frame(cap), 1.0/30.0)

        except Exception as e:
            Logger.error(f"MainScreen: 处理视频失败: {e}")
            self.show_message('错误', f'处理视频失败: {str(e)}')

    def process_video_frame(self, cap):
        """处理视频帧"""
        try:
            ret, frame = cap.read()

            if not ret:
                # 视频结束
                cap.release()
                self.is_detecting = False

                if self.session_counter > 0:
                    self.save_session_result()

                if self.pose_detector:
                    self.pose_detector.cleanup()
                    self.pose_detector = None

                self.set_default_image()
                return False  # 停止调度

            # 处理帧
            if self.pose_detector:
                self.pose_detector.process_frame(frame)

            return True  # 继续调度

        except Exception as e:
            Logger.error(f"MainScreen: 处理视频帧失败: {e}")
            return False

    def on_switch_camera(self, instance):
        """切换摄像头按钮事件"""
        if self.camera_handler and self.is_detecting:
            self.camera_handler.switch_camera()
            Logger.info("MainScreen: 切换摄像头")
        else:
            self.show_message('提示', '请先开始检测')

    def on_reset_counter(self, instance):
        """重置计数器按钮事件"""
        if self.pose_detector:
            self.pose_detector.reset_counter()

        self.session_counter = 0
        self.counter_label.text = '计数: 0'
        self.stage_label.text = '状态: 准备'

        Logger.info("MainScreen: 重置计数器")

    def on_logout_press(self, instance):
        """登出按钮事件"""
        # 停止检测
        if self.is_detecting:
            self.stop_detection()

        # 登出用户
        app = self.get_app()
        if app:
            app.logout_user()

        Logger.info("MainScreen: 用户登出")

    def show_message(self, title, message, callback=None):
        """显示消息弹窗"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        message_label = Label(
            text=message,
            text_size=(dp(250), None),
            halign='center',
            valign='middle'
        )
        content.add_widget(message_label)

        ok_button = Button(
            text='确定',
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(ok_button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        def on_ok_press(instance):
            popup.dismiss()
            if callback:
                callback(instance)

        ok_button.bind(on_press=on_ok_press)
        popup.open()

    def on_enter(self):
        """界面进入时的处理"""
        Logger.info("MainScreen: 进入主界面")

        # 更新用户信息
        app = self.get_app()
        if app and app.current_user:
            self.user_label.text = f'用户: {app.current_user}'

    def on_leave(self):
        """界面离开时的处理"""
        Logger.info("MainScreen: 离开主界面")

        # 停止检测
        if self.is_detecting:
            self.stop_detection()
