import serial
import time
import threading
import multiprocessing
import cv2
import numpy as np
import time
import pygame
from collections import Counter
import queue

data_queue = queue.Queue(maxsize=1000)  # 设置队列最大容量
detection_event = threading.Event()
id_event = threading.Event()
stop_event = threading.Event()
running_thread_event = threading.Event()
text_event = threading.Event()
reading_thread= None  # 控制线程运行状态

class Serial:
    def __init__(self, port, baudrate):
        self.current_data = None
        # self.step = 0 
        self.current_step = "idle" # 给一个初始状态
        self.threads = {} # 正确初始化线程字典
        self.id_data = None

        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=0.1) # 减小超时以便更快响应
            print(f"串口 {port} 打开成功，波特率 {baudrate}")
        except serial.SerialException as e:
            print(f"打开串口 {port} 失败: {e}")
            self.ser = None # 标记串口未成功打开
            raise # 重新抛出异常，让调用者知道初始化失败

    def send_command(self, data):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write((data).encode('utf-8'))
                # print(f"已发送: {data}") # 调试用
                time.sleep(0.05) # 发送后短暂延时，给设备处理时间，具体值可能需要调整
            except serial.SerialException as e:
                print(f"串口发送错误: {e}")
            except Exception as e:
                print(f"发送命令时发生未知错误: {e}")
        else:
            print("串口未打开或未初始化，无法发送命令。")

    def read_response(self):
        if not self.ser or not self.ser.is_open:
            return None
        try:
            if self.ser.in_waiting > 0: # 检查是否有等待读取的数据
                response_bytes = self.ser.readline() # 读取一行数据
                if response_bytes:
                    # 解码并去除首尾空白及可能存在的空字节
                    decoded_response = response_bytes.decode("utf-8", errors='ignore').strip()
                    # print(f"原始读取: {decoded_response}") # 调试用
                    return decoded_response
            return None # 超时或没有读到数据
        except serial.SerialException as e:
            print(f"串口读取错误 (SerialException): {e}")
            return None
        except Exception as e:
            print(f"串口读取时发生未知错误: {e}")
            return None

    def put_queue_stream(self):
        """从串口读取数据并放入队列（独立线程）"""
        print("串口读取线程已启动...")
        while running_thread_event.is_set(): # 使用全局事件控制循环
            if not self.ser or not self.ser.is_open:
                print("串口读取线程：串口未连接，线程退出。")
                break
            response = self.read_response()
            if response: # 确保 response 不是 None 或空字符串
                try:
                    data_queue.put(response, timeout=0.1) 

                except queue.Full:
                    print("警告：数据队列已满，数据可能丢失。")
            else:
                time.sleep(0.01)
        print("串口读取线程已停止。")

    def read_queue_stream(self):
        """处理队列中的数据（独立线程）"""
        print("数据处理线程已启动...")
        while running_thread_event.is_set():
            try:
                self.current_data = data_queue.get(timeout=0.1) # 使用超时避免队列空时永久阻塞

                # CarMove 类可能会重写此方法以加入更具体的逻辑
                if self.current_data.startswith("#"):
                    print("处理：触发停止信号！")
                    stop_event.set()
                # 注意: self.current_step 的值需要被正确管理
                elif self.current_data.startswith("STOP OVER!"):
                    print("处理：触发检测任务！")
                    detection_event.set()

                elif self.current_data.startswith("@"): # 假设ID数据以@开头
                    print(f"处理：触发识别任务！数据: {self.current_data}")
                    self.id_data=self.current_data[1:] # 去掉@符号
                    id_event.set() # 通知 id_stream 处理
                else:
                    print(f"处理：收到未识别数据: {self.current_data}")

                #data_queue.task_done() # 通知队列任务已完成
            except queue.Empty:
                continue # 队列为空，继续等待
            except Exception as e:
                print(f"处理队列数据时出错: {e}")

        print("数据处理线程已停止。")

    def id_stream(self):
        """识别任务处理线程 (只保留一个定义)"""
        print("ID处理线程已启动...")
        while running_thread_event.is_set():
            if id_event.wait(timeout=0.5):  # 等待事件触发，带超时
                if self.id_data:
                    print(f"ID处理:识别到数据: {self.id_data}")
                    # 在这里执行具体的识别逻辑...
                else:
                    print("ID处理:id_event触发，但current_data不是预期的ID格式。")
                id_event.clear()  # 重置事件，以便下次可以再次触发
        print("ID处理线程已停止。")

    def start_all_threads(self):
        if not self.ser or not self.ser.is_open:
            print("无法启动线程：串口未初始化或打开失败。")
            return

        running_thread_event.set() # 先设置运行标志

        self.threads["reader"] = threading.Thread(target=self.put_queue_stream, daemon=True)
        self.threads["processor"] = threading.Thread(target=self.read_queue_stream, daemon=True)
        self.threads["id_handler"] = threading.Thread(target=self.id_stream, daemon=True)

        self.threads["reader"].start()
        self.threads["processor"].start()
        self.threads["id_handler"].start()

        print("所有串口相关线程已启动。")

    def stop_all_threads(self):
        print("正在停止所有串口相关线程...")
        running_thread_event.clear() # 清除运行标志，通知所有线程退出循环

        # 等待所有线程结束
        for name, thread_obj in self.threads.items():
            if thread_obj.is_alive():
                print(f"等待线程 {name} 结束...")
                thread_obj.join(timeout=1.0) # 给1秒超时
                if thread_obj.is_alive():
                    print(f"警告：线程 {name} 未能在超时内结束。")
        
        self.threads.clear()

        if self.ser and self.ser.is_open:
            self.ser.close()
            print("串口已关闭。")
        print("所有串口相关线程已停止，串口已关闭。")

