from oled import *
import serial
from Serial import *
from boardcast import * 
from pan import *
from detection import *

ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=115200,
        timeout=1)
def main():
    pan.pan_left()
    ret1,num,num1=d.judge_center()
    if ret1:
        ret_center=pan.pan_judge(num)
        if ret_center==1 or ret_center==2:
            ret,shape,Best_Shape,Best_Color=d.Detect()
        elif ret_center==3:
            pan.pan_left_right()
            ret,shape,Best_Shape,Best_Color=d.Detect()
            print(ret,shape,Best_Shape,Best_Color)
    else :
        print("白板")
        pan.pan_right()
        ret1,num,num1=d.judge_center()
        if ret1:
            ret_center=pan.pan_judge(num)
            if ret_center==1 or ret_center==3:
                ret,shape,Best_Shape,Best_Color=d.Detect()
            elif ret_center==2:
                pan.pan_right_left()
                ret,shape,Best_Shape,Best_Color=d.Detect()
                print(ret,shape,Best_Shape,Best_Color)
    print(ret1,num,num1) 

if __name__ == '__main__':
    
    oled = Oled()
    board = Boardcast()
    seri=Seri()
    pan=Pan()
    obj=Detect_q()
    running_thread_event.set()

    start_thread("put_queue_stream",seri.put_queue_stream)
    start_thread("read_queue_stream",seri.read_queue_stream)
    start_thread("boardcast",board.threading_sound)
    start_thread("oled",oled.threading_text)


    while running_thread_event.is_set():
        if detection_event.is_set():
            pan.pan_left()
            time.sleep(1)
            obj.judge_center()
            ret,result,shape,color= obj.Detect()
            real_result=result-1
            if ret:
                if real_result//4==0:
                    shapez="矩形"
                elif real_result//4==1:
                    shapez ="上梯形"
                elif real_result//4==2:
                    shapez="下梯形"
                elif real_result//4==3:
                    shapez="正方形"

                if shape%2==0:
                    hollow="空心"
                else: 
                    hollow="实心"
                if color ==1: 
                    tran_color="红色"
                else : 
                    tran_color="蓝色"
                print("find")
                oled.update_display("识别到图像",f"{shapez}",f"{hollow}",f"{tran_color}")
                board._play_sound("shape", shape)
                board._play_sound("color", color)
                
                pan.pan_center()
                ser.write("5|0|0".encode("utf-8"))
                detection_event.clear()
            else:
                pan.pan_right()
                time.sleep(1)
                ret,result,shape,color= obj.Detect()
                if ret:
                    if (result-1)//4==0:
                        shapez="矩形"
                    elif (result-1)//4==1:
                        shapez ="上梯形"
                    elif (result-1)//4==2:
                        shapez="下梯形"
                    elif (result-1)//4==3:
                        shapez="正方形"

                    if shape%2==0:
                        hollow="空心"
                    else: 
                        hollow="实心"
                    if color ==1: 
                        tran_color="红色"
                    else : 
                        tran_color="蓝色"
                    print("find")
                    oled.update_display("识别到图像",f"{shapez}",f"{hollow}",f"{tran_color}")
                    board._play_sound("shape", shape)
                    board._play_sound("color", color)
                    
                    pan.pan_center()
                    ser.write("5|0|0".encode("utf-8"))
                    detection_event.clear()
                else:
                    print("No find!")
                    board.update_sound('shape',0)
                    pan.pan_center()
                    ser.write("5|0|0".encode("utf-8"))
