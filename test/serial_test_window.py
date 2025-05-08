import serial

ser=serial.Serial()
ser.BAUDRATES=115200
ser.port="COM8"
ser.open()


def send_data(data):
    ser.write(data.encode('utf-8'))

def read_data():
    data=ser.readline().decode('utf-8')
    return data

def move_ahead():
    send_data("1|60|0")

###根据下位机的指示
##param1:指令类型 1:前进 2:转向
##param2:角度值  负数表示左转，正数表示右转度数
##param3:速度值  范围0-100

def turn_left():
    send_data("2|90|25")

def turn_right():
    send_data("2|-90|25")

def stop():
    send_data("1|0|0")