class Oled:###finished

    """OLED luma 驱动库测试程序
    功能：显示 test 和矩形外框持续3秒 
    调用方法:show_test(行1,行2,行3)
    """
   
    def __init__(self):
        from luma.core.interface.serial import i2c, spi
        from luma.core.render import canvas
        from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
        from time import sleep
        self.canvas = canvas
        self.serial = i2c(port=1, address=0x3C)# 初始化端口
        self.device_module = {'ssd1306': ssd1306}
        self.device = self.device_module['ssd1306'](self.serial)
    # 调用显示函数
    def show_text(self,t1=None,t2=None,t3=None):
        with self.canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="white", fill="black")
            draw.text((10, 10), str(t1), fill="white")
            draw.text((10, 20), str(t2), fill="white")
            draw.text((10, 30), str(t3), fill="white")
        time.sleep(3)# 延时显示3s
        self.device.command(0xAE) # 关闭显示

    def threading_text(self,t1,t2,t3):
        while running_thread_event.is_set():
            if text_event.is_set():
                self.show_text(t1,t2,t3)  
                text_event.clear() 

class Pan:

    """云台转动设置
    功能:设置云台角度,实现左右转动摄像头识别
    调用方法:pan_left()左转  pan_right()右转  pan_center() 返回中心
    """
    def __init__(self):
        import RPi.GPIO as GPIO
        self.GPIO= GPIO
        self.pin_1= 18   
        self.pin_2 =13
        self.pin_light= 4 
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_1,GPIO.OUT)
        GPIO.setup(self.pin_2,GPIO.OUT)
        GPIO.setup(self.pin_light,GPIO.OUT)

    def light_on(self):###补光灯可省略，直接使用现有供电
        self.GPIO.output(self.pin_light,self.GPIO.HIGH)

    def set_angle(self,pin,angle):
        pwm=self.GPIO.PWM(pin,50)
        pwm.start(0)
        duty=2+angle/18
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)
        pwm.stop()

    def pan_left(self,angle=120):
        self.set_angle(self.pin_1,0)
        self.set_angle(self.pin_2,angle)

    def pan_right(self,angle=120):
        self.set_angle(self.pin_1,170)
        self.set_angle(self.pin_2,angle)

    def pan_center(self,angle=120):
        self.set_angle(self.pin_1,90)
        self.set_angle(self.pin_2,angle)
    
    def test(self):
        self.pan_left()
        time.sleep(2)
        self.pan_right()
        time.sleep(2)
        self.pan_center()
        time.sleep(2)


