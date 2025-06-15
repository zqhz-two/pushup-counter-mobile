#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果展示界面
显示用户的训练历史和统计信息
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.logger import Logger


class ResultScreen(Screen):
    """结果展示界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """构建用户界面"""
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 标题
        title = Label(
            text='训练统计',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(60),
            color=(0.2, 0.2, 0.2, 1)
        )
        main_layout.add_widget(title)
        
        # 统计信息区域
        self.build_stats_area(main_layout)
        
        # 历史记录区域
        self.build_history_area(main_layout)
        
        # 返回按钮
        back_button = Button(
            text='返回',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_button.bind(on_press=self.on_back_press)
        main_layout.add_widget(back_button)
        
        self.add_widget(main_layout)
    
    def build_stats_area(self, parent_layout):
        """构建统计信息区域"""
        stats_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            spacing=dp(5)
        )
        
        # 统计标签
        self.total_label = Label(
            text='总计: 0 个俯卧撑',
            font_size=dp(18),
            color=(0.2, 0.2, 0.2, 1)
        )
        stats_layout.add_widget(self.total_label)
        
        self.sessions_label = Label(
            text='训练次数: 0 次',
            font_size=dp(16),
            color=(0.4, 0.4, 0.4, 1)
        )
        stats_layout.add_widget(self.sessions_label)
        
        self.best_label = Label(
            text='最佳记录: 0 个',
            font_size=dp(16),
            color=(0.4, 0.4, 0.4, 1)
        )
        stats_layout.add_widget(self.best_label)
        
        self.average_label = Label(
            text='平均每次: 0.0 个',
            font_size=dp(16),
            color=(0.4, 0.4, 0.4, 1)
        )
        stats_layout.add_widget(self.average_label)
        
        parent_layout.add_widget(stats_layout)
    
    def build_history_area(self, parent_layout):
        """构建历史记录区域"""
        # 历史记录标题
        history_title = Label(
            text='最近记录',
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40),
            color=(0.2, 0.2, 0.2, 1)
        )
        parent_layout.add_widget(history_title)
        
        # 滚动视图
        scroll = ScrollView()
        
        # 历史记录布局
        self.history_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5)
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        
        scroll.add_widget(self.history_layout)
        parent_layout.add_widget(scroll)
    
    def update_statistics(self):
        """更新统计信息"""
        try:
            app = self.get_app()
            if not app or not app.current_user:
                return
            
            # 获取用户统计信息
            stats = app.user_manager.get_user_statistics(app.current_user)
            
            if stats:
                self.total_label.text = f'总计: {stats["total_pushups"]} 个俯卧撑'
                self.sessions_label.text = f'训练次数: {stats["total_sessions"]} 次'
                self.best_label.text = f'最佳记录: {stats["best_session"]} 个'
                self.average_label.text = f'平均每次: {stats["average_per_session"]} 个'
                
                # 更新历史记录
                self.update_history(stats["recent_records"])
            
        except Exception as e:
            Logger.error(f"ResultScreen: 更新统计信息失败: {e}")
    
    def update_history(self, records):
        """更新历史记录"""
        # 清空现有记录
        self.history_layout.clear_widgets()
        
        if not records:
            no_data_label = Label(
                text='暂无训练记录',
                font_size=dp(16),
                size_hint_y=None,
                height=dp(40),
                color=(0.6, 0.6, 0.6, 1)
            )
            self.history_layout.add_widget(no_data_label)
            return
        
        # 添加记录
        for record in records:
            record_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40),
                spacing=dp(10)
            )
            
            # 日期
            date_str = record['date'][:10]  # 只显示日期部分
            date_label = Label(
                text=date_str,
                font_size=dp(14),
                size_hint_x=0.4,
                color=(0.4, 0.4, 0.4, 1)
            )
            record_layout.add_widget(date_label)
            
            # 次数
            count_label = Label(
                text=f'{record["count"]} 个',
                font_size=dp(16),
                size_hint_x=0.3,
                color=(0.2, 0.2, 0.2, 1),
                bold=True
            )
            record_layout.add_widget(count_label)
            
            # 时长（如果有）
            duration_text = ''
            if record.get('duration'):
                duration_text = f'{record["duration"]:.1f}s'
            
            duration_label = Label(
                text=duration_text,
                font_size=dp(14),
                size_hint_x=0.3,
                color=(0.6, 0.6, 0.6, 1)
            )
            record_layout.add_widget(duration_label)
            
            self.history_layout.add_widget(record_layout)
    
    def get_app(self):
        """获取应用实例"""
        try:
            from main import get_app
            return get_app()
        except:
            return None
    
    def on_back_press(self, instance):
        """返回按钮事件"""
        self.manager.current = 'main'
        Logger.info("ResultScreen: 返回主界面")
    
    def on_enter(self):
        """界面进入时的处理"""
        Logger.info("ResultScreen: 进入结果界面")
        self.update_statistics()
    
    def on_leave(self):
        """界面离开时的处理"""
        Logger.info("ResultScreen: 离开结果界面")
