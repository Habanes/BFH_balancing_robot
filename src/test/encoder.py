from gpiozero import RotaryEncoder
import time
import numpy as np
import matplotlib.pyplot as plt

SAMPLE_COUNT = 1000

ENCODER_LEFT_A = 19
ENCODER_LEFT_B = 20
ENCODER_RIGHT_A = 9
ENCODER_RIGHT_B = 10

class MotorEncoder:
    def __init__(self, is_left: bool):
        self.invert_direction = is_left
        pin_a = ENCODER_LEFT_A if is_left else ENCODER_RIGHT_A
        pin_b = ENCODER_LEFT_B if is_left else ENCODER_RIGHT_B

        self.encoder = RotaryEncoder(
            pin_a,
            pin_b,
            max_steps=(256 * 21) / 2,
            wrap=False
        )
        self.steps = 0.0

    def read(self) -> float:
        self.steps = -self.encoder.steps if self.invert_direction else self.encoder.steps
        return self.steps

if __name__ == "__main__":
    encoder_left = MotorEncoder(is_left=True)
    encoder_right = MotorEncoder(is_left=False)

    readings = np.zeros((SAMPLE_COUNT, 2))

    for i in range(SAMPLE_COUNT):
        print(f"Left: {encoder_left.steps:.2f}  Right: {encoder_right.steps:.2f}")
        readings[i, 0] = encoder_left.read()
        readings[i, 1] = encoder_right.read()
        time.sleep(0.01)

    plt.plot(readings)
    plt.savefig("plot_encoder.png")