class CarMove(Serial):
    def __init__(self, port, baudrate):
        super().__init__(port, baudrate)
        self.paused_step = 0
        self.route_steps = [
            "ahead", "left", 
            "ahead", "right",
            "ahead", "right",
            "ahead", "right",
            "ahead", "right", 
            "ahead", "left",
            "ahead", "left", "ahead"
        ]###跑图动作组

    def turn(self, angle, val):
        command = f"2|{angle}|{val}"
        self.send_command(command)

    def ahead_appoint(self, centimeter, val):###走指定距离，可以留着备用
        command = f"3|{centimeter}|{val}"
        self.send_command(command)

    def ahead(self, val=40):
        command = f"1|{val}|0"
        self.send_command(command)

    def stop(self):
        command = "4|0|0"
        self.send_command(command)

    def execute_step(self,step_name):
        if   step_name == "ahead":
            self.ahead(50)
        elif step_name == "left" :
            self.turn(90, 50)
        elif step_name == "right":
            self.turn(-90, 50)
        elif step_name == "stop":
            self.stop()
        else:
            print(f"未知步骤: {step_name}")

    def execute_route(self):
        if not (self.ser and self.ser.is_open):
            print("CarMove: 无法执行路径，串口未连接。")
            return

        print(f"CarMove: 开始执行路径，共 {len(self.route_steps)} 个步骤。")
        self.current_step = 0 # 从路径的第一个步骤开始

        while self.current_step < len(self.route_steps) and running_thread_event.is_set():
            current_step_name = self.route_steps[self.current_step]
            print(f"\n--- 路径步骤 {self.current_step + 1}/{len(self.route_steps)}: {current_step_name} ---")

            # 执行当前步骤的动作
            if not self.execute_step(current_step_name):
                print(f"CarMove: 执行步骤 '{current_step_name}' 失败，路径终止。")
                break
            print(f"CarMove: 等待步骤 '{current_step_name}' 完成信号 (stop_event)...")


            while running_thread_event.is_set():

                if stop_event.wait(timeout=0.1): # 等待 stop_event，带超时
                    print(f"CarMove: 收到步骤 '{current_step_name}' 完成信号 (stop_event)。")
                    stop_event.clear()  
                    self.current_step += 1 # 移动到路径中的下一个步骤
                    break # 跳出内部的等待循环，进入下一个路径步骤

            else: # 如果 running_thread_event 被清除了 (外部循环的条件)
                print("CarMove: 路径执行被外部中断 (running_thread_event cleared)。")
                break 

            time.sleep(0.5)

        if self.current_step >= len(self.route_steps):
            print("CarMove: 路径所有步骤执行完毕。")
        elif not running_thread_event.is_set():
            print("CarMove: 路径执行因程序关闭而中止。")



class Boardcast():
    def __init__(self):
       pygame.mixer.init()

    def test():
        pygame.mixer.music.load("Yellow.mp3")    # 播放音乐
        pygame.mixer.music.play()           
        while pygame.mixer.music.get_busy():# 等待音乐播放完毕
            pygame.time.Clock().tick(1)   

