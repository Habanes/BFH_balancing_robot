from src.config.configManager import global_config
from src.pid.PIDEstimatedTorqueToTorque import PIDEstimatedTorqueToTorque
from src.pid.PIDTiltAngleToTorque import PIDTiltAngleToTorque
from src.pid.PIDVelocityToTiltAngle import PIDVelocityToTiltAngle

class pidManager:
    def __init__(self):
        # self.pid_tilt_angle_to_torque = PIDTiltAngleToTorque(0.0120305263, 0.117203011, 0.000096108, global_config.angle_neutral)
        self.pid_tilt_angle_to_torque = PIDTiltAngleToTorque(0.03, 0.2, 0.0017, global_config.angle_neutral)
        # offset = 6.7 degrees
        
        self.pid_velocity_to_tilt_angle = PIDVelocityToTiltAngle(0.01, 0.0, 0.001, 0.0)
        
        self.base_target_velocity = 0.0
        self.dynamic_target_velocity_offset = 0.0
        
        self.base_target_angle = global_config.angle_neutral
        self.dynamic_target_angle_offset = 0.0

    def update_pid_target_angle(self):
        final_target = self.base_target_angle + self.dynamic_target_angle_offset
        self.pid_tilt_angle_to_torque.target_angle = final_target
        print(f"Updated target angle: {final_target:.2f}")
        
    def update_pid_target_velocity(self):
        final_target = self.base_target_velocity + self.dynamic_target_velocity_offset
        self.pid_velocity_to_tilt_angle.target_velocity = final_target
        print(f"Updated target angle: {final_target:.2f}")

    def set_dynamic_target_angle_offset(self, value):
        self.dynamic_target_angle_offset = value
        self.update_pid_target_angle()

    def stop(self):
        self.base_target_angle = global_config.angle_neutral
        self.update_pid_target_angle()

    def goForward(self):
        self.base_target_angle = global_config.angle_neutral + global_config.angle_move
        self.update_pid_target_angle()

    def goBackward(self):
        self.base_target_angle = global_config.angle_neutral - global_config.angle_move
        self.update_pid_target_angle()
        
    def setTargetAngle(self,value):
        self.base_target_angle = global_config.angle_neutral - value
        self.update_pid_target_angle()
        
    def setTargetVelocity(self,value):
        self.base_target_velocity = value
        self.update_pid_target_angle()
