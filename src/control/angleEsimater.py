class AngleEstimator:
    def __init__(self, imu):
        self.imu = imu
        self.estimated_angle = self.imu.read_pitch()

    def get_angle(self) -> float:
        return self.estimated_angle
