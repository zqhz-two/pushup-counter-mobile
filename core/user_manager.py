#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理模块
处理用户注册、登录、数据存储等功能
"""

import json
import os
import hashlib
from datetime import datetime
from kivy.logger import Logger


class UserManager:
    """用户管理类"""
    
    def __init__(self):
        self.users_file = self._get_users_file_path()
        self.users_data = {}
        self.load_users()
    
    def _get_users_file_path(self):
        """获取用户数据文件路径"""
        # 在Android上使用应用私有目录
        try:
            from android.storage import app_storage_path
            data_dir = app_storage_path()
        except ImportError:
            # 桌面环境下使用当前目录
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            os.makedirs(data_dir, exist_ok=True)
        
        return os.path.join(data_dir, 'users.json')
    
    def _hash_password(self, password):
        """密码哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self):
        """从文件加载用户数据"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users_data = json.load(f)
                Logger.info(f"UserManager: 加载了 {len(self.users_data)} 个用户")
            else:
                self.users_data = {}
                Logger.info("UserManager: 创建新的用户数据文件")
        except Exception as e:
            Logger.error(f"UserManager: 加载用户数据失败: {e}")
            self.users_data = {}
    
    def save_users(self):
        """保存用户数据到文件"""
        try:
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users_data, f, ensure_ascii=False, indent=2)
            Logger.info("UserManager: 用户数据已保存")
        except Exception as e:
            Logger.error(f"UserManager: 保存用户数据失败: {e}")
    
    def register(self, username, password, name=""):
        """用户注册"""
        if not username or not password:
            return False, "用户名和密码不能为空"
        
        if username in self.users_data:
            return False, "用户名已存在"
        
        # 创建用户数据
        user_data = {
            'password_hash': self._hash_password(password),
            'name': name,
            'created_at': datetime.now().isoformat(),
            'pushup_records': [],
            'total_pushups': 0,
            'best_session': 0
        }
        
        self.users_data[username] = user_data
        self.save_users()
        
        Logger.info(f"UserManager: 用户 {username} 注册成功")
        return True, "注册成功"
    
    def authenticate(self, username, password):
        """用户认证"""
        if username not in self.users_data:
            return False
        
        stored_hash = self.users_data[username]['password_hash']
        input_hash = self._hash_password(password)
        
        return stored_hash == input_hash
    
    def get_user_info(self, username):
        """获取用户信息"""
        return self.users_data.get(username, {})
    
    def add_pushup_record(self, username, count, duration=None):
        """添加俯卧撑记录"""
        if username not in self.users_data:
            return False
        
        record = {
            'count': count,
            'date': datetime.now().isoformat(),
            'duration': duration
        }
        
        user_data = self.users_data[username]
        user_data['pushup_records'].append(record)
        user_data['total_pushups'] += count
        user_data['best_session'] = max(user_data['best_session'], count)
        
        self.save_users()
        Logger.info(f"UserManager: 为用户 {username} 添加记录: {count} 个俯卧撑")
        return True
    
    def get_user_statistics(self, username):
        """获取用户统计信息"""
        if username not in self.users_data:
            return None
        
        user_data = self.users_data[username]
        records = user_data['pushup_records']
        
        if not records:
            return {
                'total_pushups': 0,
                'total_sessions': 0,
                'best_session': 0,
                'average_per_session': 0,
                'recent_records': []
            }
        
        total_sessions = len(records)
        total_pushups = user_data['total_pushups']
        best_session = user_data['best_session']
        average_per_session = total_pushups / total_sessions if total_sessions > 0 else 0
        
        # 获取最近10条记录
        recent_records = sorted(records, key=lambda x: x['date'], reverse=True)[:10]
        
        return {
            'total_pushups': total_pushups,
            'total_sessions': total_sessions,
            'best_session': best_session,
            'average_per_session': round(average_per_session, 1),
            'recent_records': recent_records
        }
