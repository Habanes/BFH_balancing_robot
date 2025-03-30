from src.interfacing.imu import IMU
from src.interfacing.motorController import MotorController
from src.interfacing.currentSensor import CurrentSensor
from control.angleEsimater import AngleEstimator
from control.angleController import AngleController
from control.torqueController import TorqueController
from config.configManager import ConfigManager
from log.logManager import LogManager
import time

# === Initialization ===
# Create a single ConfigManager instance
global_config = ConfigManager()
global_log_manager = global_log_manager = LogManager(print_to_console=global_config.print_to_console, debug_mode=global_config.debug_mode)

global_log_manager.log_info("Initializing components", location="main")
imu = IMU()
angle_estimator = AngleEstimator(imu)

motor_left = MotorController(is_left=True)
motor_right = MotorController(is_left=False)

current_left = CurrentSensor(is_left=True)
current_right = CurrentSensor(is_left=False)

global_log_manager.log_info("Components initialized", location="main")

# === PID Controllers ===
angle_pid = AngleController(kp=30.0, ki=0.0, kd=0.5)
torque_pid_left = TorqueController(current_left, kp=0.0, ki=0.5, kd=0.0)
torque_pid_right = TorqueController(current_right, kp=0.0, ki=0.5, kd=0.0)

# === Start motors ===
global_log_manager.log_info("Starting motors", location="main")
motor_left.start()
motor_right.start()

# === Control Loop ===
LOOP_HZ = 100
LOOP_DT = 1.0 / LOOP_HZ
LOG_INTERVAL = 0.25  # Log once every 0.25 seconds
last_log_time = time.time()

TEST_MODE = global_config.test_mode  # Set this flag in your config

if TEST_MODE:
    global_log_manager.log_info("Running in TEST MODE (torque only)", location="main")
    target_torque = 0.5  # fixed target for testing

try:
    while True:
        angle = angle_estimator.get_angle()

        if abs(angle) > 45:
            global_log_manager.log_critical(f"Angle exceeded safe limit: {angle:.2f}. Stopping motors.", location="safety")
            motor_left.stop()
            motor_right.stop()
            break

        if TEST_MODE:
            pwm_left = torque_pid_left.update(target_torque)
            pwm_right = torque_pid_right.update(target_torque)
        else:
            target_torque = angle_pid.update(angle)
            pwm_left = torque_pid_left.update(target_torque)
            pwm_right = torque_pid_right.update(target_torque)

        motor_left.set_speed(pwm_left)
        motor_right.set_speed(pwm_right)

        current_time = time.time()
        if current_time - last_log_time >= LOG_INTERVAL:
            global_log_manager.log_debug(f"angle={angle:.2f}, torque={target_torque:.2f}, pwmL={pwm_left:.2f}, pwmR={pwm_right:.2f}", location="loop")
            last_log_time = current_time

        time.sleep(LOOP_DT)

except KeyboardInterrupt:
    global_log_manager.log_warning("KeyboardInterrupt detected. Stopping motors.", location="main")
    motor_left.stop()
    motor_right.stop()
    global_log_manager.log_info("Shutdown complete", location="main")
