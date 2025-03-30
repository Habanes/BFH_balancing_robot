from gpiozero import RotaryEncoder

# GPIO pin mappings for rotary encoders
ENCODER_LEFT_A = 19
ENCODER_LEFT_B = 20
ENCODER_RIGHT_A = 9
ENCODER_RIGHT_B = 10

class MotorEncoder:
    def __init__(self, is_left: bool):
        self.invert_direction = is_left

        # Select correct encoder pins based on motor side
        pin_a = ENCODER_LEFT_A if is_left else ENCODER_RIGHT_A
        pin_b = ENCODER_LEFT_B if is_left else ENCODER_RIGHT_B

        # Initialize rotary encoder with gear ratio and no wrapping
        self.encoder = RotaryEncoder(
            pin_a,
            pin_b,
            max_steps=(256 * 21) / 2,
            wrap=False
        )

        self.steps = 0.0

    def read(self) -> float:
        # Return signed step count based on motor side
        self.steps = -self.encoder.steps if self.invert_direction else self.encoder.steps
        return self.steps
