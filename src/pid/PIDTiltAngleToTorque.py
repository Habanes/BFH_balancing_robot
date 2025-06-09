from simple_pid import PID
from src.config.configManager import global_config

class PIDTiltAngleToTorque:
    def __init__(self, kp, ki, kd, setpoint=global_config.angle_neutral, output_limits=(-global_config.torque_limit, global_config.torque_limit)):
        self.pid = PID(kp, ki, kd, setpoint=setpoint)
        self.pid.output_limits = output_limits
        
        # Direct access attributes
        self.target_angle = setpoint
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limits = output_limits

    def update(self, current_angle: float) -> float:
        # Sync attributes with PID object
        self.pid.setpoint = self.target_angle
        self.pid.Kp = self.kp
        self.pid.Ki = self.ki
        self.pid.Kd = self.kd
        self.pid.output_limits = self.output_limits
        output = - self.pid(current_angle)
        
        return output
