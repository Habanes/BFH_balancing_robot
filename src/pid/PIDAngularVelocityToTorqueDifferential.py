from simple_pid import PID
from src.config.configManager import global_config

class PIDAngularVelocityToTorqueDifferential:
    def __init__(self, kp, ki, kd, setpoint=0.0,
                 output_limits=(-global_config.torque_differential_limit, global_config.torque_differential_limit)):
        self.pid = PID(kp, ki, kd, setpoint=setpoint)
        self.pid.output_limits = output_limits

    def update(self, estimated_torque_diff: float) -> float:
        return self.pid(estimated_torque_diff)

    @property
    def target_torque(self) -> float:
        return self.pid.setpoint

    @target_torque.setter
    def target_torque(self, value: float):
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