class Detect:
    
    def __init__(self):

        self.if_shape_test =True
        self.if_color_test = True

        self.contours = None
        self.img_two = None
        self.img_blur   = None

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        ###可调参
        self._threshold = 70        ###二值化初始阈值
        self.area_min   = 10000     ###cnt面积阈值
        self.ROI_range = 50         ###图像ROI范围
        self.canny_threshold1 = 50  ###canny初始阈值1
        self.canny_threshold2 = 100 ###canny初始阈值2
        self.rectangle_thresh = 66  ###矩形阈值
        self.square_thresh = 38     ###正方形阈值

        ###颜色
        self.red_low     = (0, 0, 100)
        self.red_up      = (50, 50, 255)  # 调阈值
        self.blue_low    = (100, 0, 0)
        self.blue_up     = (255, 50, 50)
        self.yellow_low  = (20, 100, 100)  # 添加黄色阈值
        self.yellow_up   = (30, 255, 255)   # 添加黄色阈值

        self.red_iter = 1
        self.blue_iter = 1
        self.yellow_iter = 1  # 添加黄色迭代次数

    def process(self,img):
        
        """
        处理图像
        # 转换为灰度图
        # # 中值滤波
        # # # 动态调整二值化阈值
        # # # # 二值化
        # # # # # Canny边缘检测
        # # # # # # 形态学操作(膨胀和腐蚀)
        """

        self.img_blur = cv2.GaussianBlur(img, (5, 5), 1)
        img_gray = cv2.cvtColor(self.img_blur, cv2.COLOR_BGR2GRAY)

        self._threshold += 2
        if self._threshold > 170:
            self._threshold = 70
        _, self.img_two = cv2.threshold(img_gray, self._threshold, 255, cv2.THRESH_BINARY_INV)

        img_canny = cv2.Canny(self.img_two, self.canny_threshold1, self.canny_threshold2)
        kernel = np.ones((5, 5))
        img_dilate = cv2.dilate(img_canny, kernel, iterations=1)
        img_erode = cv2.erode(img_dilate, kernel, iterations=1)
        img_gradient = cv2.morphologyEx(img_erode, cv2.MORPH_GRADIENT, np.ones((3, 3)))

        if self.if_shape_test:
            cv2.imshow("Gray", img_gray)
            cv2.imshow("img_two", self.img_two)
            cv2.imshow("img_Contours", img_gradient)

        self.contours, _ = cv2.findContours(img_gradient, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    def shape_detect(self):

        """
        形状识别
        """

        for cnt in self.contours:
            area = cv2.contourArea(cnt)
            if area > self.area_min:
                perimeter = cv2.arcLength(cnt, True)   ###周长
                approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)###多边形顶点
        #    A
        #   / \
        #  B---C
            if len(approx) == 3:
                shape_type = "Triangle"
                center_x, center_y = self.Centroid(cnt)
                print(f"三角形中心: ({center_x}, {center_y})")
                pts = approx.squeeze()  # 形状应为(3,2)
                A = pts[0]  # 第一个顶点 [x0,y0]
                B = pts[1]  # 第二个顶点 [x1,y1]
                C = pts[2]  # 第三个顶点 [x2,y2]
                y_coords = pts[:, 1]    # 所有y坐标
                sorted_idx = np.argsort(y_coords)  # 按y坐标升序排序的索引
                top_point = pts[sorted_idx[0]]  # y最小的点
                bottom_point = pts[sorted_idx[2]] # y最大的点 好像没用到

                if y_coords[0] < y_coords[1] and y_coords[0] < y_coords[2]:
                    shape_type = "上三角"  # 有一个顶点明显在上方
                    hollow, color = self.color_detect(self.img_blur, center_x, center_y, int(top_point[0]), int(top_point[1]))
                elif y_coords[0] > y_coords[1] and y_coords[0] > y_coords[2]:
                    shape_type = "下三角"  # 有一个顶点明显在下方
                    hollow, color = self.color_detect(self.img_blur, center_x, center_y, int(bottom_point[0]), int(bottom_point[1]))
                else:
                        shape_type = "其他三角形"
            elif len(approx) == 4:
                shape_type = "Rectangle"
                x, y, w, h = cv2.boundingRect(approx)
                center_x, center_y = self.Centroid(cnt)
                approx = np.array(approx).squeeze()
                sorted_points = approx[np.argsort(approx[:, 1])]
    # A —— B
    # |    |
    # D —— C
                if sorted_points[0][0] <= sorted_points[1][0]:
                    A = sorted_points[0]
                    B = sorted_points[1]
                else:
                    A = sorted_points[1]
                    B = sorted_points[0]
                if sorted_points[2][0] <= sorted_points[3][0]:
                    D = sorted_points[2]
                    C = sorted_points[3]
                else:
                    D = sorted_points[3]
                    C = sorted_points[2]

                AB = int(np.sqrt((A[0]-B[0])**2 + (A[1]-B[1])**2))
                CD = int(np.sqrt((C[0]-D[0])**2 + (C[1]-D[1])**2))
                AC = int(np.sqrt((A[0]-C[0])**2 + (A[1]-C[1])**2))
                AD = int(np.sqrt((A[0]-D[0])**2 + (A[1]-D[1])**2))

                angle_AB_CD = np.abs(np.arctan2(B[1]-A[1], B[0]-A[0]) - np.arctan2(C[1]-D[1], C[0]-D[0]))
                angle_AB_AD = np.abs(np.arctan2(B[1]-A[1], B[0]-A[0]) - np.arctan2(D[1]-A[1], D[0]-A[0]))

                if AB - AD > self.rectangle_thresh and CD - AD > self.rectangle_thresh:
                    shape_type = "矩形"
                elif angle_AB_CD < np.pi/18 and angle_AB_AD >np.pi/1.8:
                    shape_type = "上梯形"
                elif angle_AB_CD < np.pi/18 and angle_AB_AD < np.pi/2.25 :
                    shape_type = "下梯形"
                elif AB - AC <= self.square_thresh and CD - AD <= self.square_thresh:
                    shape_type = "正方形"
                else:
                    shape_type = "其他四边形"

                return x,y,center_x,center_y,shape_type, hollow, color
                            
            else:
                shape_type = "Circle"
        if self.if_shape_test:
            print(A,B,C,D)
            print(angle_AB_AD*180/np.pi,angle_AB_CD*180/np.pi)
            print(f"检测到形状: {shape_type}, AB={AB:.1f}, CD={CD:.1f}, AC={AC:.1f}, AD={AD:.1f}")

    def color_detect(self, img, center_x, center_y, x, y):
        """颜色处理函数"""
        hollow = None
        color = None
        
        ROI_img = self.img_two[center_y-self.ROI_range:center_y+self.ROI_range, center_x-self.ROI_range:center_x+self.ROI_range]
        
        white_count = cv2.countNonZero(ROI_img)  
        black_count = ROI_img.size - white_count
        color_counts = { "black": black_count, "white": white_count}
        max_color = max(color_counts, key=color_counts.get)

        ROI_img_color=img[center_y-self.ROI_range:center_y+self.ROI_range, center_x-self.ROI_range:center_x+self.ROI_range]

        red_mask = cv2.inRange(ROI_img_color, self.red_low, self.red_up)
        red_mask = cv2.erode(red_mask, None, iterations=self.red_iter)
        red_mask = cv2.dilate(red_mask, None, iterations=self.red_iter)
        red_count = cv2.countNonZero(red_mask)

        blue_mask = cv2.inRange(ROI_img_color, self.blue_low, self.blue_up)
        blue_mask = cv2.erode(blue_mask, None, iterations=self.blue_iter)
        blue_mask = cv2.dilate(blue_mask, None, iterations=self.blue_iter)
        blue_count = cv2.countNonZero(blue_mask)

        # 添加黄色检测
        yellow_mask = cv2.inRange(ROI_img_color, self.yellow_low, self.yellow_up)
        yellow_mask = cv2.erode(yellow_mask, None, iterations=self.yellow_iter)
        yellow_mask = cv2.dilate(yellow_mask, None, iterations=self.yellow_iter)
        yellow_count = cv2.countNonZero(yellow_mask)

        edge_color_counts = {"red": red_count, "blue": blue_count, "yellow": yellow_count}

        max_edge_color = max(edge_color_counts, key=edge_color_counts.get)
        print(f"边缘检测到颜色: {max_edge_color}")

        if max_color == "black":
            hollow = 2
            print("空心")
            if max_edge_color == "red":
                color = 1
            elif max_edge_color == "blue":
                color = 2
            elif max_edge_color == "yellow":
                color = 3
        else:
            hollow = 1
            print("实心")
            if max_edge_color == "red":
                color = 1
            elif max_edge_color == "blue":
                color = 2
            elif max_edge_color == "yellow":
                color = 3

        if self.if_color_test:
            cv2.imshow("ROI", ROI_img)
        return hollow, color

    def counter(self,img):
        """连续二值化检测最有可能的形状"""
        most_common_shape=None
        most_common_hollow=None
        most_common_color=None
        shape_zip = []
        hollow_zip = []
        color_zip = []
        i = 0

        while i < 37:
            x,y,center_x,center_y,shape, hollow, color = self.shape_detect(img)
            hollow, color = self.color_detect(self.img_blur, center_x, center_y, x, y)
            if None not in (shape):
                shape_zip.append((shape))
            if None not in (hollow):
                hollow_zip.append((hollow))
            if None not in (color):
                color_zip.append((color))
                print(f"第{i+1}次检测 - 形状: {shape}, 空心: {hollow}, 颜色: {color}")
            i += 1
            time.sleep(0.1)  # 调整到循环末尾
            
            if shape_zip != []:
                most_common_shape = Counter(shape_zip).most_common(1)[0][0]
                most_common_hollow = Counter(hollow_zip).most_common(1)[0][0]
                most_common_color = Counter(color_zip).most_common(1)[0][0]

                if most_common_shape == "矩形":
                    if most_common_hollow == 1:
                        Shape = 1
                    elif most_common_hollow == 2:
                        Shape = 2
                elif most_common_shape == "上梯形":
                    if most_common_hollow == 1:
                        Shape = 3
                    elif most_common_hollow == 2:
                        Shape = 4
                elif most_common_shape == "下梯形":
                    if most_common_hollow == 1:
                        Shape = 5
                    elif most_common_hollow == 2:
                        Shape = 6
                elif most_common_shape == "正方形":
                    if most_common_hollow == 1:
                        Shape = 7
                    elif most_common_hollow == 2:
                        Shape = 8
                else:
                    Shape = None

                print(f"最终的形状: {most_common_shape}, 最终的空心: {most_common_hollow}, 最终的颜色: {most_common_color}")
                print(f"最终确定的形状代号: {Shape}")
                return True,most_common_shape,most_common_hollow,most_common_color
            else:
                print("没有检测到有效的形状和颜色")
                return False,None,None,None 
            
    def capture_frame_save(self):#####保存一帧frame功能实现

        self.cap = cv2.VideoCapture(0)  # 创建 VideoCapture 对象，参数为摄像头索引   
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if self.cap.isOpened():  
            print("摄像头已打开")
            ret, frame = self.cap.read()  # 从摄像头读取一帧图像
            cv2.imwrite("Frame.jpg", frame)  
            cv2.imshow("Frame", frame)  # 显示图像
            cv2.waitKey(1)  
    
        self.cap.release()  # 释放摄像头资源
        cv2.destroyAllWindows()  # 销毁所有窗口
        return ret,frame

    def Centroid(cnt):
        """计算轮廓的质心"""
        mu = cv2.moments(cnt)
        if mu["m00"] != 0:
            center_x_mu = int(mu["m10"] / mu["m00"]) if mu["m00"] != 0 else 0
            center_y_mu = int(mu["m01"] / mu["m00"]) if mu["m00"] != 0 else 0
        return center_x_mu, center_y_mu

    def main(self):     ###保存一帧frame并进行检测
        ret,frame=self.capture_frame_save()
        time.sleep(1)   
        if ret:         ###感觉有点重复了
            ret_detect,shape,hollow,color=self.counter(frame)
            if ret_detect:
                return True,shape,hollow,color
            else:
                return False,None,None,None
        else:
            print("没有保存成功")




