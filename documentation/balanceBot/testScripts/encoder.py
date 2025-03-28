from gpiozero import RotaryEncoder
import time
import numpy as np
import matplotlib.pyplot as plt


DEBBUG_LENGTH = 1000
A_PIN  = 19
B_PIN  = 20
A_PIN_2 = 9
B_PIN_2 = 10


class Encoder:
    def __init__(self,left_right):

        self.inverse_dir = left_right
        self.steps = 0.0
        
        #self.encoder = RotaryEncoder(self.encoder_a_pin_nr,self.encoder_b_pin_nr,max_steps=0,wrap=True)
        self.encoder = RotaryEncoder(A_PIN if left_right else A_PIN_2,B_PIN if left_right else B_PIN_2,max_steps=(256*21)/2,wrap=False)#absolut position for the wheel
    
        
    def get_steps(self):
        self.steps = self.encoder.steps
        if self.inverse_dir:
            self.steps = - self.steps
        return self.steps
    
    





if __name__=="__main__":
    encoder_1 = Encoder(left_right=True)
    encoder_2 = Encoder(left_right=False)
     
    plotData = np.zeros((DEBBUG_LENGTH,2))

    for i in range(DEBBUG_LENGTH):
        
        
        
        print("Pos Motor 1: %f  Pos Motor 2: %f"%(encoder_1.steps,encoder_2.steps))
        plotData[i,0] = encoder_1.get_steps()
        plotData[i,1] = encoder_2.get_steps()
        
        time.sleep(0.01)
        

    plt.plot(plotData)
    plt.savefig("plot_encoder.png")
    # plt.show()
    # while True:
    #     time.sleep(1)