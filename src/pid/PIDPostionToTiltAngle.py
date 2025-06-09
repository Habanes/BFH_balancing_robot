from simple_pid import PID
from src.config.configManager import global_config

class PIDPositionToTiltAngle:
    def __init__(self, kp, ki, kd, setpoint=0.0,
                 output_limits=(-global_config.tilt_angle_soft_limit, global_config.tilt_angle_soft_limit)):
        self.pid = PID(kp, ki, kd, setpoint=setpoint)
        self.pid.output_limits = output_limits
        
        # Direct access attributes
        self.target_position = setpoint
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limits = output_limits

    def update(self, current_position: float) -> float:
        # Sync attributes with PID object
        self.pid.setpoint = self.target_position
        self.pid.Kp = self.kp
        self.pid.Ki = self.ki
        self.pid.Kd = self.kd
        self.pid.output_limits = self.output_limits
        
        return self.pid(current_position)
