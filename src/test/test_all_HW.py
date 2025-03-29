from currentMeas import CurrentSensor
from motor import MotorController
from encoder import MotorEncoder
from imu import IMU

import numpy as np
import matplotlib.pyplot as plt
import time
import smbus2 as smbus

SAMPLE_COUNT = 100
I2C_BUS_ID = 1

if __name__ == "__main__":
    data = np.zeros((SAMPLE_COUNT, 5))  # current_left, current_right, pos_left, pos_right, pitch
    timestamps = np.zeros((SAMPLE_COUNT, 1))

    bus = smbus.SMBus(I2C_BUS_ID)

    motor_left = MotorController(is_left=True)
    motor_right = MotorController(is_left=False)

    encoder_left = MotorEncoder(is_left=True)
    encoder_right = MotorEncoder(is_left=False)

    imu = IMU(bus)

    current_left = CurrentSensor(is_left=True, bus=bus)
    current_right = CurrentSensor(is_left=False, bus=bus)

    motor_left.start()
    motor_right.start()

    t0 = time.time()

    for i in range(SAMPLE_COUNT):
        if i < SAMPLE_COUNT / 2:
            pwm = i / (SAMPLE_COUNT / 2)
        else:
            pwm = (SAMPLE_COUNT - i) / (SAMPLE_COUNT / 2)

        motor_left.set_speed(pwm)
        motor_right.set_speed(pwm)

        data[i, 0] = current_left.read_current()
        data[i, 1] = current_right.read_current()
        data[i, 2] = encoder_left.read()
        data[i, 3] = encoder_right.read()
        data[i, 4] = imu.read_pitch()
        timestamps[i] = time.time() - t0

        print(f"PWM: {pwm:.2f}")
        time.sleep(0.01)

    motor_left.stop()
    motor_right.stop()

    print("done")

    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)

    ax1.plot(timestamps[5:], data[5:, 0:2])
    ax1.set_title("Currents")

    ax2.plot(timestamps[5:], data[5:, 2:4])
    ax2.set_title("Positions")

    ax3.plot(timestamps[5:], data[5:, 4])
    ax3.set_title("Pitch")
    ax3.set_xlabel("Time")

    plt.savefig("plot_HW.png")
