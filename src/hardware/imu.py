import smbus2 as smbus
from src.config.configManager import global_config

# I2C configuration
I2C_BUS_ID = 1
IMU_ADDR = 0x28

# Register addresses
REG_MODE = 0x3D
REG_PITCH_LSB = 0x1E
REG_GYRO_Y_LSB = 0x16
REG_GYRO_Z_LSB = 0x18

# Operation modes
MODE_CONFIG = 0b0000
MODE_NDOF = 0b1100

class IMU:
    def __init__(self, bus=smbus.SMBus(I2C_BUS_ID)) -> None:
        self.bus = bus
        self.pitch_filtered = None
        self.gyro_y_filtered = None
        self.alpha = 0.1  # Smoothing factor: lower = smoother but slower
        
        self._initialize()

    def _initialize(self):
        # Set to config mode first
        self.bus.write_byte_data(IMU_ADDR, REG_MODE, MODE_CONFIG)
        if self.bus.read_byte_data(IMU_ADDR, REG_MODE) == MODE_CONFIG:
            # Switch to NDOF mode (sensor fusion)
            self.bus.write_byte_data(IMU_ADDR, REG_MODE, MODE_NDOF)
            if self.bus.read_byte_data(IMU_ADDR, REG_MODE) != MODE_NDOF:
                raise RuntimeError("IMU failed to initialize NDOF mode")
            print("IMU initialized")

      
    def read_pitch(self) -> float:
        # Read and decode 16-bit pitch value
        raw = self.bus.read_i2c_block_data(IMU_ADDR, REG_PITCH_LSB, 2)
        value = (raw[1] << 8) | raw[0]
        if value > 32767:
            value -= 65536
        return value / 16 + 90  + global_config.angle_neutral # Normalize offset

    def read_gyro_y(self) -> float:
        # Read and decode 16-bit Y-axis gyro value
        raw = self.bus.read_i2c_block_data(IMU_ADDR, REG_GYRO_Y_LSB, 2)
        value = (raw[1] << 8) | raw[0]
        if value > 32767:
            value -= 65536
        return value / 16
        
    def read_gyro_z(self) -> float:
        """Read and decode 16-bit Z-axis gyro value (yaw rate in °/s)"""
        raw = self.bus.read_i2c_block_data(IMU_ADDR, REG_GYRO_Z_LSB, 2)
        value = (raw[1] << 8) | raw[0]
        if value > 32767:
            value -= 65536
        return value / 16  # Convert from LSB to °/s