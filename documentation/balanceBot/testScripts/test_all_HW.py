from currentMeas import CurrentMeas       # For motor current measurement
from motor import Motor                   # For controlling motor direction and PWM
from encoder import Encoder               # For reading motor position
from imu import IMU                       # For reading pitch angle
import numpy as np                        # For data storage and operations
import matplotlib.pyplot as plt           # For plotting
import time                               # For timing and delays
import smbus2 as smbus                    # For I2C communication

# Number of samples to record for debugging
DEBBUG_LENGTH = 100

# I2C bus number
DEV_BUS = 1

# Main execution block
if __name__ == "__main__":
    # Initialize data arrays: 5 values per sample (2 currents, 2 positions, 1 pitch)
    plotData = np.zeros((DEBBUG_LENGTH, 5))
    plotTime = np.zeros((DEBBUG_LENGTH, 1))

    # Create shared I2C bus
    bus = smbus.SMBus(DEV_BUS)

    # Initialize motors
    motor_1 = Motor(left_right=True)
    motor_2 = Motor(left_right=False)

    # Initialize encoders
    encoder_1 = Encoder(left_right=True)
    encoder_2 = Encoder(left_right=False)

    # Initialize IMU on shared I2C bus
    imu = IMU(bus)

    # Initialize current sensors on shared I2C bus
    current_1 = CurrentMeas(left_right=True, bus=bus)
    current_2 = CurrentMeas(left_right=False, bus=bus)

    # Start both motors with PWM enabled and ready
    motor_1.start_pwm()
    motor_2.start_pwm()

    # Record start time
    timeStart = time.time()

    # Main data collection loop
    for i in range(DEBBUG_LENGTH):
        # Linearly increase PWM for first half, decrease for second half
        if i < DEBBUG_LENGTH / 2:
            pwm = (float(i) / (DEBBUG_LENGTH / 2)) * 1.0
        else:
            pwm = (float(DEBBUG_LENGTH - i) / (DEBBUG_LENGTH / 2)) * 1.0

        # Write same PWM to both motors
        motor_1.write_pwm(pwm)
        motor_2.write_pwm(pwm)

        # Read encoder positions
        pos1 = encoder_1.get_steps()
        pos2 = encoder_2.get_steps()

        # Read motor currents
        currMeas = [current_1.getCurrent(), current_2.getCurrent()]

        # Read pitch angle from IMU
        pitch = imu.read_pitch()

        # Store data
        plotData[i, 0] = currMeas[0]
        plotData[i, 1] = currMeas[1]
        plotData[i, 2] = pos1
        plotData[i, 3] = pos2
        plotData[i, 4] = pitch
        plotTime[i] = time.time() - timeStart

        # Print current PWM value
        print(pwm)

        # Wait 10 ms before next sample
        time.sleep(0.01)

    # Stop motors after data collection
    motor_1.stop_pwm()
    motor_2.stop_pwm()

    print("fettig")  # Done

    # Create plots: currents, positions, and pitch over time
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
    
    ax1.plot(plotTime[5:], plotData[5:, 0:2])
    ax1.set_title('Currents')

    ax2.plot(plotTime[5:], plotData[5:, 2:4])
    ax2.set_title('Positions')

    ax3.plot(plotTime[5:], plotData[5:, 4])
    ax3.set_title('Pitch')
    ax3.set_xlabel('Time')

    # Save plot to file
    plt.savefig("plot_HW.png")

    # Optionally keep the script running and show the plot (commented out)
    # plt.show()
    # while True:
    #     time.sleep(1)
