from simple_pid import PID

class AngleController:
    def __init__(self, kp, ki, kd, setpoint=0.0, output_limits=(-1.0, 1.0)):
        # Initialize PID controller with gains and output limits
        self.pid = PID(kp, ki, kd, setpoint=setpoint)
        self.pid.output_limits = output_limits

    def update(self, current_angle: float) -> float:
        # Compute control output based on current angle
        return self.pid(current_angle)
    
    def setTargetAngle(self, targetAngle):
        self.pid.setpoint = targetAngle

    def setKp(self, kp):
        self.pid.Kp = kp

    def setKi(self, ki):
        self.pid.Ki = ki

    def setKd(self, kd):
        self.pid.Kd = kd
