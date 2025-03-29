from gpiozero import DigitalOutputDevice, PWMOutputDevice
from hardwarePWMLib import HardwarePWM
import time


DEBBUG_LENGTH=1000


PWM_PIN = 13
DIR_PIN = 23
OTHER_PIN = 17
PWM_PIN_2 = 12
DIR_PIN_2 = 24
OTHER_PIN_2 = 18



class Motor:
    def __init__(self,left_right:bool):

        self.inverse_dir = not left_right
        self.hwPWM = HardwarePWM(pwm_channel=1 if left_right else 0,hz=50000,chip=2)
        self.direction = DigitalOutputDevice(pin=DIR_PIN if left_right else DIR_PIN_2) 
        self.other_pin = DigitalOutputDevice(pin=OTHER_PIN if left_right else OTHER_PIN_2)

        

    
    def write_pwm(self,pwm_value):
        pwm_value_abs = 1 - min(abs(pwm_value),1.0)
        self.hwPWM.change_duty_cycle(100.0*pwm_value_abs)
        if self.inverse_dir:
            if pwm_value < 0:
                self.direction.on()
            else:
                self.direction.off()
        else:
            if pwm_value < 0:
                self.direction.off()
            else:
                self.direction.on()
    
    def start_pwm(self):
        self.hwPWM.start(0)
        self.other_pin.on()
        self.write_pwm(0)
    
    def stop_pwm(self):
        self.hwPWM.stop()
        self.other_pin.off()



if __name__=="__main__":

    motor_1 = Motor(left_right=True)
    motor_2 = Motor(left_right=False)
     
    motor_1.start_pwm()
    motor_2.start_pwm()
    
    motor_1.write_pwm(-0.5)
    motor_2.write_pwm(-0.5)
    
    time.sleep(2)

    motor_1.stop_pwm()
    motor_2.stop_pwm()