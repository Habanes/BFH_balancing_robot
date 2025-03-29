from gpiozero import RotaryEncoder     # Import class to interface with rotary encoders
import time                            # For timing/sleep
import numpy as np                     # For numerical operations and arrays
import matplotlib.pyplot as plt        # For plotting

# Number of data points to record for debugging
DEBBUG_LENGTH = 1000

# GPIO pins for encoder 1 (motor 1)
A_PIN  = 19
B_PIN  = 20

# GPIO pins for encoder 2 (motor 2)
A_PIN_2 = 9
B_PIN_2 = 10


# Class to read rotary encoder values
class Encoder:
    def __init__(self, left_right):
        # Whether to invert direction for this encoder
        self.inverse_dir = left_right

        # Internal variable to store the number of steps
        self.steps = 0.0
        
        # Initialize the RotaryEncoder object with appropriate pins
        # 'wrap=False' so the value does not wrap but gives absolute position
        # Max steps: 256 pulses per revolution * 21 gear ratio / 2 (quadrature encoding)
        self.encoder = RotaryEncoder(
            A_PIN if left_right else A_PIN_2,
            B_PIN if left_right else B_PIN_2,
            max_steps=(256 * 21) / 2,
            wrap=False
        )
    
    def get_steps(self):
        # Read encoder steps and store in self.steps
        self.steps = self.encoder.steps

        # Invert direction if necessary
        if self.inverse_dir:
            self.steps = -self.steps

        # Return the step count
        return self.steps


# Main block: executed only if this script is run directly
if __name__ == "__main__":
    # Create encoder objects for both motors
    encoder_1 = Encoder(left_right=True)
    encoder_2 = Encoder(left_right=False)
     
    # Initialize array to store encoder positions for both motors
    plotData = np.zeros((DEBBUG_LENGTH, 2))

    # Collect data over time
    for i in range(DEBBUG_LENGTH):
        # Print current encoder positions
        print("Pos Motor 1: %f  Pos Motor 2: %f" % (encoder_1.steps, encoder_2.steps))

        # Read and store encoder step values
        plotData[i, 0] = encoder_1.get_steps()
        plotData[i, 1] = encoder_2.get_steps()
        
        # Wait 10 ms before next read
        time.sleep(0.01)

    # Plot recorded encoder data
    plt.plot(plotData)
    
    # Save the plot to a PNG file
    plt.savefig("plot_encoder.png")

    # Optional: show the plot interactively (commented out)
    # plt.show()

    # Optional: keep script running (commented out)
    # while True:
    #     time.sleep(1)
