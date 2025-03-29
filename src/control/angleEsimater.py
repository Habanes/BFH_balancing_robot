class AngleEstimator:
    def __init__(self, imu):
        self.imu = imu
        self.alpha = 0.98
        self.estimated_angle = self.imu.read_pitch()

    def get_angle(self) -> float:
        accel_angle = self.imu.read_pitch()
        gyro_rate = self.imu.read_gyro_y()

        dt = 0.01  # Assumes fixed loop rate of 100Hz
        self.estimated_angle = (
            self.alpha * (self.estimated_angle + gyro_rate * dt)
            + (1 - self.alpha) * accel_angle
        )

        return self.estimated_angle