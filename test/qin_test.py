import serial 
import time 
import threading

class SerialTest:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate)
        self.stop_flag = False
    
    def send_command(self,command):
        self.ser.write(command.encode())
    def read_response(self):
        response =self.ser.readline().decode("utf-8").replace("\x00"," ").strip()
        return response
    def ReadStream(self):
        while True:
            response = self.read_response() 
            if response:
                print(f"received:{response}")
                if response == "OK!":
                    print("task over !!!")
                    stop_flag = True    
                time.sleep(0.01)
    def ReadThread(self):
        read_thread = threading.Thread(target=self.ReadStream)
        read_thread.start()
class Carmove(SerialTest):
    def __init__(self, port, baudrate):
        super().__init__(port, baudrate)

    def Turn(self,angle,val):
        command = f"2|{angle}|{val}"
        print(f"send:{command}")
        self.send_command(command)

car =Carmove(port='/dev/ttyUSB0', baudrate=115200)

if __name__ == '__main__':
    car.Turn(-90,20)
    car.ReadStream()