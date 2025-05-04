import serial_send
import threading
import Boardcast
import OLED
import time

if_read_ID_thread = False
serial_lock = threading.Lock()
ID = 0


route_steps = [
    "moving_ahead",
    "turn_right",
    "moving_ahead",
    "turn_left",
    "moving_ahead",
    "turn_left",
    "moving_ahead",
    "turn_left",
    "moving_ahead",
    "turn_right"
    "moving_ahead"
]
def if_ID_head(data):
    return data[0]=="!"
        

def if_task_finish_head(data):
    return data[0]=="%"
     
    
def if_color_head(data):
    return data[0]=="#"
#ID:$|12|
def read_text(self,messages):
    #找到第一个'|'
    index = messages.find('|')
    #找到第二个'|'
    index2 = messages.find('|',index+1)
    #拿到两个|之间的数据
    text = int(messages[index+1:index2])
    return text

def read_ID_thread():
    global if_read_ID_thread
    global ID
    while True:
        data=serial_send.read_data()

        if if_ID_head(data):
            ID=read_text(data)##读取ID
            OLED.show_text(ID)##显示ID
            id_sounder=Boardcast()
            id_sounder.ID(ID)##广播ID
            if_read_ID_thread=True
        time.sleep(0.1)

def execute_step(step):
    global if_moving
    if step == "moving_ahead":
        with serial_lock:
            serial_send.move_ahead()
        if_moving = True
        while if_moving:
            with serial_lock:
                data = serial_send.read_data()
            if if_task_finish_head(data):
                with serial_lock:
                    serial_send.stop()
                if_moving = False
                print("Task finished, movement stopped.")
                break
            elif if_color_head(data):
                with serial_lock:
                    serial_send.stop()
                if_moving = False
                print("Color detected, movement stopped.")
                if_moving = True
                with serial_lock:
                    serial_send.move_ahead()
            time.sleep(0.1)
    elif step == "turn_right":
        with serial_lock:
            serial_send.turn_right()
        time.sleep(1)  # 假设右转需要 1 秒
        if_moving = False 

def moving_thread():
    global current_step
    while current_step < len(route_steps):
        step = route_steps[current_step]
        execute_step(step)
        current_step += 1
def main():
    ID_threading=threading.Thread(target=read_ID_thread)
    ID_threading.start() 

    moving_threading = threading.Thread(target=moving_thread)
    moving_threading.start()
    while True:
        if if_read_ID_thread:
            print("ID:",ID)
            if_read_ID_thread=False
        time.sleep(0.1) 

if __name__ == '__main__':
    main()