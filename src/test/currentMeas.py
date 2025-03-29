import smbus2 as smbus
import matplotlib.pyplot as plt
import time
import numpy as np

SAMPLE_COUNT = 1000
I2C_BUS_ID = 1
ADC_ADDR_LEFT = 0x4B
ADC_ADDR_RIGHT = 0x4D

class CurrentSensor:
    def __init__(self, is_left: bool, bus=smbus.SMBus(I2C_BUS_ID)) -> None:
        self.bus = bus
        self.address = ADC_ADDR_LEFT if is_left else ADC_ADDR_RIGHT

    def read_current(self) -> int:
        raw = self.bus.read_i2c_block_data(self.address, 0x00, 2)
        value = ((raw[1] >> 2) | (raw[0] << 6)) & 0x3FF
        return value - 1024 if value & 0x200 else value

if __name__ == "__main__":
    sensor_left = CurrentSensor(is_left=True)
    sensor_right = CurrentSensor(is_left=False)
    
    samples = np.zeros((SAMPLE_COUNT, 2))

    for i in range(SAMPLE_COUNT):
        samples[i, 0] = sensor_left.read_current()
        samples[i, 1] = sensor_right.read_current()
        print(f"Left: {samples[i,0]:.2f}  Right: {samples[i,1]:.2f}")
        time.sleep(0.01)

    plt.plot(samples)
    plt.savefig("plot_encoder.png")
