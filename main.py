import time

from io.imu import IMU
from io.motorController import MotorController
from io.currentSensor import CurrentSensor
from control.angleEsimater import AngleEstimator
from control.angleController import AngleController
from control.torqueController import TorqueController

# === Initialization ===
imu = IMU()
angle_estimator = AngleEstimator(imu)

motor_left = MotorController(is_left=True)
motor_right = MotorController(is_left=False)

current_left = CurrentSensor(is_left=True)
current_right = CurrentSensor(is_left=False)

# === PID Controllers ===
angle_pid = AngleController(kp=30.0, ki=0.0, kd=0.5)
torque_pid_left = TorqueController(current_left, kp=0.0, ki=0.5, kd=0.0)
torque_pid_right = TorqueController(current_right, kp=0.0, ki=0.5, kd=0.0)

# === Start motors ===
motor_left.start()
motor_right.start()

# === Control Loop ===
LOOP_HZ = 100
LOOP_DT = 1.0 / LOOP_HZ

try:
    while True:
        angle = angle_estimator.get_angle()
        target_torque = angle_pid.update(angle)

        pwm_left = torque_pid_left.update(target_torque)
        pwm_right = torque_pid_right.update(target_torque)

        motor_left.set_speed(pwm_left)
        motor_right.set_speed(pwm_right)

        time.sleep(LOOP_DT)

except KeyboardInterrupt:
    print("Shutting down...")
    motor_left.stop()
    motor_right.stop()
