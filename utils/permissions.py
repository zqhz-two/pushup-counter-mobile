#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android权限管理模块
处理摄像头、存储等权限申请
"""

from kivy.logger import Logger


class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        self.permissions_granted = {}
        self.required_permissions = [
            'android.permission.CAMERA',
            'android.permission.WRITE_EXTERNAL_STORAGE',
            'android.permission.READ_EXTERNAL_STORAGE',
        ]
    
    def request_permissions(self):
        """申请必要权限"""
        try:
            # 检查是否在Android环境
            from android.permissions import request_permissions, Permission
            from android.permissions import check_permission
            
            # 检查权限状态
            permissions_to_request = []
            
            for permission in self.required_permissions:
                if not check_permission(permission):
                    permissions_to_request.append(permission)
                    Logger.info(f"PermissionManager: 需要申请权限: {permission}")
                else:
                    self.permissions_granted[permission] = True
                    Logger.info(f"PermissionManager: 权限已授予: {permission}")
            
            # 申请缺失的权限
            if permissions_to_request:
                Logger.info(f"PermissionManager: 申请权限: {permissions_to_request}")
                request_permissions(permissions_to_request)
            else:
                Logger.info("PermissionManager: 所有权限已授予")
                
        except ImportError:
            # 非Android环境，跳过权限检查
            Logger.info("PermissionManager: 非Android环境，跳过权限检查")
            for permission in self.required_permissions:
                self.permissions_granted[permission] = True
        except Exception as e:
            Logger.error(f"PermissionManager: 权限申请失败: {e}")
    
    def check_camera_permission(self):
        """检查摄像头权限"""
        try:
            from android.permissions import check_permission
            return check_permission('android.permission.CAMERA')
        except ImportError:
            return True  # 非Android环境默认有权限
        except Exception as e:
            Logger.error(f"PermissionManager: 检查摄像头权限失败: {e}")
            return False
    
    def check_storage_permission(self):
        """检查存储权限"""
        try:
            from android.permissions import check_permission
            return (check_permission('android.permission.WRITE_EXTERNAL_STORAGE') and
                   check_permission('android.permission.READ_EXTERNAL_STORAGE'))
        except ImportError:
            return True  # 非Android环境默认有权限
        except Exception as e:
            Logger.error(f"PermissionManager: 检查存储权限失败: {e}")
            return False
    
    def request_camera_permission(self):
        """单独申请摄像头权限"""
        try:
            from android.permissions import request_permission
            request_permission('android.permission.CAMERA')
            Logger.info("PermissionManager: 已申请摄像头权限")
        except ImportError:
            Logger.info("PermissionManager: 非Android环境，跳过摄像头权限申请")
        except Exception as e:
            Logger.error(f"PermissionManager: 申请摄像头权限失败: {e}")
    
    def request_storage_permission(self):
        """单独申请存储权限"""
        try:
            from android.permissions import request_permissions
            request_permissions([
                'android.permission.WRITE_EXTERNAL_STORAGE',
                'android.permission.READ_EXTERNAL_STORAGE'
            ])
            Logger.info("PermissionManager: 已申请存储权限")
        except ImportError:
            Logger.info("PermissionManager: 非Android环境，跳过存储权限申请")
        except Exception as e:
            Logger.error(f"PermissionManager: 申请存储权限失败: {e}")
    
    def get_permission_status(self):
        """获取权限状态"""
        status = {}
        try:
            from android.permissions import check_permission
            
            for permission in self.required_permissions:
                status[permission] = check_permission(permission)
                
        except ImportError:
            # 非Android环境，所有权限默认为True
            for permission in self.required_permissions:
                status[permission] = True
        except Exception as e:
            Logger.error(f"PermissionManager: 获取权限状态失败: {e}")
            for permission in self.required_permissions:
                status[permission] = False
        
        return status
    
    def is_all_permissions_granted(self):
        """检查是否所有权限都已授予"""
        status = self.get_permission_status()
        return all(status.values())


# 全局权限管理器实例
permission_manager = PermissionManager()
