from simple_pid import PID
from src.config.configManager import global_config

class PIDTiltAngleToTorque:
    def __init__(self, kp, ki, kd, setpoint=global_config.angle_neutral,
                 output_limits=(-global_config.torque_limit, global_config.torque_limit)):
        self.pid = PID(kp, ki, kd, setpoint=setpoint)
        self.pid.output_limits = output_limits

    def update(self, current_angle: float) -> float:
        return self.pid(current_angle)

    @property
    def target_angle(self) -> float:
        return self.pid.setpoint

    @target_angle.setter
    def target_angle(self, value: float):
        self.pid.setpoint = value

    @property
    def kp(self) -> float:
        return self.pid.Kp

    @kp.setter
    def kp(self, value: float):
        self.pid.Kp = value

    @property
    def ki(self) -> float:
        return self.pid.Ki

    @ki.setter
    def ki(self, value: float):
        self.pid.Ki = value

    @property
    def kd(self) -> float:
        return self.pid.Kd

    @kd.setter
    def kd(self, value: float):
        self.pid.Kd = value

    @property
    def output_limits(self) -> tuple:
        return self.pid.output_limits
