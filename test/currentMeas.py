import smbus2 as smbus
import matplotlib.pyplot as plt
import time
import numpy as np


DEBBUG_LENGTH = 1000

DEV_BUS = 1
DEV_ADDR = 0x4B 
DEV_ADDR_2 = 0x4D


class CurrentMeas:
    def __init__(self,left_right = False,bus=smbus.SMBus(DEV_BUS)) -> None:
        self.init(left_right,bus)

    def init(self,left_right,bus):
       self.left_right = left_right
       self.bus = bus


    def getCurrent(self):
        data = self.bus.read_i2c_block_data(DEV_ADDR if self.left_right else DEV_ADDR_2,0x00,2)

        meas = ((data[1]>>2) | (data[0]<<6))&0x3FF
        meas += -2*(meas & 0x200) #get negative values from twos complement   
        return meas




if __name__=="__main__":
    current_1 = CurrentMeas(left_right=True)
    current_2 = CurrentMeas(left_right=False)
     
    plotData = np.zeros((DEBBUG_LENGTH,2))

    for i in range(DEBBUG_LENGTH):
        
        plotData[i,0] = current_1.getCurrent()
        plotData[i,1] = current_2.getCurrent()
        print("Current 1: %f  Curent 2: %f"%(plotData[i,0],plotData[i,1]))
        
        time.sleep(0.01)
        

    plt.plot(plotData)
    plt.savefig("plot_encoder.png")
    # plt.show()
    # while True:
    #     time.sleep(1)
