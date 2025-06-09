import threading
import time
import tkinter as tk

from src.config.configManager import global_config
from src.pid.pidManager import pidManager
from src.log.logManager import global_log_manager
from src.hardware.imu import IMU
from src.hardware.motorController import MotorController

# === Shared Variables for GUI ===
latest_angle = 0.0
latest_torque = 0.0

def get_latest_state():
    return latest_angle, latest_torque

# === Initialization ===
global_log_manager.log_info("Initializing components", location="main")

imu = IMU()
motor_left = MotorController(is_left=True)
motor_right = MotorController(is_left=False)

pid_manager = pidManager()

wait_until_correct_angle = True

# === Control Loop ===
LOG_INTERVAL = 0.25
last_log_time = time.time()
RUNNING = True

def control_loop():
    global last_log_time, latest_angle, latest_torque, wait_until_correct_angle

    target_torque = 0.0  # ensure it's initialized

    motor_left.start()
    motor_right.start()

    while RUNNING:
        current_time = time.time()

        # === Sensor readings ===
        estimated_tilt_angle = imu.read_pitch() + global_config.imu_angle_offset

        # === Safety check ===:
        abs_angle = abs(estimated_tilt_angle)

        if abs_angle > global_config.angle_limit:
            # HARD LIMIT: stop everything
            global_log_manager.log_critical(
                f"Angle exceeded hard limit: {estimated_tilt_angle:.2f}. Stopping motors.",
                location="safety"
            )
            motor_left.stop()
            motor_right.stop()
            wait_until_correct_angle = True

        elif abs_angle > global_config.tilt_angle_soft_limit:
            # SOFT LIMIT: still running, but set target angle to 0
            if pid_manager.pid_tilt_angle_to_torque.target_angle != global_config.angle_neutral:
                global_log_manager.log_warning(
                    f"Angle exceeded soft limit: {estimated_tilt_angle:.2f}. PID target set to 0.",
                    location="safety"
                )
            pid_manager.pid_tilt_angle_to_torque.target_angle = global_config.angle_neutral

        else:            # Within safe range
            if wait_until_correct_angle:
                motor_left.start()
                motor_right.start()
                wait_until_correct_angle = False

            # Reset PID target angle to normal if it was set to neutral during soft limit
            if pid_manager.pid_tilt_angle_to_torque.target_angle == global_config.angle_neutral:
                pid_manager.update_pid_target()        
        
        # === Control loops ===
        target_torque = pid_manager.pid_tilt_angle_to_torque.update(estimated_tilt_angle)
        
        target_torque_left = clip(target_torque - pid_manager.torque_differential, -1.0, 1.0)
        target_torque_right = clip(target_torque + pid_manager.torque_differential, -1.0, 1.0)

        # === Motor Commands ===
        motor_left.set_speed(target_torque_left)
        motor_right.set_speed(target_torque_right)

        # === Update shared values for GUI ===
        latest_angle = estimated_tilt_angle
        latest_torque = target_torque        
        
        # === Logging ===
        if current_time - last_log_time >= LOG_INTERVAL:
            global_log_manager.log_debug(
                f"set={pid_manager.pid_tilt_angle_to_torque.target_angle:.2f}  "
                f"est={estimated_tilt_angle:.2f}  "
                f"tgtT={target_torque:.2f}  ",
                location="loop"
            )
            last_log_time = current_time

        time.sleep(global_config.main_loop_interval)

    motor_left.stop()
    motor_right.stop()
    global_log_manager.log_info("Control loop exited", location="main")
    
def clip(value, min_val, max_val):
    return max(min(value, max_val), min_val)

# === Shutdown Handler ===
def shutdown():
    global RUNNING
    RUNNING = False
    global_log_manager.log_warning("Shutdown initiated by KeyboardInterrupt", location="main")

if __name__ == "__main__":
    try:
        global_log_manager.log_info("Starting motors", location="main")

        loop_thread = threading.Thread(target=control_loop, daemon=True)
        loop_thread.start()

        from src.user_input.RobotGui import RobotGui
        root = tk.Tk()
        RobotGui(root, pid_manager, get_latest_state)
        root.mainloop()

    except KeyboardInterrupt:
        shutdown()

    finally:
        # Always stop motors and join thread safely
        global_log_manager.log_info("Final cleanup: stopping motors", location="main")
        RUNNING = False
        motor_left.stop()
        motor_right.stop()
        loop_thread.join()
        global_log_manager.log_info("Shutdown complete", location="main")
