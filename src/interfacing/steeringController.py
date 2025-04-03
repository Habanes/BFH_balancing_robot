from src.config.configManager import global_config

class steeringController:
    def __init__(self):
        self.angleYOffset = 0.0
        self.angleY = global_config.angleNeutral + self.angleYOffset
        self.angleZ = 0.0
        self.kpY = global_config.init_kp
        self.kiY = global_config.init_ki
        self.kdY = global_config.init_kd

    def getAngleY(self):
        return self.angleY

    def getAngleZ(self):
        return self.angleZ

    def setAngleY(self, angle):
        self.angleY = angle

    def setAngleZ(self, angle):
        self.angleZ = angle

    def getKpY(self):
        return self.kpY

    def getKiY(self):
        return self.kiY

    def getKdY(self):
        return self.kdY
    
    def getAngleYOffset(self):
        return self.angleYOffset

    def setKpY(self, value):
        self.kpY = value

    def setKiY(self, value):
        self.kiY = value

    def setKdY(self, value):
        self.kdY = value
        
    def setAngleYOffset(self, value):
        self.angleYOffset = value
        self.angleY = global_config.angleNeutral + self.angleYOffset

    def goForward(self):
        self.angleY = global_config.angleMove

    def goBackward(self):
        self.angleY = - global_config.angleMove
        
    def rotateRight(self):
        self.angleY = global_config.angleNeutral
        self.angleZ += global_config.angleRotation
        
    def rotateLeft(self):
        self.angleY = global_config.angleNeutral
        self.angleZ -= global_config.angleRotation
