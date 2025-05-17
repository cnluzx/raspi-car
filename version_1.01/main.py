import serial_task
import threading
import boardcast
import oled
import time
import detect
import pwm

if_read_ID_thread = False
ID = 0
current_step = 0
if_moving = False


route_steps = [
    "moving_ahead",
    "turn_left"
    #"moving_ahead",
   # "turn_right",
    #"moving_ahead"

]
def if_ID_head(data):
    return data[0]=="@"
        

def if_task_finish_head(data):
    return data[0]=="#"
     
    
def if_color_head(data):
    return data[0]=="!"
#ID:$|12|
def read_text(messages):
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
        data=serial_task.read_data()

        if if_ID_head(data):
            ID=read_text(data)##读取ID
           #oled.show_text(ID)##显示ID
           # id_sounder=Boardcast.Board_cast()
           # id_sounder.ID(ID)##广播ID
            if_read_ID_thread=True
        time.sleep(0.1)

def execute_step(step):
    global if_moving
    
    if step == "moving_ahead":
        serial_task.move_ahead()
        if_moving = True
            
        while if_moving:
            data = serial_task.read_data()
            if if_ID_head(data):
               # print(data)
                continue
                
            
            elif if_task_finish_head(data):
                if_moving = False
                print("Task finished, movement stopped.")
                break

           # elif if_color_head(data):
            #    serial_send.stop()
              #  if_moving = False
                    #handle_object_detection()  # 将物体检测逻辑提取为单独函数
             #   break
                
              #  time.sleep(0.1)
                
    elif step == "turn_right":
        serial_task.turn_right()
        while True:
            data=serial_task.read_data()
            print(data)            
            if if_task_finish_head(data):
              #  print("ok")
                break
                if_moving = False
        
    elif step == "turn_left":
        serial_task.turn_left()
        while True:
            data=serial_task.read_data()
            print(data)
           
            if if_task_finish_head(data):
                print("ok")
                break
                if_moving = False


def handle_object_detection():
    """处理物体检测逻辑"""
    pan = pwm.pan_left

    ret,frame,frame_count=detect.capture_frame()
    if_detect, shape, hollow, color = detect.main(frame)    
    if not if_detect:
        pan.Pan_right()
        if_detect, shape, hollow, color = detect.main(frame)
    
    display_text = f"{shape} {hollow} {color}" if if_detect else "No object detected."
    oled.show_text(display_text)

def moving_thread():
    global current_step
    while current_step < len(route_steps):
        step = route_steps[current_step]
        execute_step(step)
        current_step += 1
        print(current_step)

def main():

    moving_thread()
    
    

if __name__ == '__main__':
    main()