import serial
import time
import threading
import oled
####已完成，无问题的模块会打######

####使用到的标志位:stop_flag 停止标志位
####detection_triggered 检测任务触发标志
####detection_completed 检测任务完成标志

###重要的参数：current_step 当前执行的步骤
###
class SerialTest:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.stop_event = threading.Event()  # 使用Event对象控制线程
        self.step = 0
        self.detection_triggered = threading.Event()  # 检测任务触发标志
        self.detection_completed = threading.Event()  # 检测任务完成标志
        self.current_step = None  # 记录当前执行的步骤

    def _send_command(self, command):######
        if self.ser.is_open:
            self.ser.write(command.encode())

    def _read_response(self):#########
        try:
            if self.ser.is_open:
                response = self.ser.readline()
                if response:  # 检查是否有数据返回
                    return response.decode("utf-8").replace("\x00", "").strip()
            return None
        except Exception as e:
            print(f"串口读取错误: {e}")
            return None

    def ReadStream(self):
        while not self.stop_event.is_set():
            try:
                response = self._read_response()
                if response:
                    print(f"收到响应: {response}")
                    if response == "#":
                        self.step += 1
                        print(f"当前步骤: {self.step}")
                        self.stop_flag = True
                    elif response == "!" and self.current_step == "moving_ahead":
                        # 当检测到!且当前正在直走时，触发检测任务
                        print("触发检测任务！")
                        self.detection_triggered.set()
                time.sleep(0.01)
            except Exception as e:
                print(f"读取线程异常: {e}")
                time.sleep(0.5)  # 发生异常时暂停一段时间

    def ReadThread(self):
        read_thread = threading.Thread(target=self.ReadStream)
        read_thread.daemon = True
        read_thread.start()
        return read_thread  # 返回线程对象以便后续操作

    def close(self):
        """安全关闭串口和线程"""
        self.stop_event.set()  # 通知线程停止
        self.detection_triggered.set()  # 确保不会阻塞
        self.detection_completed.set()  # 确保不会阻塞
        time.sleep(0.1)  # 给线程时间处理停止请求
        if self.ser.is_open:
            self.ser.close()
            print("串口已关闭")

class CarMove(SerialTest):######继承于SerialTest类 

    def __init__(self, port, baudrate):
        super().__init__(port, baudrate)
        self.route_steps = [
            "moving_ahead", "turn_left", "moving_ahead", "turn_right",
            "moving_ahead", "turn_right", "moving_ahead", "turn_right",
            "moving_ahead", "turn_right", "moving_ahead", "turn_left",
            "moving_ahead", "turn_left", "moving_ahead"
        ]
        self.stop_flag = False  # 步骤完成标志
        self.detection_paused_step = None  # 记录检测任务暂停时的步骤

    def Turn(self, angle, val):######
        command = f"2|{angle}|{val}"
        print(f"发送命令: {command}")
        self._send_command(command)
    
    def ahead_appoint(self, centimeter, val):##########
        command = f"3|{centimeter}|{val}"
        print(f"发送命令: {command}")
        self._send_command(command)

    def moving_ahead(self, val):######
        command = f"1|{val}|0"
        print(f"发送命令: {command}")
        self._send_command(command)

    def stop(self):
        """停止所有运动"""
        command = "4|0|0"
        print(f"发送命令: {command}")
        self._send_command(command)

    def execute_step(self, step_name):#######动作组拆解翻译指令
        self.current_step = step_name
        print(f"执行动作: {step_name}")
        if step_name == "moving_ahead":
            self.moving_ahead(40)
        elif step_name == "turn_left":
            self.Turn(90, 25)
        elif step_name == "turn_right":
            self.Turn(-90, 25)
        elif step_name == "ahead_appoint":
            self.ahead_appoint(10, 50)
        elif step_name == "stop":
            self.stop()

    def perform_detection(self):
        """执行检测任务"""


    def execute_route(self):
        """执行完整路由，支持检测任务中断和恢复"""
        print(f"开始执行路由，共 {len(self.route_steps)} 个步骤")
        
        while self.step < len(self.route_steps) and not self.stop_event.is_set():
            # 重置标志
            self.stop_flag = False
            self.detection_triggered.clear()
            self.detection_completed.clear()
            
            # 执行当前步骤
            current_step = self.route_steps[self.step]
            print(f"执行步骤 {self.step + 1}/{len(self.route_steps)}: {current_step}")
            self.execute_step(current_step)
            
            # 等待当前步骤完成或检测任务触发
            while not self.stop_flag and not self.detection_triggered.is_set() and not self.stop_event.is_set():
                time.sleep(0.1)
            
            # 检查是否因检测任务触发而中断
            if self.detection_triggered.is_set():
                print(f"步骤 {self.step + 1} 被检测任务中断")
                self.detection_paused_step = self.step  # 记录暂停的步骤
                
                # 执行检测任务（在单独线程中执行，避免阻塞主程序）
                detection_thread = threading.Thread(target=self.perform_detection)
                detection_thread.daemon = True
                detection_thread.start()
                
                # 等待检测任务完成
                self.detection_completed.wait()
                
                # 恢复被中断的步骤
                print(f"恢复执行步骤 {self.step + 1}/{len(self.route_steps)}: {current_step}")
                self.execute_step(current_step)
                self.detection_triggered.clear()  # 重置触发标志
            
            # 步骤完成
            print(f"步骤 {self.step + 1} 完成")
            time.sleep(0.5)  # 步骤间适当延迟
            self.step += 1
        
        print("路线执行完成")
        self.execute_step("stop")  # 确保停止

if __name__ == "__main__":
    car = None
    try:
        car = CarMove('/dev/ttyUSB0', 115200)
        read_thread = car.ReadThread()  # 启动读取线程
        car.execute_route()  # 执行完整路由
        
        # 等待路由执行完成或用户中断
        while read_thread.is_alive() and car.step < len(car.route_steps):
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    finally:
        if car:
            car.close()  # 关闭串口和线程    