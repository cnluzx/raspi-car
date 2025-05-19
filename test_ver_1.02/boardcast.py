import pygame

pygame.mixer.music.load("sound\\shape\\cri.mp3")
        # 播放音乐
pygame.mixer.music.play()
    # 等待音乐播放完毕
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(1)  


####已完成，无问题的模块会打######
####模块列表：########################################################
####1.oled.py  OLED显示模块  太多导入就单独一个文件了
####2.Serial_test类  串口通信模块
####3.CarMove类  车辆控制模块
####4.detect 类  传统图像检测模块
####5.boardcast 类  语音播报模块
####6.pwm.py  舵机控制模块
##################################################################################
###现在的任务：
####使用到的标志位:stop_flag 停止标志位
####detection_triggered 检测任务触发标志
####detection_completed 检测任务完成标志

###重要的参数：current_step 当前执行的步骤
###