import smbus2 as smbus
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

SAMPLE_COUNT = 1000
I2C_BUS_ID = 1
IMU_ADDR = 0x28

REG_MODE = 0x3D
REG_PITCH_LSB = 0x1E
REG_GYRO_Y_LSB = 0x16

MODE_CONFIG = 0b0000
MODE_NDOF = 0b1100

class IMU:
    def __init__(self, bus=smbus.SMBus(I2C_BUS_ID)) -> None:
        self.bus = bus
        self._initialize()

    def _initialize(self):
        self.bus.write_byte_data(IMU_ADDR, REG_MODE, MODE_CONFIG)
        if self.bus.read_byte_data(IMU_ADDR, REG_MODE) == MODE_CONFIG:
            self.bus.write_byte_data(IMU_ADDR, REG_MODE, MODE_NDOF)
            if self.bus.read_byte_data(IMU_ADDR, REG_MODE) != MODE_NDOF:
                raise RuntimeError("IMU failed to initialize NDOF mode")
            print("IMU initialized")

    def read_pitch(self) -> float:
        raw = self.bus.read_i2c_block_data(IMU_ADDR, REG_PITCH_LSB, 2)
        value = (raw[1] << 8) | raw[0]
        if value > 32767:
            value -= 65536
        return value / 16 + 90

    def read_gyro_y(self) -> float:
        raw = self.bus.read_i2c_block_data(IMU_ADDR, REG_GYRO_Y_LSB, 2)
        value = (raw[1] << 8) | raw[0]
        if value > 32767:
            value -= 65536
        return value / 16

if __name__ == "__main__":
    imu = IMU()
    data = np.zeros((SAMPLE_COUNT, 3))
    t0 = time.clock_gettime(0)

    for i in range(SAMPLE_COUNT):
        pitch = imu.read_pitch()
        gyro_y = imu.read_gyro_y()
        timestamp = time.clock_gettime(0) - t0

        data[i] = [timestamp, pitch, gyro_y]
        print(f"pitch: {pitch:.2f}  gyro_y: {gyro_y:.2f}")
        time.sleep(0.01)

    plt.plot(data[:, 0], data[:, 1])
    plt.savefig("imu.png")

    pd.DataFrame(data, columns=["Time", "Pitch", "Gyro_Y"]).to_csv("IMU.csv", index=False)
