import serial
import threading
import time

class SerialReader:
    def __init__(self, port, baudrate=9600):
        # 初始化串口连接
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=0.1  # 设置超时时间，避免阻塞
        )
        self.running = False
        self.thread = None
        self.buffer = []  # 用于存储接收到的数据

    def start(self):
        # 启动串口读取线程
        self.running = True
        self.thread = threading.Thread(target=self._read_loop)
        self.thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        self.thread.start()

    def stop(self):
        # 停止串口读取
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.ser.close()

    def _read_loop(self):
        # 串口读取循环
        while self.running:
            try:
                if self.ser.in_waiting > 0:  # 检查是否有数据可读
                    data = self.ser.read(self.ser.in_waiting)  # 读取所有可用数据
                    self.buffer.append(data)  # 将数据添加到缓冲区
                    self._process_data(data)  # 处理接收到的数据
                else:
                    time.sleep(0.01)  # 短暂休眠，降低CPU使用率
            except serial.SerialException as e:
                print(f"串口异常: {e}")
                self.running = False
            except Exception as e:
                print(f"读取错误: {e}")
                self.running = False

    def _process_data(self, data):
        # 处理接收到的数据的方法，可根据需求重写
        print(f"收到数据: {data}")

    def get_buffer(self):
        # 获取并清空缓冲区
        temp = self.buffer.copy()
        self.buffer.clear()
        return temp

# 使用示例
if __name__ == "__main__":
    reader = SerialReader(port="COM3", baudrate=115200)
    reader.start()

    try:
        # 主程序可以做其他事情
        while True:
            time.sleep(1)
            # 定期处理缓冲区中的数据
            data = reader.get_buffer()
            if data:
                print(f"主程序处理数据: {data}")
    except KeyboardInterrupt:
        reader.stop()  # 确保程序退出时关闭串口
        print("程序已停止")