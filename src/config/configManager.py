import os
from typing import List
import logging

class ConfigManager:
    def __init__(self):
        print("LOADING CONFIG")
        
        self.loopUpadeRate = 1000
        self.loopInterval = 1 / self.loopUpadeRate
        
        self.angleoffset = 4
        self.angleMove = 1
        self.angleNeutral = 0 + self.angleoffset
    
        self.angleRotationSpeed = 90
        self.angleRotation = self.angleRotationSpeed / self.loopUpadeRate
        
        self.angleLimit = 50
        
        
# Create a single ConfigManager instance
global_config = ConfigManager()