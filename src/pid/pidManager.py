from src.config.configManager import global_config
from src.pid.PIDTiltAngleToTorque import PIDTiltAngleToTorque


class pidManager:
    def __init__(self):
        #self.pid_tilt_angle_to_torque = PIDTiltAngleToTorque(0.0120305263, 0.117203011, 0.000096108, global_config.angle_neutral)
        self.pid_tilt_angle_to_torque = PIDTiltAngleToTorque(0.03, 0.2, 0.0017, global_config.angle_neutral)
        
        # offset = 6.7 degrees
        
        self.torque_differential = 0.0

        self.base_target_angle = global_config.angle_neutral
        self.dynamic_target_angle_offset = 0.0

    def update_pid_target(self):
        final_target = self.base_target_angle + self.dynamic_target_angle_offset
        self.pid_tilt_angle_to_torque.target_angle = final_target
        print(f"Updated target angle: {final_target:.2f}")

    def set_dynamic_target_angle_offset(self, value):
        self.dynamic_target_angle_offset = value
        self.update_pid_target()

    def stop(self):
        self.base_target_angle = global_config.angle_neutral
        self.update_pid_target()

    def goForward(self):
        self.base_target_angle = global_config.angle_neutral + global_config.angle_move
        self.update_pid_target()

    def goBackward(self):
        self.base_target_angle = global_config.angle_neutral - global_config.angle_move
        self.update_pid_target()
        
    def setTargetAngle(self,value):
        self.base_target_angle = global_config.angle_neutral - value * 10
        self.update_pid_target()

    def setTargetTorqueDifferenital(self,value):
        self.torque_differential = value * 0.03
        