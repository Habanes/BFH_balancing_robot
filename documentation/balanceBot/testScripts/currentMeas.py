import smbus2 as smbus               # Library for I2C communication
import matplotlib.pyplot as plt      # Library for plotting graphs
import time                          # Library for time-related functions (used for delays)
import numpy as np                   # Library for numerical operations and arrays

# Number of data points to collect for debugging/plotting
DEBBUG_LENGTH = 1000

# I2C bus number (usually 1 on Raspberry Pi)
DEV_BUS = 1

# I2C addresses for the two ADCs measuring current
DEV_ADDR = 0x4B       # Presumably left motor
DEV_ADDR_2 = 0x4D     # Presumably right motor

# Class to handle current measurement over I2C
class CurrentMeas:
    def __init__(self, left_right=False, bus=smbus.SMBus(DEV_BUS)) -> None:
        # Initialize the object with left/right flag and I2C bus instance
        self.init(left_right, bus)

    def init(self, left_right, bus):
        # Store left/right flag and I2C bus in instance variables
        self.left_right = left_right
        self.bus = bus

    def getCurrent(self):
        # Read 2 bytes from the appropriate I2C address (left or right motor ADC)
        data = self.bus.read_i2c_block_data(DEV_ADDR if self.left_right else DEV_ADDR_2, 0x00, 2)

        # Combine the two bytes into a 10-bit value
        meas = ((data[1] >> 2) | (data[0] << 6)) & 0x3FF

        # Convert from two's complement if value is negative (bit 9 is sign bit)
        meas += -2 * (meas & 0x200)

        # Return the signed current measurement
        return meas


# Main block: only executed when running this file directly
if __name__ == "__main__":
    # Create current measurement objects for both motors
    current_1 = CurrentMeas(left_right=True)
    current_2 = CurrentMeas(left_right=False)
    
    # Initialize array to store current data for plotting
    plotData = np.zeros((DEBBUG_LENGTH, 2))

    # Collect data over time
    for i in range(DEBBUG_LENGTH):
        # Measure current from both sensors
        plotData[i, 0] = current_1.getCurrent()
        plotData[i, 1] = current_2.getCurrent()

        # Print current values to console
        print("Current 1: %f  Curent 2: %f" % (plotData[i, 0], plotData[i, 1]))

        # Wait 10 ms before next sample
        time.sleep(0.01)
    
    # Plot the collected current data
    plt.plot(plotData)
    
    # Save the plot to a file
    plt.savefig("plot_encoder.png")
    
    # Optionally, show the plot window (currently commented out)
    # plt.show()
    
    # Optionally, keep script running after collection (currently commented out)
    # while True:
    #     time.sleep(1)
