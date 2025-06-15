#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
姿态检测模块
移植自原项目的sprot2.py，适配移动端使用
"""

import cv2
import mediapipe as mp
import numpy as np
import threading
import time
from kivy.logger import Logger
from kivy.clock import Clock


class PoseDetector:
    """俯卧撑姿态检测器"""
    
    def __init__(self, callback=None):
        """
        初始化姿态检测器
        
        Args:
            callback: 检测结果回调函数，接收(frame, counter, stage, arm_angle, leg_angle)
        """
        # MediaPipe初始化
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 计数相关变量
        self.counter = 0
        self.stage = None
        
        # 角度阈值（移动端优化后的参数）
        self.max_angle = 160      # 完成俯卧撑的最大角度
        self.min_angle = 80       # 准备开始俯卧撑的最小角度
        self.max_leg_angle = 160  # 腿部最大角度
        self.min_leg_angle = 150  # 腿部最小角度
        
        # 性能优化参数
        self.process_interval = 3  # 每3帧处理一次（移动端优化）
        self.frame_count = 0
        
        # 回调函数
        self.callback = callback
        
        # 控制变量
        self.is_running = False
        self.is_paused = False
        
        Logger.info("PoseDetector: 姿态检测器初始化完成")
    
    def calculate_angle(self, a, b, c):
        """
        计算三点之间的角度
        
        Args:
            a, b, c: 三个点的坐标 [x, y]
            
        Returns:
            float: 角度值（度）
        """
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        # 计算两个向量的角度差（弧度）
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        
        # 转换为角度（度）
        angle = np.abs(radians * 180.0 / np.pi)
        
        # 确保角度在0到360度之间
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def deblur_image(self, img):
        """
        去模糊处理（移动端简化版本）
        
        Args:
            img: 输入图像
            
        Returns:
            numpy.ndarray: 处理后的图像
        """
        try:
            # 简化的去模糊处理，减少计算量
            img_gas = cv2.GaussianBlur(img, (3, 3), 1.0)  # 减少模糊强度
            return img_gas
        except Exception as e:
            Logger.warning(f"PoseDetector: 去模糊处理失败: {e}")
            return img
    
    def histogram_equalization(self, image):
        """
        直方图均衡化
        
        Args:
            image: RGB图像
            
        Returns:
            numpy.ndarray: 均衡化后的图像
        """
        try:
            # RGB转HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            # 对亮度通道（V）进行直方图均衡化
            hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])
            # HSV转RGB
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        except Exception as e:
            Logger.warning(f"PoseDetector: 直方图均衡化失败: {e}")
            return image
    
    def process_frame(self, frame):
        """
        处理单帧图像
        
        Args:
            frame: 输入帧
            
        Returns:
            tuple: (处理后的帧, 是否检测到姿态)
        """
        if frame is None:
            return None, False
        
        # 降低分辨率以提高处理速度（移动端优化）
        height, width = frame.shape[:2]
        if width > 640:
            scale = 640 / width
            new_width = 640
            new_height = int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))
        
        # 每隔一定帧数处理一次
        self.frame_count += 1
        if self.frame_count % self.process_interval != 0:
            return frame, False
        
        try:
            # 图像预处理（简化版本）
            processed_frame = self.deblur_image(frame)
            
            # BGR转RGB
            image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            
            # 直方图均衡化
            image = self.histogram_equalization(image)
            
            image.flags.writeable = False
            
            # MediaPipe姿态检测
            results = self.pose.process(image)
            
            # 转回BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # 处理检测结果
            pose_detected = False
            arm_angle = 0
            leg_angle = 0
            
            if results.pose_landmarks:
                pose_detected = True
                landmarks = results.pose_landmarks.landmark
                
                # 获取关键点坐标
                shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                           landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                
                hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                       landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                
                # 计算角度
                arm_angle = self.calculate_angle(shoulder, elbow, wrist)
                leg_angle = self.calculate_angle(hip, knee, ankle)
                
                # 俯卧撑计数逻辑
                if arm_angle > self.max_angle and leg_angle > 160:
                    self.stage = "down"
                    Logger.debug(f"PoseDetector: Down - Arm: {arm_angle:.1f}°, Leg: {leg_angle:.1f}°")
                
                if arm_angle < self.min_angle and leg_angle < 180 and self.stage == 'down':
                    self.stage = "up"
                    self.counter += 1
                    Logger.info(f"PoseDetector: Up - Counter: {self.counter}")
                
                # 绘制关键点和连接线
                self.mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                )
                
                # 在图像上显示信息
                self._draw_info(image, arm_angle, leg_angle)
            
            # 调用回调函数
            if self.callback:
                self.callback(image, self.counter, self.stage, arm_angle, leg_angle)
            
            return image, pose_detected
            
        except Exception as e:
            Logger.error(f"PoseDetector: 处理帧时出错: {e}")
            return frame, False
    
    def _draw_info(self, image, arm_angle, leg_angle):
        """在图像上绘制信息"""
        height, width = image.shape[:2]
        
        # 绘制背景矩形
        cv2.rectangle(image, (0, 0), (width, 80), (245, 117, 16), -1)
        
        # 显示计数
        cv2.putText(image, 'COUNT', (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(image, str(self.counter), (10, 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
        
        # 显示阶段
        cv2.putText(image, 'STAGE', (120, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(image, self.stage if self.stage else "", (120, 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        # 显示角度（如果屏幕够宽）
        if width > 400:
            cv2.putText(image, f'ARM: {arm_angle:.0f}°', (250, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, f'LEG: {leg_angle:.0f}°', (250, 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    
    def reset_counter(self):
        """重置计数器"""
        self.counter = 0
        self.stage = None
        Logger.info("PoseDetector: 计数器已重置")
    
    def get_counter(self):
        """获取当前计数"""
        return self.counter
    
    def get_stage(self):
        """获取当前阶段"""
        return self.stage
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'pose'):
            self.pose.close()
        Logger.info("PoseDetector: 资源已清理")
