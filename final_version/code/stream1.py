from oled import *
import serial
from Serial import *
from boardcast import * 
from pan import *
from detection import *


 
if __name__ == '__main__':
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=115200,
        timeout=1)
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
            pan.pan_left()#
            time.sleep(2)#
            ret1,num,num1=d.judge_center()#
            print(ret1,num,num1)
            if ret1:
                ret_center=num
                if ret_center==1 or ret_center==2:
                    ret,shape,Best_Shape,Best_Color=d.Detect(1)
                elif ret_center==3:
                    pan.pan_left_right()
                    ret,shape,Best_Shape,Best_Color=d.Detect(1)
                    print(ret,shape,Best_Shape,Best_Color)
                real_result=shape-1
                if real_result//4==0:
                    shapez="rectangle"
                elif real_result//4==1:
                    shapez ="up-trapezium"
                elif real_result//4==2:
                    shapez="down-rapeziu"
                elif real_result//4==3:
                    shapez="square"

                if shape%2==0:
                    hollow="hollow"
                else: 
                    hollow="solid"
                if Best_Color ==1: 
                    tran_color="red"
                else : 
                    tran_color="blue"
                print("find")
                oled.update_display("detected",f"{shapez}",f"{hollow}",f"{tran_color}")
                board._play_sound("shape", shape)
                board._play_sound("color", tran_color)
                pan.pan_center()
                ser.write("5|0|0".encode("utf-8"))
                print("ok")
                detection_event.clear()

            else :
                print("白板")
                pan.pan_right()
                time.sleep(2)
                print("1")
                ret2,num2,num3=d.judge_center_2()
                if ret2:
                    print("2")
                    ret_center=num2
                    if ret_center==1 or ret_center==3:
                        ret,shape,Best_Shape,Best_Color=d.Detect(2)
                    elif ret_center==2:
                        pan.pan_right_left()
                        ret,shape,Best_Shape,Best_Color=d.Detect(2)
                        print(ret,shape,Best_Shape,Best_Color)
                    real_result=shape-1
                    if real_result//4==0:
                        shapez="rectangle"
                    elif real_result//4==1:
                        shapez ="up-trapezium"
                    elif real_result//4==2:
                        shapez="down-rapeziu"
                    elif real_result//4==3:
                        shapez="square"

                    if shape%2==0:
                        hollow="hollow"
                    else: 
                        hollow="solid"
                    if Best_Color ==1: 
                        tran_color="red"
                    else : 
                        tran_color="blue"
                    oled.update_display("detected",f"{shapez}",f"{hollow}",f"{tran_color}")
                    board._play_sound("shape", shape)
                    board._play_sound("color", Best_Color)
                    pan.pan_center()
                    ser.write("5|0|0".encode("utf-8"))
                    detection_event.clear()
                else:
                    print("No find!")
                    board.update_sound(0)
                    pan.pan_center()
                    ser.write("5|0|0".encode("utf-8"))
                    detection_event.clear()