from src.config.configManager import global_config
from src.pid.PIDAngularVelocityToTorqueDifferential import PIDAngularVelocityToTorqueDifferential
from src.pid.PIDEstimatedTorqueToTorque import PIDEstimatedTorqueToTorque
from src.pid.PIDTiltAngleToTorque import PIDTiltAngleToTorque
from src.pid.PIDVelocityToTiltAngle import PIDVelocityToTiltAngle

class pidManager:
    def __init__(self):
        self.pid_angular_velocity_to_torque_differential = PIDAngularVelocityToTorqueDifferential(1.0, 1.0, 1.0)
        self.pid_estimated_torque_to_torque = PIDEstimatedTorqueToTorque(1.0, 1.0, 1.0)
        self.pid_tilt_angle_to_torque = PIDTiltAngleToTorque(0.03, 0.2, 0.01)
        self.pid_velocity_to_tilt_angle = PIDVelocityToTiltAngle(1.0, 1.0, 1.0)

        self._angle_y_offset = 0.0
        self.adjusted_neutral_angle_y = global_config.angle_neutral  # optional use

    # === Angle Offset Management ===
    @property
    def angle_y_offset(self):
        return self._angle_y_offset

    @angle_y_offset.setter
    def angle_y_offset(self, value: float):
        self._angle_y_offset = value
        self.adjusted_neutral_angle_y = global_config.angle_neutral + value

    # === Preset Movement Commands ===
    def stop(self):
        self.pid_angular_velocity_to_torque_differential.target_torque = 0.0
        self.pid_velocity_to_tilt_angle.target_velocity = 0.0

    def goForward(self):
        self.pid_angular_velocity_to_torque_differential.target_torque = 0.0
        self.pid_velocity_to_tilt_angle.target_velocity = global_config.base_velocity

    def goBackward(self):
        self.pid_angular_velocity_to_torque_differential.target_torque = 0.0
        self.pid_velocity_to_tilt_angle.target_velocity = -global_config.base_velocity

    def rotateRight(self):
        self.pid_angular_velocity_to_torque_differential.target_torque = global_config.angle_rotation
        self.pid_velocity_to_tilt_angle.target_velocity = 0.0

    def rotateLeft(self):
        self.pid_angular_velocity_to_torque_differential.target_torque = -global_config.angle_rotation
        self.pid_velocity_to_tilt_angle.target_velocity = 0.0
