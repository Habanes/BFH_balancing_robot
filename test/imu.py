import smbus2 as smbus
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


DEBBUG_LENGTH = 1000

DEV_BUS = 1
DEV_ADDR = 0x28
OPR_MODE_ADDR = 0x3d
NDOF_MODE = 0b1100
CONFIG_MODE = 0b0000
PITCH_MSB = 0x1f
PITCH_LSB = 0x1e
PAGE_ID = 0x07
GYRO_Y_MSB = 0x17
GYRO_Y_LSB = 0x16

class IMU:
    def __init__(self,bus=smbus.SMBus(DEV_BUS)) -> None:
        self.init_imu(bus)
       
                
    def init_imu(self,bus):
        self.bus=bus

        self.bus.write_byte_data(DEV_ADDR,OPR_MODE_ADDR,CONFIG_MODE) # Set into config mode
        opr_mode = self.bus.read_byte_data(DEV_ADDR,OPR_MODE_ADDR)
        if opr_mode == 0:
            self.bus.write_byte_data(DEV_ADDR,OPR_MODE_ADDR,NDOF_MODE) # Set into 9DOF mode
            opr_mode = self.bus.read_byte_data(DEV_ADDR,OPR_MODE_ADDR)
            if opr_mode != 12:
                print(opr_mode)
                raise RuntimeError("IMU Error")
            else:
                print("IMU INIT DONE")
        

        
    def read_pitch(self):

            data = self.bus.read_i2c_block_data(DEV_ADDR,PITCH_LSB,2)
            pitch = ((data[1] << 8) | data[0]) & 0xffff

            if pitch > 32767:
                pitch -= 65536
            return (pitch/16)+90


    def read_gyro(self):

            data = self.bus.read_i2c_block_data(DEV_ADDR,GYRO_Y_LSB,2)
            gyro_y = ((data[1] << 8) | data[0]) & 0xffff

            if gyro_y > 32767:
                gyro_y -= 65536
            return (gyro_y/16)
            
    
if __name__ == "__main__":

    imu = IMU()
    plotData = np.zeros((DEBBUG_LENGTH,3))
    startTime = time.clock_gettime(0)
    for i in range(DEBBUG_LENGTH):
        pitch = imu.read_pitch()
        gyro_y = imu.read_gyro()
        plotData[i,1] = pitch
        plotData[i,2] = gyro_y
        plotData[i,0] = time.clock_gettime(0)-startTime
        print("pitch: %f vel_y: %f"%(pitch,gyro_y))
        time.sleep(0.01)
        

    plt.plot(plotData[:,0],plotData[:,1:2])
    plt.savefig("imu.png")
    DF = pd.DataFrame(plotData)
    DF.to_csv("IMU.csv")
    # plt.show()
    # while True:
    #     time.sleep(1)


        






