#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
俯卧撑计数系统 - 移动端主程序
基于Kivy框架开发的Android应用
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.config import Config

# 配置Kivy
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)


class PushupCounterApp(App):
    """俯卧撑计数应用主类"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.count = 0

    def build(self):
        """构建应用界面"""
        # 创建主布局
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # 添加标题
        title = Label(
            text='俯卧撑计数器',
            font_size='24sp',
            size_hint_y=0.2
        )
        layout.add_widget(title)

        # 添加计数显示
        self.count_label = Label(
            text=f'计数: {self.count}',
            font_size='48sp',
            size_hint_y=0.4
        )
        layout.add_widget(self.count_label)

        # 添加按钮布局
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.4, spacing=10)

        # 计数按钮
        count_btn = Button(
            text='计数 +1',
            font_size='20sp'
        )
        count_btn.bind(on_press=self.increment_count)
        button_layout.add_widget(count_btn)

        # 重置按钮
        reset_btn = Button(
            text='重置',
            font_size='20sp'
        )
        reset_btn.bind(on_press=self.reset_count)
        button_layout.add_widget(reset_btn)

        layout.add_widget(button_layout)

        return layout

    def increment_count(self, instance):
        """增加计数"""
        self.count += 1
        self.count_label.text = f'计数: {self.count}'
        Logger.info(f"PushupCounter: 计数增加到 {self.count}")

    def reset_count(self, instance):
        """重置计数"""
        self.count = 0
        self.count_label.text = f'计数: {self.count}'
        Logger.info("PushupCounter: 计数已重置")

    def on_start(self):
        """应用启动时的初始化"""
        Logger.info("PushupCounter: 应用启动")

    def on_pause(self):
        """应用暂停时保存数据"""
        Logger.info("PushupCounter: 应用暂停")
        return True

    def on_resume(self):
        """应用恢复时的处理"""
        Logger.info("PushupCounter: 应用恢复")

    def on_stop(self):
        """应用停止时的清理"""
        Logger.info("PushupCounter: 应用停止")


if __name__ == '__main__':
    # 启动应用
    PushupCounterApp().run()
