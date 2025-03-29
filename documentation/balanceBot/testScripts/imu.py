import smbus2 as smbus                # Library for I2C communication
import time                           # For time-related functions
import numpy as np                    # For numerical operations and arrays
import matplotlib.pyplot as plt       # For plotting
import pandas as pd                   # For saving data to CSV

# Number of samples to record
DEBBUG_LENGTH = 1000

# I2C configuration constants
DEV_BUS = 1                           # I2C bus number
DEV_ADDR = 0x28                       # IMU I2C address
OPR_MODE_ADDR = 0x3d                  # Register to set operation mode
NDOF_MODE = 0b1100                    # 9 Degrees Of Freedom mode
CONFIG_MODE = 0b0000                  # Configuration mode
PITCH_MSB = 0x1f                      # MSB register for pitch (not used directly)
PITCH_LSB = 0x1e                      # LSB register for pitch (starting address to read 2 bytes)
PAGE_ID = 0x07                        # Page ID register (not used here)
GYRO_Y_MSB = 0x17                     # MSB register for gyro Y-axis (not used directly)
GYRO_Y_LSB = 0x16                     # LSB register for gyro Y-axis (starting address to read 2 bytes)

# Class to interface with the IMU
class IMU:
    def __init__(self, bus=smbus.SMBus(DEV_BUS)) -> None:
        # Initialize the IMU using the provided I2C bus
        self.init_imu(bus)
       
    def init_imu(self, bus):
        # Store the I2C bus object
        self.bus = bus

        # Set IMU into config mode before changing modes
        self.bus.write_byte_data(DEV_ADDR, OPR_MODE_ADDR, CONFIG_MODE)

        # Confirm config mode
        opr_mode = self.bus.read_byte_data(DEV_ADDR, OPR_MODE_ADDR)
        if opr_mode == 0:
            # Switch to NDOF mode (9 DoF sensor fusion)
            self.bus.write_byte_data(DEV_ADDR, OPR_MODE_ADDR, NDOF_MODE)

            # Read back the operation mode to confirm
            opr_mode = self.bus.read_byte_data(DEV_ADDR, OPR_MODE_ADDR)
            if opr_mode != 12:
                print(opr_mode)
                raise RuntimeError("IMU Error")
            else:
                print("IMU INIT DONE")

    def read_pitch(self):
        # Read 2 bytes from pitch registers
        data = self.bus.read_i2c_block_data(DEV_ADDR, PITCH_LSB, 2)
        
        # Combine bytes to 16-bit value
        pitch = ((data[1] << 8) | data[0]) & 0xffff

        # Convert from two's complement if value is negative
        if pitch > 32767:
            pitch -= 65536

        # Scale value and shift range by +90 degrees
        return (pitch / 16) + 90

    def read_gyro(self):
        # Read 2 bytes from gyro Y-axis registers
        data = self.bus.read_i2c_block_data(DEV_ADDR, GYRO_Y_LSB, 2)

        # Combine bytes to 16-bit value
        gyro_y = ((data[1] << 8) | data[0]) & 0xffff

        # Convert from two's complement if value is negative
        if gyro_y > 32767:
            gyro_y -= 65536

        # Scale gyro value
        return (gyro_y / 16)

# Main code block
if __name__ == "__main__":
    # Create IMU object
    imu = IMU()

    # Initialize array to store timestamp, pitch, and gyro values
    plotData = np.zeros((DEBBUG_LENGTH, 3))

    # Record start time
    startTime = time.clock_gettime(0)

    # Data collection loop
    for i in range(DEBBUG_LENGTH):
        # Read pitch and gyro values
        pitch = imu.read_pitch()
        gyro_y = imu.read_gyro()

        # Store values in array
        plotData[i, 1] = pitch
        plotData[i, 2] = gyro_y
        plotData[i, 0] = time.clock_gettime(0) - startTime

        # Print values to console
        print("pitch: %f vel_y: %f" % (pitch, gyro_y))

        # Wait 10 ms before next sample
        time.sleep(0.01)

    # Plot pitch over time
    plt.plot(plotData[:, 0], plotData[:, 1:2])
    
    # Save plot to file
    plt.savefig("imu.png")

    # Convert data to DataFrame and export to CSV
    DF = pd.DataFrame(plotData)
    DF.to_csv("IMU.csv")

    # Optional: show plot and keep program running (commented out)
    # plt.show()
    # while True:
    #     time.sleep(1)
