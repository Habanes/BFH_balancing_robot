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
        self.previous_steps = 0.0
        self.steps_traveled = 0.0  # Cumulative distance traveled

    def get_steps(self) -> float:
        """Get absolute position (can be positive or negative)"""
        # Return signed step count based on motor side
        self.steps = -self.encoder.steps if self.invert_direction else self.encoder.steps
        return self.steps
    
    def update_travel_distance(self) -> float:
        """Update cumulative travel distance (always positive)"""
        current_steps = self.get_steps()
        step_delta = abs(current_steps - self.previous_steps)
        self.steps_traveled += step_delta
        self.previous_steps = current_steps
        return self.steps_traveled
    
    def get_travel_distance(self) -> float:
        """Get total distance traveled (always positive)"""
        return self.steps_traveled
    
    def reset_travel_distance(self):
        """Reset the cumulative travel distance counter"""
        self.steps_traveled = 0.0
        self.previous_steps = self.get_steps()
