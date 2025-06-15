#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摄像头处理模块
处理摄像头初始化、帧捕获等功能
"""

import threading
import time
from kivy.logger import Logger
from kivy.clock import Clock

# 尝试导入OpenCV，如果失败则使用Kivy Camera
try:
    import cv2
    OPENCV_AVAILABLE = True
    Logger.info("CameraHandler: OpenCV available")
except ImportError:
    OPENCV_AVAILABLE = False
    Logger.warning("CameraHandler: OpenCV not available, using Kivy Camera")

# 尝试导入Android相机API
try:
    from android.runnable import run_on_ui_thread
    from jnius import autoclass, PythonJavaClass, java_method
    ANDROID_CAMERA_AVAILABLE = True
    Logger.info("CameraHandler: Android camera API available")
except ImportError:
    ANDROID_CAMERA_AVAILABLE = False
    Logger.info("CameraHandler: Android camera API not available")


class CameraHandler:
    """摄像头处理器"""
    
    def __init__(self, camera_index=0):
        """
        初始化摄像头处理器
        
        Args:
            camera_index: 摄像头索引，默认为0（后置摄像头）
        """
        self.camera_index = camera_index
        self.cap = None
        self.is_running = False
        self.is_paused = False
        self.frame_callback = None
        self.capture_thread = None
        self.current_frame = None
        self.fps = 30
        self.frame_width = 640
        self.frame_height = 480
        
        Logger.info(f"CameraHandler: 初始化摄像头处理器，索引: {camera_index}")
    
    def set_frame_callback(self, callback):
        """
        设置帧回调函数
        
        Args:
            callback: 回调函数，接收frame参数
        """
        self.frame_callback = callback
    
    def initialize_camera(self):
        """初始化摄像头"""
        try:
            # 释放之前的摄像头
            if self.cap is not None:
                self.cap.release()
            
            # 在Android上可能需要特殊处理
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                Logger.error("CameraHandler: 无法打开摄像头")
                return False
            
            # 设置摄像头参数（移动端优化）
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # 获取实际设置的参数
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            Logger.info(f"CameraHandler: 摄像头初始化成功")
            Logger.info(f"CameraHandler: 分辨率: {actual_width}x{actual_height}, FPS: {actual_fps}")
            
            return True
            
        except Exception as e:
            Logger.error(f"CameraHandler: 摄像头初始化失败: {e}")
            return False
    
    def start_capture(self):
        """开始捕获视频帧"""
        if not self.initialize_camera():
            return False
        
        self.is_running = True
        self.is_paused = False
        
        # 启动捕获线程
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
        Logger.info("CameraHandler: 开始视频捕获")
        return True
    
    def stop_capture(self):
        """停止捕获视频帧"""
        self.is_running = False
        
        # 等待线程结束
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
        
        # 释放摄像头
        if self.cap:
            self.cap.release()
            self.cap = None
        
        Logger.info("CameraHandler: 停止视频捕获")
    
    def pause_capture(self):
        """暂停捕获"""
        self.is_paused = True
        Logger.info("CameraHandler: 暂停视频捕获")
    
    def resume_capture(self):
        """恢复捕获"""
        self.is_paused = False
        Logger.info("CameraHandler: 恢复视频捕获")
    
    def _capture_loop(self):
        """视频捕获循环"""
        frame_interval = 1.0 / self.fps
        last_frame_time = 0
        
        while self.is_running:
            try:
                if self.is_paused:
                    time.sleep(0.1)
                    continue
                
                current_time = time.time()
                
                # 控制帧率
                if current_time - last_frame_time < frame_interval:
                    time.sleep(0.01)
                    continue
                
                if self.cap is None or not self.cap.isOpened():
                    Logger.warning("CameraHandler: 摄像头未打开")
                    break
                
                ret, frame = self.cap.read()
                
                if not ret:
                    Logger.warning("CameraHandler: 无法读取帧")
                    continue
                
                # 在Android上可能需要旋转图像
                frame = self._process_frame(frame)
                
                self.current_frame = frame
                last_frame_time = current_time
                
                # 调用回调函数（在主线程中执行）
                if self.frame_callback:
                    Clock.schedule_once(lambda dt: self.frame_callback(frame), 0)
                
            except Exception as e:
                Logger.error(f"CameraHandler: 捕获帧时出错: {e}")
                time.sleep(0.1)
        
        Logger.info("CameraHandler: 捕获循环结束")
    
    def _process_frame(self, frame):
        """
        处理帧（旋转、翻转等）
        
        Args:
            frame: 原始帧
            
        Returns:
            numpy.ndarray: 处理后的帧
        """
        try:
            # 在Android上可能需要旋转图像
            # 这里可以根据设备方向进行调整
            
            # 水平翻转（前置摄像头镜像效果）
            if self.camera_index == 1:  # 前置摄像头
                frame = cv2.flip(frame, 1)
            
            return frame
            
        except Exception as e:
            Logger.error(f"CameraHandler: 处理帧时出错: {e}")
            return frame
    
    def get_current_frame(self):
        """获取当前帧"""
        return self.current_frame
    
    def switch_camera(self):
        """切换前后摄像头"""
        was_running = self.is_running
        
        if was_running:
            self.stop_capture()
        
        # 切换摄像头索引
        self.camera_index = 1 - self.camera_index
        Logger.info(f"CameraHandler: 切换到摄像头 {self.camera_index}")
        
        if was_running:
            self.start_capture()
    
    def set_resolution(self, width, height):
        """
        设置分辨率
        
        Args:
            width: 宽度
            height: 高度
        """
        self.frame_width = width
        self.frame_height = height
        
        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            Logger.info(f"CameraHandler: 设置分辨率为 {width}x{height}")
    
    def set_fps(self, fps):
        """
        设置帧率
        
        Args:
            fps: 目标帧率
        """
        self.fps = fps
        
        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            Logger.info(f"CameraHandler: 设置帧率为 {fps}")
    
    def is_camera_available(self):
        """检查摄像头是否可用"""
        return self.cap is not None and self.cap.isOpened()
    
    def get_camera_info(self):
        """获取摄像头信息"""
        if not self.is_camera_available():
            return None
        
        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': self.cap.get(cv2.CAP_PROP_FPS),
            'index': self.camera_index
        }
