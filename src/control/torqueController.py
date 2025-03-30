# torque_controller.py
from simple_pid import PID

class TorqueController:
    def __init__(self, current_sensor, kp, ki, kd, output_limits=(-1.0, 1.0)):
        self.current_sensor = current_sensor
        self.pid = PID(kp, ki, kd)
        self.pid.output_limits = output_limits

    def update(self, target_torque: float) -> float:
        # Read measured current and convert to torque
        measured_current = self.current_sensor.read_current()
        measured_torque = self._current_to_torque(measured_current)

        # PID input is the torque error
        return self.pid(measured_torque - target_torque)

    def _current_to_torque(self, current: float) -> float:
        TORQUE_CONSTANT = 1.0  # Needs calibration
        return current * TORQUE_CONSTANT
