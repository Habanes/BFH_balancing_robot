from src.config.configManager import global_config
from src.pid.PIDAngularVelocityToTorqueDifferential import PIDAngularVelocityToTorqueDifferential
from src.pid.PIDEstimatedTorqueToTorque import PIDEstimatedTorqueToTorque
from src.pid.PIDTiltAngleToTorque import PIDTiltAngleToTorque
from src.pid.PIDVelocityToTiltAngle import PIDVelocityToTiltAngle

class pidManager:
    def __init__(self):
        self.pid_tilt_angle_to_torque = PIDTiltAngleToTorque(0.03, 0.2, 0.001, global_config.angle_neutral)

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
