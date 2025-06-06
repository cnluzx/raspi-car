from extent import running_thread_event, data_queue ,queue,id_event,start_thread,text_event,detection_event,id_data
import serial
import time
from oled import *


####测试成功，可以实现这个读取功能，新增了防抖功能
"""
串口模块

功能：使用串口发送/接收数据

使用方法：
step1:  ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=115200,
            timeout=1) # 设置串口参数
step2:  seri=Seri()    
step3:  running_thread_event.set()
        start_thread("put_queue_stream",self.put_queue_stream) ###启用读取线程
        start_thread("read_queue_stream",self.read_queue_stream)
        start_thread("id_stream",self.id_stream)                ##启用检查id线程
"""

ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=115200,
        timeout=1)


class Seri:
    def __init__(self):
        self.current_data = None
        self.current_step = "idle" # 给一个初始状态
        self.last_valid_signal = None  # 完整信号去重
        self.debounce_interval = 0.2  # 去重间隔（秒，避免高频重复）
        self.last_debounce_time = time.time()
        
    def read_response(self):
        if not ser or not ser.is_open:
            return None
        try:
            if ser.in_waiting > 0:
                response_bytes = ser.readline()
                if response_bytes:
                    decoded_response = response_bytes.decode("utf-8").strip()
                    
                    # 可选：添加防抖（Debounce）避免高频抖动
                    current_time = time.time()
                    if current_time - self.last_debounce_time < self.debounce_interval:
                        return None  # 短时间内重复读取，忽略
                    self.last_debounce_time = current_time
                    
                    return decoded_response
                return None
            return None
        except Exception as e:
            print(f"读取错误: {e}")
            return None
    def put_queue_stream(self):
        """从串口读取数据并放入队列（独立线程）"""

        print("串口读取线程已启动...")
        while running_thread_event.is_set(): # 使用全局事件控制循环
            if not ser or not ser.is_open:
                print("串口读取线程：串口未连接，线程退出。")
                break
            response = self.read_response()
            if response: # 确保 response 不是 None 或空字符串
                try:
                    data_queue.put(response, timeout=0.1) 

                except queue.Full:
                    print("警告：数据队列已满，数据可能丢失。")
            else:
                time.sleep(0.1)
        print("串口读取线程已停止。")

    def read_queue_stream(self):
        """处理队列中的数据（独立线程）"""
        print("数据处理线程已启动...")
        while running_thread_event.is_set():
            try:
                self.current_data = data_queue.get(timeout=0.2) # 使用超时避免队列空时永久阻塞
                if self.current_data.startswith("#"):
                    print(f"time: {time.strftime('%H:%M:%S')}处理：触发停止信号！")
                
                elif self.current_data.startswith("$"): # 假设检测数据以!开头
                    print(f"time: {time.strftime('%H:%M:%S')}处理：触发检测任务！")
                    detection_event.set()
                    
                elif self.current_data.startswith("40 7F"): # 假设ID数据以@开头
                    print(f"time: {time.strftime('%H:%M。/:%S')}处理：触发识别任务！数据: {self.current_data}")
                    id_data=self.current_data[0:] 
                    id_event.set() 
                else:
                    print(f"time: {time.strftime('%H:%M:%S')}处理：收到未识别数据: {self.current_data}")

                #data_queue.task_done() # 通知队列任务已完成
            except queue.Empty:
                continue # 队列为空，继续等待
            except Exception as e:
                print(f"处理队列数据时出错: {e}")

        print("数据处理线程已停止。")


    
    def id_stream(self):
        """识别任务处理线程 (只保留一个定义)"""
        print("ID处理线程已启动...")
        id_mapping = {
        "07 4F": "1",
        "07 4E": "2",
        "07 4D": "3",
        "07 4C": "4",
        "07 4B": "5",
        "07 4A": "6",
        "07 49": "7",
        "07 48": "8",
        "07 47": "9"
    }
        while running_thread_event.is_set():
            if id_event.wait(timeout=0.5):          ###需要根据这个进行修改
                
                if id_data:
                    print(f"ID处理:识别到数据: {id_data}")
                    if id_data in id_mapping:
                        point = id_mapping[id_data]
                        print(f"ID处理:匹配到 {point}")
                        oled.update_display(f"id:{point}")  # 显示匹配的点
                    else:
                        print(f"ID处理:未识别的ID: {id_data}")
                        oled.update_display("未知ID")
                    # 触发文本显示
           
                else:
                    print("ID处理:id_event触发，但current_data不是预期的ID格式。")
                id_event.clear()  
        print("ID处理线程已停止。")

    def detect_finished(self):
        send_data("5|0|0")
        print("检测任务完成，发送下位机停止命令。")


    def test(self):
        running_thread_event.set()
        start_thread("put_queue_stream",self.put_queue_stream)
        start_thread("read_queue_stream",self.read_queue_stream)
        start_thread("id_stream",self.id_stream)
        if ser and ser.is_open:
            send_data("1|25|0")###step1 发送开始信号！！！！


def send_data(data):
        ser.write(data.encode('utf-8'))

if __name__ == "__main__":
    
    seri=Seri()
    seri.test()
      # 直接发送指令
    oled=Oled()
    while running_thread_event.is_set():
            time.sleep(2)