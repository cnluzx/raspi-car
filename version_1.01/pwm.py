import RPi.GPIO as GPIO
import time
pin_1= 18   
pin_2 =13
pin_light= 4 
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_1,GPIO.OUT)
GPIO.setup(pin_2,GPIO.OUT)
GPIO.setup(pin_light,GPIO.OUT)

def light_on():
    GPIO.output(pin_light,GPIO.HIGH)

def set_angle(pin,angle):
    pwm=GPIO.PWM(pin,50)
    pwm.start(0)
    duty=2+angle/18
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.stop()


def pan_left(angle=120):
    set_angle(pin_1,0)
    set_angle(pin_2,angle)

def pan_right(angle=120):
    set_angle(pin_1,170)
    set_angle(pin_2,angle)

def pan_center(angle=120):
    set_angle(pin_1,90)
    set_angle(pin_2,angle)
