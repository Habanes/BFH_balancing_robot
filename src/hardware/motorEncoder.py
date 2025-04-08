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

    def update(self):
        now = time.monotonic()
        dt = now - self._last_time

        current_steps = -self.encoder.steps if self.invert_direction else self.encoder.steps
        delta_steps = current_steps - self._last_steps

        if dt == 0:
            print(f"[WARNING] dt=0, skipping velocity update.")
            return

        raw_velocity = delta_steps / dt
        self.velocity = raw_velocity

        direction = "LEFT" if self.invert_direction else "RIGHT"

        print(f"[ENCODER {direction}]")
        print(f"  steps (prev -> now): {self._last_steps} -> {current_steps}")
        print(f"  delta_steps: {delta_steps}")
        print(f"  dt: {dt:.6f} s")
        print(f"  velocity: {self.velocity:.2f} steps/sec")
        print("")

    self._last_steps = current_steps
    self._last_time = now

    def get_velocity(self) -> float:
        return self.velocity

    def get_steps(self) -> float:
        return -self.encoder.steps if self.invert_direction else self.encoder.steps
