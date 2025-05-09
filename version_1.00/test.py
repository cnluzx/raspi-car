####主要是串口有些问题，就一步一步测试了
import serial_send
import threading
import time
import Detect_object
import PWM


if_moving = False
current_step = 0

route_steps = [
    "turn_right",
    "turn_left",
    "turn_left",
    "turn_left",
    "turn_left",
    "turn_right",
    "turn_right",
]

def if_ID_head(data):
    return data[0]=="@"
        
def if_task_finish_head(data):
    return data[0]=="#"
     
def if_color_head(data):
    return data[0]=="！"

#ID:$|12|
def read_text(messages):
    #找到第一个'|'
    index = messages.find('|')
    #找到第二个'|'
    index2 = messages.find('|',index+1)
    #拿到两个|之间的数据
    text = int(messages[index+1:index2])
    return text

def execute_step(step):
    global if_moving
    try:
        if step == "moving_ahead":
            serial_send.move_ahead()
            if_moving = True
            
            while if_moving:
                data = serial_send.read_data()

                if  if_ID_head(data):
                    ID=read_text(data)##读取ID
                    print(ID)##输出检测到的ID
                    #OLED.show_text(ID)##显示ID
                    continue

                elif if_task_finish_head(data):
                    #serial_send.stop()
                    if_moving = False
                    break

                elif if_color_head(data):
                    serial_send.stop()
                    if_moving = False
                    if_ret, display_text = handle_object_detection()
                    if if_ret:
                        print(display_text)
                        serial_send.move_ahead()
                        #OLED.show_text(display_text)##显示物体检测结果
                    continue
                
                time.sleep(0.1)
                
        elif step == "turn_right":
            serial_send.turn_right()
            while if_moving:  
                data=serial_send.read_data()
                print(data)##测试串口数据
                if if_task_finish_head(data):
                    if_moving = False
        
        elif step == "turn_left":
            serial_send.turn_left()
            if_moving = True
            while if_moving:  
                data=serial_send.read_data()
                print(data)##测试串口数据
                if if_task_finish_head(data):
                    if_moving = False

    except Exception as e:
        print(f"Error in execute_step: {str(e)}")
        if_moving = True
        while if_moving: 
            data=serial_send.stop()
            print(data)##测试串口数据
            if if_task_finish_head(data):
                if_moving = False

def handle_object_detection():
    """处理物体检测逻辑"""
    pan = PWM.PAN()
    pan.Pan_left()
    ret,frame,frame_count=Detect_object.capture_frame()
    if_detect, shape, hollow, color = Detect_object.main(frame)
    if not if_detect:
        pan.Pan_right()
        if_detect, shape, hollow, color = Detect_object.main(frame)
    
    display_text = f"{shape} {hollow} {color}" if if_detect else "No object detected."
    return if_detect, display_text  
    #OLED.show_text(display_text)

def moving_thread():
    global current_step
    while current_step < len(route_steps):
        step = route_steps[current_step]
        execute_step(step)
        print("step"+str(current_step))
        current_step += 1


def main():
    moving_thread()


if __name__ == '__main__':
    main()