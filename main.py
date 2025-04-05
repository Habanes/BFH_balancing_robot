import threading
import time
import tkinter as tk

from src.config.configManager import global_config
from src.pid.pidManager import pidManager
from src.log.logManager import global_log_manager
from src.user_input.steeringGUI import SteeringGUI
from src.hardware.motorEncoder import MotorEncoder

# === Global GUI reference ===
gui = None

# === Initialization ===
global_log_manager.log_info("Initializing components", location="main")

# Log loop config
global_log_manager.log_info(
    f"Control loops enabled: Velocity={global_config.enable_velocity_loop}, "
    f"Yaw={global_config.enable_yaw_loop}, TorqueFeedback={global_config.enable_torque_feedback_loop}",
    location="main"
)

# Use simulator if test mode is on
if global_config.test_mode:
    from src.hardware.sensorSimulator import SensorSimulator
    sim = SensorSimulator()
    imu = sim
    motor_left = sim
    motor_right = sim

else:
    from src.hardware.imu import IMU
    from src.hardware.motorController import MotorController

    imu = IMU()
    motor_encoder = MotorEncoder()
    motor_left = MotorController(is_left=True)
    motor_right = MotorController(is_left=False)

pid_manager = pidManager()

# === Control Loop ===
LOG_INTERVAL = 0.25
last_log_time = time.time()
RUNNING = True

# === Loop Timers ===
last_velocity_to_tilt_time = 0
last_tilt_to_torque_time = 0
last_estimated_torque_time = 0
last_yaw_control_time = 0

def control_loop():
    global last_log_time
    global last_velocity_to_tilt_time, last_tilt_to_torque_time, last_estimated_torque_time, last_yaw_control_time
    global gui

    start_time = time.time()
    actual_torque_output = 0.0
    torque_diff = 0.0
    
    motor_left.start()
    motor_right.start()

    while RUNNING:
        current_time = time.time()

        # === Sensor readings ===
        estimated_tilt_angle = -imu.read_pitch()
        z_angular_velocity = imu.read_gyro_z()
        measured_velocity = (motor_left.get_steps() + motor_right.get_steps()) / 2
        measured_current = (motor_left.get_current() + motor_right.get_current()) / 2

        # === Safety check ===
        if current_time - start_time > global_config.angle_limit_time_delay and abs(estimated_tilt_angle) > global_config.angle_limit:
            global_log_manager.log_critical(f"Angle exceeded safe limit: {estimated_tilt_angle:.2f}. Stopping motors.", location="safety")
            motor_left.stop()
            motor_right.stop()
            break

        # === Control loops ===

        # Loop 1: Velocity → Tilt Angle
        if current_time - last_velocity_to_tilt_time >= global_config.velocity_to_tilt_angle_interval:
            if global_config.enable_velocity_loop:
                target_tilt_angle = pid_manager.pid_velocity_to_tilt_angle.update(measured_velocity)
                pid_manager.pid_tilt_angle_to_torque.target_angle = target_tilt_angle
            else:
                pid_manager.pid_tilt_angle_to_torque.target_angle = pid_manager.adjusted_neutral_angle_y
            last_velocity_to_tilt_time = current_time

        # Loop 2: Tilt Angle → Torque (always active)
        if current_time - last_tilt_to_torque_time >= global_config.tilt_angle_to_torque_interval:
            target_torque = pid_manager.pid_tilt_angle_to_torque.update(estimated_tilt_angle)
            pid_manager.pid_estimated_torque_to_torque.target_torque = target_torque
            last_tilt_to_torque_time = current_time

        # Loop 3: Estimated Torque → Applied Torque
        if current_time - last_estimated_torque_time >= global_config.estimated_torque_to_actual_torque_interval:
            estimated_applied_torque = measured_current
            if global_config.enable_torque_feedback_loop:
                actual_torque_output = pid_manager.pid_estimated_torque_to_torque.update(estimated_applied_torque)
            else:
                actual_torque_output = pid_manager.pid_estimated_torque_to_torque.target_torque
            last_estimated_torque_time = current_time

        # Loop 4: Angular Velocity → Torque Differential
        if current_time - last_yaw_control_time >= global_config.angular_velocity_to_torque_diff_interval:
            if global_config.enable_yaw_loop:
                torque_diff = pid_manager.pid_angular_velocity_to_torque_differential.update(z_angular_velocity)
            else:
                torque_diff = 0.0
            last_yaw_control_time = current_time

        # === Motor Commands ===
        motor_left.set_speed(actual_torque_output - torque_diff)
        motor_right.set_speed(actual_torque_output + torque_diff)

        # === Dashboard Update ===
        if gui is not None:
            gui.update_dashboard_value("Velocity", pid_manager.pid_velocity_to_tilt_angle.target_velocity, measured_velocity)
            gui.update_dashboard_value("Tilt Angle", pid_manager.pid_tilt_angle_to_torque.target_angle, estimated_tilt_angle)
            gui.update_dashboard_value("Torque", pid_manager.pid_estimated_torque_to_torque.target_torque, actual_torque_output)
            gui.update_dashboard_value("Z Angular Velocity", pid_manager.pid_angular_velocity_to_torque_differential.target_torque, 0.0 if not global_config.enable_yaw_loop else imu.read_gyro_z())

        # === Logging ===
        if current_time - last_log_time >= LOG_INTERVAL:
            global_log_manager.log_debug(
                f"set={pid_manager.pid_tilt_angle_to_torque.target_angle:.2f}  "
                f"est={estimated_tilt_angle:.2f}  "
                f"tgtT={actual_torque_output:.2f}  "
                f"diff={torque_diff:.3f}",
                location="loop"
            )
            last_log_time = current_time

        time.sleep(global_config.main_loop_interval)

    motor_left.stop()
    motor_right.stop()
    global_log_manager.log_info("Control loop exited", location="main")

# === GUI Thread Setup ===
def start_gui():
    global gui
    root = tk.Tk()
    gui = SteeringGUI(root, pid_manager)
    root.protocol("WM_DELETE_WINDOW", shutdown)
    root.mainloop()

# === Shutdown Handler ===
def shutdown():
    global RUNNING
    RUNNING = False
    global_log_manager.log_warning("Shutdown initiated by GUI or KeyboardInterrupt", location="main")

# === Start Everything ===
if __name__ == "__main__":
    try:
        global_log_manager.log_info("Starting motors", location="main")

        loop_thread = threading.Thread(target=control_loop, daemon=True)
        loop_thread.start()

        start_gui()

    except KeyboardInterrupt:
        shutdown()

    loop_thread.join()
    global_log_manager.log_info("Shutdown complete", location="main")
