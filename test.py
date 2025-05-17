import serial
import time
import threading


class SerialTest:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.stop_event = threading.Event()  # 使用Event对象控制线程
        self.step = 0

    def _send_command(self, command):
        if self.ser.is_open:
            self.ser.write(command.encode())

    def _read_response(self):
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
        time.sleep(0.1)  # 给线程时间处理停止请求
        if self.ser.is_open:
            self.ser.close()
            print("串口已关闭")


class CarMove(SerialTest):
    def __init__(self, port, baudrate):
        super().__init__(port, baudrate)
        self.route_steps = [
            "moving_ahead",
            "ahead_appoint",
            "turn_left",
            "ahead_appoint",
            "moving_ahead"
        ]
        self.stop_flag = False  # 步骤完成标志

    def Turn(self, angle, val):
        command = f"2|{angle}|{val}"
        print(f"发送命令: {command}")
        self._send_command(command)

    def ahead_appoint(self, centimeter, val):
        command = f"3|{centimeter}|{val}"
        print(f"发送命令: {command}")
        self._send_command(command)

    def moving_ahead(self, val):
        command = f"1|{val}|0"
        print(f"发送命令: {command}")
        self._send_command(command)

    def execute_step(self, step_name):
        if step_name == "moving_ahead":
            self.moving_ahead(30)
        elif step_name == "turn_left":
            self.Turn(90, 30)
        elif step_name == "turn_right":
            self.Turn(-90, 30)
        elif step_name == "ahead_appoint":
            self.ahead_appoint(10, 50)

    def execute_route(self):
        """执行完整路由"""
        while self.step < len(self.route_steps) and not self.stop_event.is_set():
            # 重置标志
            self.stop_flag = False

            # 执行当前步骤
            current_step = self.route_steps[self.step]
            print(f"执行步骤 {self.step + 1}/{len(self.route_steps)}: {current_step}")
            self.execute_step(current_step)

            # 等待当前步骤完成或线程被要求停止
            while not self.stop_flag and not self.stop_event.is_set():
                time.sleep(0.1)

            print(f"步骤 {self.step + 1} 完成")
            time.sleep(0.5)  # 步骤间适当延迟

        print("路线执行完成")
        self.execute_step("stop")  # 完成后停止


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