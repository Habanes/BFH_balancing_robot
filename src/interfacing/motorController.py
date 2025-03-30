from gpiozero import DigitalOutputDevice
from src.interfacing.hardwarePWMLib import HardwarePWM

# GPIO pin mappings for both motors
PIN_PWM_LEFT = 13
PIN_DIR_LEFT = 23
PIN_EN_LEFT = 17

PIN_PWM_RIGHT = 12
PIN_DIR_RIGHT = 24
PIN_EN_RIGHT = 18

class MotorController:
    def __init__(self, is_left: bool):
        # Set correct pins and PWM channel depending on motor side
        pwm_channel = 1 if is_left else 0
        dir_pin = PIN_DIR_LEFT if is_left else PIN_DIR_RIGHT
        en_pin = PIN_EN_LEFT if is_left else PIN_EN_RIGHT

        self._reverse = not is_left  # Reverse direction for right motor
        self._pwm = HardwarePWM(pwm_channel=pwm_channel, hz=50000, chip=2)
        self._dir = DigitalOutputDevice(pin=dir_pin)
        self._enable = DigitalOutputDevice(pin=en_pin)

    def start(self):
        self._pwm.start(0)
        self._enable.on()
        self.set_speed(0)

    def stop(self):
        self.set_speed(0)
        self._pwm.stop()
        self._enable.off()

    def set_speed(self, value: float):
        # Convert speed to duty cycle (inverted)
        duty = 1 - min(abs(value), 1.0)
        self._pwm.change_duty_cycle(100.0 * duty)

        # Set direction depending on sign and motor side
        if (value < 0) ^ self._reverse:
            self._dir.on()
        else:
            self._dir.off()
