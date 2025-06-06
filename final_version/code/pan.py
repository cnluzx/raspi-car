import time
"""云台模块

    功能:设置云台角度,实现左右转动摄像头识别
    pan_left()左转  pan_right()右转  pan_center() 返回中心

    使用方法:
    step1: pan=Pan()
    step2: pan.pan_left()  pan.pan_right()  pan.pan_center()
    
    """
class Pan:

    ang=120
    def __init__(self):
        import RPi.GPIO as GPIO
        self.GPIO= GPIO
        self.pin_1= 18   
        self.pin_2 =13
        self.pin_light= 4 
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_1,GPIO.OUT)
        GPIO.setup(self.pin_2,GPIO.OUT)
        GPIO.setup(self.pin_light,GPIO.OUT)

    def light_on(self):###补光灯可省略，直接使用现有供电
        self.GPIO.output(self.pin_light,self.GPIO.HIGH)

    def set_angle(self,pin,angle=ang):
        pwm=self.GPIO.PWM(pin,50)
        pwm.start(0)
        duty=2+angle/18
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)
        pwm.stop()

    def pan_left(self,angle=ang):
        self.set_angle(self.pin_1,0)
        self.set_angle(self.pin_2,angle)
    def pan_left_right(self,angle=ang):
        self.set_angle(self.pin_1,10)
        self.set_angle(self.pin_2,angle)

    def pan_right(self,angle=ang):
        self.set_angle(self.pin_1,170)
        self.set_angle(self.pin_2,angle)

    def pan_right_left(self,angle=ang):
        self.set_angle(self.pin_1,160)
        self.set_angle(self.pin_2,angle)
    def pan_center(self,angle=ang):
        self.set_angle(self.pin_1,90)
        self.set_angle(self.pin_2,angle)
    
    def pan_turn(self,down_angle,up_angle):
        self.set_angle(self.pin_1,down_angle)
        self.set_angle(self.pin_2,up_angle)

    def pan_center_up(self):
        self.set_angle(self.pin_1,90)
        self.set_angle(self.pin_2,0)

    def test(self):
        self.pan_left()
        time.sleep(2)
        self.pan_right()
        time.sleep(2)
        self.pan_center()
        time.sleep(2)

if __name__ == '__main__':
    p=Pan()
    p.test()