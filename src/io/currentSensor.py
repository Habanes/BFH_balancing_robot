import smbus2 as smbus

# I2C configuration
I2C_BUS_ID = 1
ADC_ADDR_LEFT = 0x4B
ADC_ADDR_RIGHT = 0x4D

class CurrentSensor:
    def __init__(self, is_left: bool, bus=smbus.SMBus(I2C_BUS_ID)) -> None:
        self.bus = bus
        self.address = ADC_ADDR_LEFT if is_left else ADC_ADDR_RIGHT

    def read_current(self) -> int:
        # Read two bytes from the ADC
        raw = self.bus.read_i2c_block_data(self.address, 0x00, 2)

        # Combine and mask to get 10-bit result
        value = ((raw[1] >> 2) | (raw[0] << 6)) & 0x3FF

        # Convert from two's complement if negative
        return value - 1024 if value & 0x200 else value