if __name__ == "__main__":
    SERIAL_PORT = '/dev/ttyUSB0'
    BAUD_RATE = 115200

    print("程序启动...")
    car = None

    # running_thread_event 应该在程序开始时设置，在结束时清除
    running_thread_event.set() # 设置全局运行标志

    try:
        car = CarMove(SERIAL_PORT, BAUD_RATE)
        car.start_all_threads() # 启动串口读写和ID处理等后台线程
        time.sleep(0.5) # 给后台线程一点启动时间

        print("准备在主线程中开始执行路径...")
        if car.ser and car.ser.is_open: # 确保串口已成功打开
            car.execute_route() # 直接在主线程调用，会阻塞直到完成或中断
            print("路径执行结束或被中断。")
        else:
            print("串口未成功打开，无法执行路径。")

        # 路径执行完毕后，主线程可以继续做其他事情，或者准备退出
        # 如果路径执行是程序的唯一主要任务，执行完毕后可以考虑停止所有线程并退出
        print("路径执行完毕，准备关闭程序...")
        running_thread_event.clear() # 发出停止信号给所有后台线程

    except serial.SerialException:
        print(f"无法初始化车辆控制：串口 {SERIAL_PORT} 存在问题。程序退出。")
        running_thread_event.clear() # 发生严重错误，也应尝试停止后台线程
    except KeyboardInterrupt:
        print("\n接收到 Ctrl+C, 程序准备退出...")
        running_thread_event.clear() # 用户中断，发出停止信号
    except Exception as e:
        print(f"发生未预料的错误: {e}")
        running_thread_event.clear() # 未知错误，也应尝试停止后台线程
    finally:
        # 确保 running_thread_event 在 finally 块之前已经被 clear()
        # 如果没有，可以在这里再次 clear()，但通常在 except 块中处理更好
        # running_thread_event.clear() # 确保所有线程都会收到停止信号

        print("正在执行清理操作...")
        if car:
            # 如果 execute_route 是因为 KeyboardInterrupt 中断的，
            # car 对象可能还在，需要停止其后台线程
            car.stop_all_threads() # 这个方法内部会等待线程结束并关闭串口
        else:
            # 如果 car 初始化失败，running_thread_event 可能仍然是 set 状态
            # 但由于没有 car 对象，也就没有 car.stop_all_threads() 可调用
            # 不过，如果后台线程（如OLED、Pan的线程）也依赖 running_thread_event，
            # 它们会因为 running_thread_event.clear() 而停止。
            pass

        print("程序已退出。")

