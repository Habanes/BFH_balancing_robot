from gpiozero import DigitalOutputDevice, PWMOutputDevice  # GPIO control library
from lib.hardwarePWMLib import HardwarePWM                 # Custom hardware PWM library
import time                                                # For delays

# Number of debug samples (not used in this script)
DEBBUG_LENGTH = 1000

# GPIO pin assignments for motor 1
PWM_PIN = 13
DIR_PIN = 23
OTHER_PIN = 17

# GPIO pin assignments for motor 2
PWM_PIN_2 = 12
DIR_PIN_2 = 24
OTHER_PIN_2 = 18

# Class to control a motor using PWM and direction pins
class Motor:
    def __init__(self, left_right: bool):
        # Invert direction logic based on left/right flag
        self.inverse_dir = not left_right

        # Create hardware PWM object (channel 1 for left, 0 for right)
        self.hwPWM = HardwarePWM(pwm_channel=1 if left_right else 0, hz=50000, chip=2)

        # Direction control pin
        self.direction = DigitalOutputDevice(pin=DIR_PIN if left_right else DIR_PIN_2)

        # Additional pin (possibly enable or brake pin)
        self.other_pin = DigitalOutputDevice(pin=OTHER_PIN if left_right else OTHER_PIN_2)

    def write_pwm(self, pwm_value):
        # Limit absolute value to 1.0, then invert it (duty cycle: 0 = full power, 1 = off)
        pwm_value_abs = 1 - min(abs(pwm_value), 1.0)

        # Set duty cycle (0-100%) to PWM device
        self.hwPWM.change_duty_cycle(100.0 * pwm_value_abs)

        # Set motor direction based on sign of pwm_value and inverse_dir flag
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
        # Start PWM with 0% duty cycle
        self.hwPWM.start(0)

        # Enable motor via the other pin
        self.other_pin.on()

        # Ensure motor is not moving initially
        self.write_pwm(0)
    
    def stop_pwm(self):
        # Stop PWM signal
        self.hwPWM.stop()

        # Disable motor via the other pin
        self.other_pin.off()

# Main block: executed when running script directly
if __name__ == "__main__":
    # Create motor objects for both motors
    motor_1 = Motor(left_right=True)
    motor_2 = Motor(left_right=False)
    
    # Start both motors (initialize PWM and enable)
    motor_1.start_pwm()
    motor_2.start_pwm()
    
    # Set both motors to rotate with 50% speed in negative direction
    motor_1.write_pwm(-0.5)
    motor_2.write_pwm(-0.5)
    
    # Let motors run for 2 seconds
    time.sleep(2)

    # Stop both motors
    motor_1.stop_pwm()
    motor_2.stop_pwm()
