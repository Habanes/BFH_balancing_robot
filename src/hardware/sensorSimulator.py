import math
import time

class SensorSimulator:
    def __init__(self):
        # State
        self.pitch = 0.0  # in degrees
        self.pitch_rate = 0.0  # deg/s
        self.yaw = 0.0  # not simulated
        self.yaw_rate = 0.0  # not simulated
        self.step_count = 0.0
        self.current = 0.2
        self.motor_torque = 0.0

        # Constants for simulated dynamics
        self.inertia = 1.0
        self.damping = 0.6
        self.gravity_effect = 1.5
        self.encoder_gain = 0.1  # encoder ticks per torque unit per second
        self.current_gain = 0.01  # amps per torque unit

        self.last_time = time.time()

    # === IMU-like methods ===
    def read_pitch(self):
        self.update()
        return self.pitch

    def read_gyro_y(self):
        self.update()
        return self.pitch_rate

    def read_gyro_z(self):
        return self.yaw_rate  # still static for now

    def read_yaw(self):
        return self.yaw  # still static for now

    # === MotorController-like methods ===
    def get_steps(self):
        self.update()
        return self.step_count

    def get_current(self):
        return self.current + self.current_gain * abs(self.motor_torque)

    def start(self):
        pass

    def stop(self):
        self.motor_torque = 0.0

    def set_speed(self, torque):
        # Clamp to reasonable motor torque range
        self.motor_torque = max(min(torque, 10.0), -10.0)

    # === Physics Simulation ===
    def update(self):
        now = time.time()
        dt = now - self.last_time
        if dt <= 0.0:
            return
        self.last_time = now

        # Simulate 2nd order system: pitch acceleration from torque
        pitch_acc = (
            self.motor_torque / self.inertia
            - self.damping * self.pitch_rate
            - self.gravity_effect * self.pitch
        )

        self.pitch_rate += pitch_acc * dt
        self.pitch += self.pitch_rate * dt

        # Simulate encoder ticks from torque
        self.step_count += self.motor_torque * self.encoder_gain * dt
