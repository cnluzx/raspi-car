import serial

ser=serial.Serial()
ser.BAUDRATES=115200
ser.port="/dev/ttyUSB0"
ser.open()


def send_data(data):
    ser.write(data.encode('utf-8'))

def read_data():
    data=ser.readline().decode('utf-8')
    return data

def move_ahead():
    send_data("1|60|0")


def turn_left():
    send_data("2|25|90")

def turn_right():
    send_data("2|25|180")

def stop():
    send_data("1|0|0")
