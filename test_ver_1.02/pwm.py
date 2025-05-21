import RPi.GPIO as GPIO
############################
##树莓派连接云台完成
##使用方式：1.装RPI库，如果初始的使用的是树莓派官方的系统则不用安装（    sudo apt-get update    sudo apt-get install python-rpi.gpio）
##         2.接线，接线步骤在下方
##         3.导入库，创建对象，调用相应的函数，传入角度值
##树莓派连接BCM编码方式
##树莓派连接sg90舵机引脚位GPIO1和GPIO23
##使用BCM编码方式为 pin18  pin13
##电源红线接树莓派5V 接树莓派GND 黄色线接上面的编码引脚
##有点粗略，会继续修改，一般我们只会用到下方控制大范围转向的舵机
##因为走的路径是横平竖直的，所以下方的舵机控制只有三个状态：左、右、中，分别对应角度为0、180、90度
##微小角度值：angle的可以设置上方摄像头的角度
##代码编写者：cnluzx
##########################

##现在有个bug 使用的是360度的舵机，逻辑上有差异，需要修改

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
