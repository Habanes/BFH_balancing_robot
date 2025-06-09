from TEST_currentMeas import CurrentMeas
from TEST_motor import Motor
from TEST_encoder import Encoder
from TEST_imu import IMU
import numpy as np
import matplotlib.pyplot as plt
import time
import smbus2 as smbus


DEBBUG_LENGTH=100

DEV_BUS = 1

if __name__ == "__main__":
    plotData = np.zeros((DEBBUG_LENGTH,5))
    plotTime = np.zeros((DEBBUG_LENGTH,1))

    bus = smbus.SMBus(DEV_BUS)
    motor_1 = Motor(left_right=True)
    motor_2 = Motor(left_right=False)
    encoder_1 = Encoder(left_right=True)
    encoder_2 = Encoder(left_right=False)
    imu = IMU(bus)
    current_1 = CurrentMeas(left_right=True,bus=bus)
    current_2 = CurrentMeas(left_right=False,bus=bus)

    motor_1.start_pwm()
    motor_2.start_pwm()
    timeStart = time.time()
    for i in range(DEBBUG_LENGTH):

        if i < DEBBUG_LENGTH/2:
            pwm = ((float(i)/(float(DEBBUG_LENGTH/2)))*1.0)
        else:
            pwm = ((float(DEBBUG_LENGTH-i)/(float(DEBBUG_LENGTH/2)))*1.0)

        motor_1.write_pwm(pwm)
        motor_2.write_pwm(pwm)
        pos1 = encoder_1.get_steps()
        pos2 = encoder_2.get_steps()
        
        currMeas = [current_1.getCurrent(),current_2.getCurrent()]
        pitch = imu.read_pitch()
        
        plotData[i,0]=currMeas[0]
        plotData[i,1]=currMeas[1]
        plotData[i,2]=pos1
        plotData[i,3]=pos2
        plotData[i,4]=pitch
        plotTime[i] = time.time()-timeStart

        
        print(pwm)
        time.sleep(0.01)

    motor_1.stop_pwm()
    motor_2.stop_pwm()

    print("fettig")
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
    ax1.plot(plotTime[5:],plotData[5:,0:2])
    ax1.set_title('Currents')
    ax2.plot(plotTime[5:],plotData[5:,2:4])
    ax2.set_title('Positions')
    ax3.plot(plotTime[5:],plotData[5:,4])
    ax3.set_title('Pitch')
    ax3.set_xlabel('Time')


    # plt.show()
    plt.savefig("plot_HW.png")
    # while True:
    #     time.sleep(1)










