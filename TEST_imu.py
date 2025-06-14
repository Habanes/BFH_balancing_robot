import smbus2 as smbus
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from src.config.configManager import global_config


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
        
        # Use same variable and logic as main IMU
        # Subtract offset so when IMU reads +6.7°, we return 0° (upright)
        angle_degrees = (pitch/16) + 90 - global_config.imu_mounting_offset
        return angle_degrees
        return angle_degrees


    def read_gyro(self):

            data = self.bus.read_i2c_block_data(DEV_ADDR,GYRO_Y_LSB,2)
            gyro_y = ((data[1] << 8) | data[0]) & 0xffff

            if gyro_y > 32767:
                gyro_y -= 65536
            return (gyro_y/16)
        






