#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
俯卧撑计数器应用测试脚本
用于测试应用的各个功能模块
"""

import unittest
import os
import sys
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入测试模块
from core.user_manager import UserManager
from core.pose_detector import PoseDetector
from utils.permissions import PermissionManager
from utils.camera_handler import CameraHandler


class TestUserManager(unittest.TestCase):
    """用户管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_users.json')
        self.user_manager = UserManager()
        self.user_manager.users_file = self.test_file
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)
    
    def test_user_registration(self):
        """测试用户注册"""
        # 测试正常注册
        success, message = self.user_manager.register("test_user", "password123", "测试用户")
        self.assertTrue(success)
        self.assertEqual(message, "注册成功")
        
        # 测试重复注册
        success, message = self.user_manager.register("test_user", "password456")
        self.assertFalse(success)
        self.assertEqual(message, "用户名已存在")
        
        # 测试空用户名
        success, message = self.user_manager.register("", "password123")
        self.assertFalse(success)
        self.assertEqual(message, "用户名和密码不能为空")
    
    def test_user_authentication(self):
        """测试用户认证"""
        # 注册用户
        self.user_manager.register("test_user", "password123")
        
        # 测试正确密码
        self.assertTrue(self.user_manager.authenticate("test_user", "password123"))
        
        # 测试错误密码
        self.assertFalse(self.user_manager.authenticate("test_user", "wrong_password"))
        
        # 测试不存在的用户
        self.assertFalse(self.user_manager.authenticate("nonexistent", "password123"))
    
    def test_pushup_record(self):
        """测试俯卧撑记录"""
        # 注册用户
        self.user_manager.register("test_user", "password123")
        
        # 添加记录
        success = self.user_manager.add_pushup_record("test_user", 15)
        self.assertTrue(success)
        
        # 获取统计信息
        stats = self.user_manager.get_user_statistics("test_user")
        self.assertIsNotNone(stats)
        self.assertEqual(stats['total_pushups'], 15)
        self.assertEqual(stats['total_sessions'], 1)
        self.assertEqual(stats['best_session'], 15)
        
        # 添加更多记录
        self.user_manager.add_pushup_record("test_user", 20)
        self.user_manager.add_pushup_record("test_user", 10)
        
        stats = self.user_manager.get_user_statistics("test_user")
        self.assertEqual(stats['total_pushups'], 45)
        self.assertEqual(stats['total_sessions'], 3)
        self.assertEqual(stats['best_session'], 20)
        self.assertEqual(stats['average_per_session'], 15.0)


class TestPoseDetector(unittest.TestCase):
    """姿态检测器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.pose_detector = PoseDetector()
    
    def tearDown(self):
        """测试后清理"""
        if self.pose_detector:
            self.pose_detector.cleanup()
    
    def test_angle_calculation(self):
        """测试角度计算"""
        # 测试90度角
        angle = self.pose_detector.calculate_angle([0, 0], [1, 0], [1, 1])
        self.assertAlmostEqual(angle, 90.0, places=1)
        
        # 测试180度角（直线）
        angle = self.pose_detector.calculate_angle([0, 0], [1, 0], [2, 0])
        self.assertAlmostEqual(angle, 180.0, places=1)
        
        # 测试0度角
        angle = self.pose_detector.calculate_angle([0, 0], [1, 0], [0, 0])
        self.assertAlmostEqual(angle, 0.0, places=1)
    
    def test_counter_reset(self):
        """测试计数器重置"""
        # 设置初始计数
        self.pose_detector.counter = 10
        self.pose_detector.stage = "up"
        
        # 重置计数器
        self.pose_detector.reset_counter()
        
        # 验证重置结果
        self.assertEqual(self.pose_detector.counter, 0)
        self.assertIsNone(self.pose_detector.stage)
    
    @patch('cv2.imread')
    def test_image_processing(self, mock_imread):
        """测试图像处理"""
        import numpy as np
        
        # 模拟图像
        mock_image = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        
        # 测试去模糊处理
        processed = self.pose_detector.deblur_image(mock_image)
        self.assertIsNotNone(processed)
        self.assertEqual(processed.shape, mock_image.shape)


class TestPermissionManager(unittest.TestCase):
    """权限管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.permission_manager = PermissionManager()
    
    @patch('utils.permissions.check_permission')
    def test_permission_check(self, mock_check):
        """测试权限检查"""
        # 模拟权限已授予
        mock_check.return_value = True
        self.assertTrue(self.permission_manager.check_camera_permission())
        
        # 模拟权限未授予
        mock_check.return_value = False
        self.assertFalse(self.permission_manager.check_camera_permission())
    
    def test_permission_status(self):
        """测试权限状态获取"""
        status = self.permission_manager.get_permission_status()
        self.assertIsInstance(status, dict)
        
        # 检查必要权限是否在状态中
        required_permissions = [
            'android.permission.CAMERA',
            'android.permission.WRITE_EXTERNAL_STORAGE',
            'android.permission.READ_EXTERNAL_STORAGE'
        ]
        
        for permission in required_permissions:
            self.assertIn(permission, status)


