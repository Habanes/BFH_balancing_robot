from gpiozero import RotaryEncoder
import time

# GPIO pin mappings for rotary encoders
ENCODER_LEFT_A = 19
ENCODER_LEFT_B = 20
ENCODER_RIGHT_A = 9
ENCODER_RIGHT_B = 10

class MotorEncoder:
    def __init__(self, is_left: bool):
        self.invert_direction = is_left
        pin_a = ENCODER_LEFT_A if is_left else ENCODER_RIGHT_A
        pin_b = ENCODER_LEFT_B if is_left else ENCODER_RIGHT_B

        self.encoder = RotaryEncoder(pin_a, pin_b, max_steps=(256 * 21) / 2, wrap=False)
        self._last_steps = 0.0
        self._last_time = time.monotonic()
        self.velocity = 0.0  # steps per second

        # Smoothing and limits
        self._alpha = 0.2  # exponential smoothing factor
        self._max_step_jump = 1000
        self._min_dt = 0.001   # 1 ms
        self._max_dt = 0.5     # 500 ms

    def update(self):
        now = time.monotonic()
        dt = now - self._last_time

        # Reject unreasonable timing
        if dt < self._min_dt or dt > self._max_dt:
            self._last_time = now
            return

        current_steps = -self.encoder.steps if self.invert_direction else self.encoder.steps
        delta_steps = current_steps - self._last_steps

        # Reject large step jumps
        if abs(delta_steps) > self._max_step_jump:
            self._last_time = now
            return

        raw_velocity = delta_steps / dt

        # Apply exponential smoothing
        self.velocity = (1 - self._alpha) * self.velocity + self._alpha * raw_velocity

        self._last_steps = current_steps
        self._last_time = now
        
        print(f"VELOCITY FOR MOTOR IS LEFT = {self.invert_direction}: {self.velocity}, raw_velocity: {raw_velocity}, dt: {dt}")

    def get_velocity(self) -> float:
        return self.velocity

    def get_steps(self) -> float:
        return -self.encoder.steps if self.invert_direction else self.encoder.steps
