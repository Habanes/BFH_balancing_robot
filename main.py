import threading
import time
import tkinter as tk

from src.config.configManager import global_config
from src.pid.pidManager import pidManager
from src.log.logManager import global_log_manager
from src.hardware.imu import IMU
from src.hardware.motorController import MotorController
from src.hardware.motorEncoder import MotorEncoder

# === Shared Variables for GUI ===
latest_angle = 0.0
latest_torque = 0.0
latest_left_position = 0.0
latest_right_position = 0.0
latest_left_travel = 0.0
latest_right_travel = 0.0

def get_latest_state():
    return (latest_angle, latest_torque, latest_left_position, latest_right_position, 
            latest_left_travel, latest_right_travel)

# === Initialization ===
global_log_manager.log_info("Initializing components", location="main")

# Use simulator if test mode is on

imu = IMU()
motor_left = MotorController(is_left=True)
motor_right = MotorController(is_left=False)

# === TEMPORARILY DISABLED FOR TIMING TEST ===
# Initialize encoders for position tracking
# encoder_left = MotorEncoder(is_left=True)
# encoder_right = MotorEncoder(is_left=False)

# Reset travel distance counters
# encoder_left.reset_travel_distance()
# encoder_right.reset_travel_distance()

pid_manager = pidManager()

wait_until_correct_angle = True

# === Control Loop ===
LOG_INTERVAL = 0.25
last_log_time = time.time()
RUNNING = True
last_tilt_to_torque_time = 0

# === Timing optimization for encoder reads ===
# With 40Hz main loop, read encoders at 20Hz (every 2nd iteration)
# This minimizes I2C traffic while maintaining adequate position tracking
ENCODER_READ_RATE = 20  # Hz - Final conservative approach
encoder_read_interval = 1.0 / ENCODER_READ_RATE
last_encoder_read_time = 0

def control_loop():
    global last_log_time, last_tilt_to_torque_time, last_encoder_read_time
    global latest_angle, latest_torque
    global latest_left_position, latest_right_position, latest_left_travel, latest_right_travel
    global wait_until_correct_angle

    start_time = time.time()
    target_torque = 0.0  # ensure it's initialized

    motor_left.start()
    motor_right.start()

    while RUNNING:
        current_time = time.time()        
        
        # === Sensor readings ===
        raw_imu_reading = imu.read_pitch_raw()  # For debugging
        estimated_tilt_angle = imu.read_pitch()        # === Encoder readings (TEMPORARILY DISABLED) ===
        # Only read encoders at 20Hz instead of 40Hz to improve timing
        # This is sufficient for position tracking while maintaining stability
        if current_time - last_encoder_read_time >= encoder_read_interval:
            # left_position = encoder_left.get_steps()
            # right_position = encoder_right.get_steps()
            # left_travel = encoder_left.update_travel_distance()
            # right_travel = encoder_right.update_travel_distance()
            
            # Update shared values for GUI (set to dummy values)
            latest_left_position = 0
            latest_right_position = 0
            latest_left_travel = 0
            latest_right_travel = 0
            
            last_encoder_read_time = current_time

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

        else:
            # Within safe range
            if wait_until_correct_angle:
                motor_left.start()
                motor_right.start()
                wait_until_correct_angle = False
            
            # Reset PID target angle to normal if it was set to neutral before
            if pid_manager.pid_tilt_angle_to_torque.target_angle == global_config.angle_neutral:
                pid_manager.update_pid_target()  # Restore proper target angle


        # === Control loops ===
        target_torque = pid_manager.pid_tilt_angle_to_torque.update(estimated_tilt_angle)
        target_torque_left  = clip(target_torque - pid_manager.torque_differential, -1.0, 1.0)
        target_torque_right = clip(target_torque + pid_manager.torque_differential, -1.0, 1.0)
        
        # === Motor Commands ===
        motor_left.set_speed(target_torque_left)
        motor_right.set_speed(target_torque_right)

        # === Update shared values for GUI ===
        latest_angle = estimated_tilt_angle
        latest_torque = target_torque
        # Encoder values updated above at 1kHz rate

        # === Logging ===
        if current_time - last_log_time >= LOG_INTERVAL:
            global_log_manager.log_debug(
                f"raw_imu={raw_imu_reading:.2f}  "
                f"corrected={estimated_tilt_angle:.2f}  "
                f"offset={global_config.imu_mounting_offset:.2f}  "
                f"set={pid_manager.pid_tilt_angle_to_torque.target_angle:.2f}  "
                f"tgtT={target_torque:.2f}  "
                f"encL={latest_left_position:.0f}  "
                f"encR={latest_right_position:.0f}  "
                f"travL={latest_left_travel:.0f}  "
                f"travR={latest_right_travel:.0f}  ",
                location="debug"            )
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
        gui = RobotGui(root, pid_manager, get_latest_state)
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
