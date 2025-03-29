# angle_controller.py
from simple_pid import PID

class AngleController:
    def __init__(self, kp, ki, kd, setpoint=0.0, output_limits=(-1.0, 1.0)):
        self.pid = PID(kp, ki, kd, setpoint=setpoint)
        self.pid.output_limits = output_limits

    def update(self, current_angle: float) -> float:
        return self.pid(current_angle)