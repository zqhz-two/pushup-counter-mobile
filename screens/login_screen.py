#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录界面
移动端优化的登录界面，支持触摸操作
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.logger import Logger


class LoginScreen(Screen):
    """登录界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """构建用户界面"""
        # 主布局
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15)
        )
        
        # 标题
        title = Label(
            text='俯卧撑计数系统',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(60),
            color=(0.2, 0.2, 0.2, 1)
        )
        main_layout.add_widget(title)
        
        # 副标题
        subtitle = Label(
            text='请登录您的账户',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            color=(0.5, 0.5, 0.5, 1)
        )
        main_layout.add_widget(subtitle)
        
        # 添加间距
        main_layout.add_widget(Label(size_hint_y=None, height=dp(20)))
        
        # 用户名输入
        username_label = Label(
            text='用户名:',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30),
            text_size=(None, None),
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        main_layout.add_widget(username_label)
        
        self.username_input = TextInput(
            hint_text='请输入用户名',
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16),
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        main_layout.add_widget(self.username_input)
        
        # 密码输入
        password_label = Label(
            text='密码:',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30),
            text_size=(None, None),
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        main_layout.add_widget(password_label)
        
        self.password_input = TextInput(
            hint_text='请输入密码',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16),
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        main_layout.add_widget(self.password_input)
        
        # 添加间距
        main_layout.add_widget(Label(size_hint_y=None, height=dp(20)))
        
        # 按钮布局
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        # 登录按钮
        login_button = Button(
            text='登录',
            font_size=dp(18),
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        login_button.bind(on_press=self.on_login_press)
        button_layout.add_widget(login_button)
        
        # 注册按钮
        register_button = Button(
            text='注册',
            font_size=dp(18),
            background_color=(0.3, 0.5, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        register_button.bind(on_press=self.on_register_press)
        button_layout.add_widget(register_button)
        
        main_layout.add_widget(button_layout)
        
        # 添加弹性空间
        main_layout.add_widget(Label())
        
        self.add_widget(main_layout)
    
    def on_login_press(self, instance):
        """登录按钮点击事件"""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.show_message('错误', '用户名和密码不能为空！')
            return
        
        # 获取应用实例
        app = self.manager.app if hasattr(self.manager, 'app') else None
        if not app:
            from main import get_app
            app = get_app()
        
        # 尝试登录
        if app.login_user(username, password):
            self.show_message('成功', '登录成功！', self.on_login_success)
            Logger.info(f"LoginScreen: 用户 {username} 登录成功")
        else:
            self.show_message('错误', '用户名或密码错误！')
            Logger.warning(f"LoginScreen: 用户 {username} 登录失败")
    
    def on_register_press(self, instance):
        """注册按钮点击事件"""
        self.manager.current = 'register'
        Logger.info("LoginScreen: 切换到注册界面")
    
    def on_login_success(self, instance):
        """登录成功回调"""
        # 清空输入框
        self.username_input.text = ''
        self.password_input.text = ''
    
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
        
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        
        ok_button = Button(
            text='确定',
            size_hint_y=None,
            height=dp(40)
        )
        button_layout.add_widget(ok_button)
        content.add_widget(button_layout)
        
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
        Logger.info("LoginScreen: 进入登录界面")
        # 清空输入框
        self.username_input.text = ''
        self.password_input.text = ''
    
    def on_leave(self):
        """界面离开时的处理"""
        Logger.info("LoginScreen: 离开登录界面")