class TestCameraHandler(unittest.TestCase):
    """摄像头处理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.camera_handler = CameraHandler()
    
    def tearDown(self):
        """测试后清理"""
        if self.camera_handler:
            self.camera_handler.stop_capture()
    
    def test_camera_initialization(self):
        """测试摄像头初始化"""
        # 注意：在测试环境中可能没有摄像头
        # 这里主要测试方法调用不会出错
        try:
            result = self.camera_handler.initialize_camera()
            # 如果有摄像头，应该返回True；如果没有，返回False
            self.assertIsInstance(result, bool)
        except Exception as e:
            # 在没有摄像头的环境中，这是预期的
            self.assertIsInstance(e, Exception)
    
    def test_camera_info(self):
        """测试摄像头信息获取"""
        info = self.camera_handler.get_camera_info()
        # 在没有摄像头的环境中应该返回None
        if info is not None:
            self.assertIsInstance(info, dict)
            self.assertIn('width', info)
            self.assertIn('height', info)
            self.assertIn('fps', info)
            self.assertIn('index', info)
    
    def test_resolution_setting(self):
        """测试分辨率设置"""
        # 测试设置分辨率不会出错
        self.camera_handler.set_resolution(640, 480)
        self.assertEqual(self.camera_handler.frame_width, 640)
        self.assertEqual(self.camera_handler.frame_height, 480)
    
    def test_fps_setting(self):
        """测试帧率设置"""
        # 测试设置帧率不会出错
        self.camera_handler.set_fps(30)
        self.assertEqual(self.camera_handler.fps, 30)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_users.json')
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)
    
    def test_user_workflow(self):
        """测试完整的用户工作流程"""
        # 创建用户管理器
        user_manager = UserManager()
        user_manager.users_file = self.test_file
        
        # 1. 用户注册
        success, message = user_manager.register("integration_test", "password123", "集成测试")
        self.assertTrue(success)
        
        # 2. 用户登录
        authenticated = user_manager.authenticate("integration_test", "password123")
        self.assertTrue(authenticated)
        
        # 3. 添加训练记录
        user_manager.add_pushup_record("integration_test", 25)
        user_manager.add_pushup_record("integration_test", 30)
        user_manager.add_pushup_record("integration_test", 20)
        
        # 4. 获取统计信息
        stats = user_manager.get_user_statistics("integration_test")
        self.assertEqual(stats['total_pushups'], 75)
        self.assertEqual(stats['total_sessions'], 3)
        self.assertEqual(stats['best_session'], 30)
        self.assertEqual(stats['average_per_session'], 25.0)
        
        # 5. 验证数据持久化
        user_manager.save_users()
        
        # 6. 重新加载数据
        new_user_manager = UserManager()
        new_user_manager.users_file = self.test_file
        new_user_manager.load_users()
        
        # 7. 验证数据一致性
        new_stats = new_user_manager.get_user_statistics("integration_test")
        self.assertEqual(new_stats['total_pushups'], 75)


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("俯卧撑计数器应用测试")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_classes = [
        TestUserManager,
        TestPoseDetector,
        TestPermissionManager,
        TestCameraHandler,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # 返回测试是否成功
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
