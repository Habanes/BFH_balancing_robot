from src.config.configManager import global_config
from src.pid.PIDAngularVelocityToTorqueDifferential import PIDAngularVelocityToTorqueDifferential
from src.pid.PIDEstimatedTorqueToTorque import PIDEstimatedTorqueToTorque
from src.pid.PIDTiltAngleToTorque import PIDTiltAngleToTorque
from src.pid.PIDVelocityToTiltAngle import PIDVelocityToTiltAngle

class pidManager:
    def __init__(self):
        self.pid_tilt_angle_to_torque = PIDTiltAngleToTorque(0.03, 0.2, 0.001, global_config.angle_neutral)

    # === Preset Movement Commands ===
    
    def set_dynamic_target_angle_offset(self,value):
        self.dynamic_target_angle_offset = value
        self.pid_tilt_angle_to_torque.target_angle = self.pid_tilt_angle_to_torque.target_angle + self.dynamic_target_angle_offset
        print(f"dynamic angle target offset: {self.dynamic_target_angle_offset}")
    
    def stop(self):
        self.pid_tilt_angle_to_torque.target_angle = global_config.angle_neutral
        print(f"stop tgt: {self.pid_tilt_angle_to_torque.target_angle}")

    def goForward(self):
        self.pid_tilt_angle_to_torque.target_angle = global_config.angle_move
        print(f"fwd tgt: {self.pid_tilt_angle_to_torque.target_angle}")

    def goBackward(self):
        self.pid_tilt_angle_to_torque.target_angle = - global_config.angle_move
        print(f"back tgt: {self.pid_tilt_angle_to_torque.target_angle}")
