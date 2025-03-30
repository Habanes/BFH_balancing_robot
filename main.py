from src.interfacing.imu import IMU
from src.interfacing.motorController import MotorController
from src.interfacing.currentSensor import CurrentSensor
from src.control.angleEsimater import AngleEstimator
from src.control.angleController import AngleController
from src.control.torqueController import TorqueController
from src.config.configManager import global_config
from src.log.logManager import global_log_manager
import time

# === Initialization ===

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
INNER_HZ = 500
OUTER_HZ = 100
LOOP_DT = 1.0 / INNER_HZ
OUTER_DIVIDER = int(INNER_HZ / OUTER_HZ)

LOG_INTERVAL = 0.25
last_log_time = time.time()
TEST_MODE = global_config.test_mode

if TEST_MODE:
    global_log_manager.log_info("Running in TEST MODE (torque only)", location="main")
    target_torque = 0.2

try:
    counter = 0
    while True:
        angle = angle_estimator.get_angle()

        if abs(angle) > 45:
            global_log_manager.log_critical(f"Angle exceeded safe limit: {angle:.2f}. Stopping motors.", location="safety")
            motor_left.stop()
            motor_right.stop()
            break

        # Update outer loop every OUTER_DIVIDER cycles
        if not TEST_MODE and counter % OUTER_DIVIDER == 0:
            target_torque = angle_pid.update(angle)

        pwm_left = torque_pid_left.update(target_torque)
        pwm_right = torque_pid_right.update(target_torque)

        motor_left.set_speed(pwm_left)
        motor_right.set_speed(pwm_right)

        if time.time() - last_log_time >= LOG_INTERVAL:
            set_angle = angle_pid.pid.setpoint
            raw_angle = imu.read_pitch()  # You could cache this inside AngleEstimator if needed
            est_angle = angle
            angle_error = set_angle - est_angle
            measured_torque_L = torque_pid_left._current_to_torque(current_left.read_current())
            measured_torque_R = torque_pid_right._current_to_torque(current_right.read_current())

            global_log_manager.log_debug(
                f"set={set_angle:.2f} angle={raw_angle:.2f} est={est_angle:.2f} err={angle_error:.2f} "
                f"tgtT={target_torque:.2f} measT_L={measured_torque_L:.2f} measT_R={measured_torque_R:.2f} "
                f"pwmL={pwm_left:.2f} pwmR={pwm_right:.2f}",
                location="loop"
            )
            last_log_time = time.time()
            
        counter += 1
        time.sleep(LOOP_DT)

except KeyboardInterrupt:
    global_log_manager.log_warning("KeyboardInterrupt detected. Stopping motors.", location="main")
    motor_left.stop()
    motor_right.stop()
    global_log_manager.log_info("Shutdown complete", location="main")
