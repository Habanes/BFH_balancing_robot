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
        self.previous_steps = 0.0
        self.steps_traveled = 0.0  # Cumulative distance traveled
        
        #self.encoder = RotaryEncoder(self.encoder_a_pin_nr,self.encoder_b_pin_nr,max_steps=0,wrap=True)
        self.encoder = RotaryEncoder(A_PIN if left_right else A_PIN_2,B_PIN if left_right else B_PIN_2,max_steps=(256*21)/2,wrap=False)#absolut position for the wheel
    
        
    def get_steps(self):
        """Get absolute position (can be positive or negative)"""
        self.steps = self.encoder.steps
        if self.inverse_dir:
            self.steps = - self.steps
        return self.steps
    
    def update_travel_distance(self):
        """Update cumulative travel distance (always positive)"""
        current_steps = self.get_steps()
        step_delta = abs(current_steps - self.previous_steps)
        self.steps_traveled += step_delta
        self.previous_steps = current_steps
        return self.steps_traveled
    
    def get_travel_distance(self):
        """Get total distance traveled (always positive)"""
        return self.steps_traveled
    
    def reset_travel_distance(self):
        """Reset the cumulative travel distance counter"""
        self.steps_traveled = 0.0
        self.previous_steps = self.get_steps()

if __name__=="__main__":
    encoder_1 = Encoder(left_right=True)
    encoder_2 = Encoder(left_right=False)
     
    plotData = np.zeros((DEBBUG_LENGTH,4))  # Now storing 4 values: abs_pos1, abs_pos2, travel1, travel2
    
    # Initialize travel distance tracking
    encoder_1.reset_travel_distance()
    encoder_2.reset_travel_distance()

    for i in range(DEBBUG_LENGTH):
        # Get absolute positions
        abs_pos_1 = encoder_1.get_steps()
        abs_pos_2 = encoder_2.get_steps()
        
        # Update and get travel distances
        travel_1 = encoder_1.update_travel_distance()
        travel_2 = encoder_2.update_travel_distance()
        
        print("Motor 1 - Abs: %6.0f  Travel: %6.0f  |  Motor 2 - Abs: %6.0f  Travel: %6.0f" % 
              (abs_pos_1, travel_1, abs_pos_2, travel_2))
        
        plotData[i,0] = abs_pos_1
        plotData[i,1] = abs_pos_2
        plotData[i,2] = travel_1
        plotData[i,3] = travel_2
        
        time.sleep(0.01)
        

    # Create subplots for better visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Plot absolute positions
    ax1.plot(plotData[:, 0], label='Motor 1 (Left) - Absolute', color='blue')
    ax1.plot(plotData[:, 1], label='Motor 2 (Right) - Absolute', color='red')
    ax1.set_title('Absolute Position (Steps from Start)')
    ax1.set_ylabel('Steps')
    ax1.legend()
    ax1.grid(True)
    
    # Plot travel distances
    ax2.plot(plotData[:, 2], label='Motor 1 (Left) - Travel Distance', color='cyan')
    ax2.plot(plotData[:, 3], label='Motor 2 (Right) - Travel Distance', color='orange')
    ax2.set_title('Cumulative Travel Distance (Total Steps Moved)')
    ax2.set_xlabel('Time (0.01s intervals)')
    ax2.set_ylabel('Steps')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig("plot_encoder.png", dpi=150)
    print(f"\nTest completed! Plot saved as 'plot_encoder.png'")
    print(f"Final travel distances - Motor 1: {plotData[-1,2]:.0f} steps, Motor 2: {plotData[-1,3]:.0f} steps")
    # plt.show()
    # while True:
    #     time.sleep(1)