import time
import serial_test_window

if_read_ID_thread = False
ID = 0
current_step = 0
if_moving = False

route_steps = [
    "moving_ahead",
    
    
   

]
def if_ID_head(data):
    return data[0]=="@"
        

def if_task_finish_head(data):
    return data[0]=="#"
     
    
def if_color_head(data):
    return data[0]=="!"
#ID:$|12|

def read_ID_thread():
    global if_read_ID_thread
    global ID
    while True:
        data=serial_test_window.read_data()

        if if_ID_head(data):
           # ID=read_text(data)##读取ID
            #OLED.show_text(ID)##显示ID
           # id_sounder=Boardcast.Board_cast()
           # id_sounder.ID(ID)##广播ID
            if_read_ID_thread=True
        time.sleep(0.1)

def execute_step(step):
    global if_moving
    
    if step == "moving_ahead":
        serial_test_window.move_ahead()
        if_moving = True
            
        while if_moving:
            data = serial_test_window.read_data()
            
            if if_ID_head(data):
                print(data)
                continue
                
            
            elif if_task_finish_head(data):
                serial_test_window.stop()
                if_moving = False
                print("Task finished, movement stopped.")
                break

            elif if_color_head(data):
                serial_test_window.stop()
                if_moving = False
                    #handle_object_detection()  # 将物体检测逻辑提取为单独函数
                break
                
                time.sleep(0.1)
                
    elif step == "turn_right":
        serial_test_window.turn_right()
        while True:
            data=serial_test_window.read_data()
            print(data)
            
            if if_task_finish_head(data):
                print("ok")
                break
                if_moving = False
        
    elif step == "turn_left":
        serial_test_window.turn_left()
        while True:
            data=serial_test_window.read_data()
            print(data)
           
            if if_task_finish_head(data):
                print("ok")
                break
                if_moving = False


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
