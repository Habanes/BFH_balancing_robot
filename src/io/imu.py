import smbus2 as smbus

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