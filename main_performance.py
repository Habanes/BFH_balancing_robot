#!/usr/bin/env python3
"""
PERFORMANCE-OPTIMIZED MAIN.PY
Based on actual timing measurements showing IMU reads take 0.67ms average

MEASURED PERFORMANCE:
- IMU read: 0.67ms average (was 67% of total loop time!)
- Encoder reads: 0.001ms (negligible)
- Motor commands: 0.065ms (small)

SOLUTION:
- Main loop: 100Hz (10ms budget) - gives 15x safety margin
- Encoder reads: 50Hz (every 2nd iteration)
- Still very responsive for balancing control
"""

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
global_log_manager.log_info("Initializing components (PERFORMANCE OPTIMIZED)", location="main")

imu = IMU()
motor_left = MotorController(is_left=True)
motor_right = MotorController(is_left=False)

# Initialize encoders for position tracking
encoder_left = MotorEncoder(is_left=True)
encoder_right = MotorEncoder(is_left=False)

# Reset travel distance counters
encoder_left.reset_travel_distance()
encoder_right.reset_travel_distance()

pid_manager = pidManager()

wait_until_correct_angle = True

# === Performance-Optimized Control Loop ===
LOG_INTERVAL = 1.0  # Reduced logging frequency
RUNNING = True

# === Encoder timing (every 2nd iteration at 100Hz = 50Hz encoder reads) ===
encoder_read_counter = 0

def control_loop():
    global encoder_read_counter
    global latest_angle, latest_torque
    global latest_left_position, latest_right_position, latest_left_travel, latest_right_travel
    global wait_until_correct_angle

    start_time = time.time()
    target_torque = 0.0
    last_log_time = time.time()

    motor_left.start()
    motor_right.start()

    global_log_manager.log_info(f"Starting PERFORMANCE-OPTIMIZED control loop", location="main")
    global_log_manager.log_info(f"Main loop: {global_config.main_loop_rate}Hz, Encoder reads: {global_config.main_loop_rate/2}Hz", location="main")

    iteration_count = 0

    while RUNNING:
        iteration_start = time.perf_counter()
        current_time = time.time()
        iteration_count += 1
        
        # === Sensor readings (every iteration for balance control) ===
        estimated_tilt_angle = imu.read_pitch()
        
        # === Encoder readings (every 2nd iteration = 50Hz) ===
        encoder_read_counter += 1
        if encoder_read_counter >= 2:
            encoder_read_counter = 0
            
            left_position = encoder_left.get_steps()
            right_position = encoder_right.get_steps()
            left_travel = encoder_left.update_travel_distance()
            right_travel = encoder_right.update_travel_distance()
            
            # Update shared values for GUI
            latest_left_position = left_position
            latest_right_position = right_position
            latest_left_travel = left_travel
            latest_right_travel = right_travel

        # === Safety check ===
        abs_angle = abs(estimated_tilt_angle)

        if abs_angle > global_config.angle_limit:
            global_log_manager.log_critical(
                f"Angle exceeded hard limit: {estimated_tilt_angle:.2f}. Stopping motors.",
                location="safety"
            )
            motor_left.stop()
            motor_right.stop()
            wait_until_correct_angle = True

        elif abs_angle > global_config.tilt_angle_soft_limit:
            if pid_manager.pid_tilt_angle_to_torque.target_angle != global_config.angle_neutral:
                global_log_manager.log_warning(
                    f"Angle exceeded soft limit: {estimated_tilt_angle:.2f}. PID target set to 0.",
                    location="safety"
                )
            pid_manager.pid_tilt_angle_to_torque.target_angle = global_config.angle_neutral

        else:
            if wait_until_correct_angle:
                motor_left.start()
                motor_right.start()
                wait_until_correct_angle = False
            
            if pid_manager.pid_tilt_angle_to_torque.target_angle == global_config.angle_neutral:
                pid_manager.update_pid_target()

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

        # === Performance monitoring ===
        iteration_end = time.perf_counter()
        iteration_time_ms = (iteration_end - iteration_start) * 1000

        # === Reduced frequency logging ===
        if current_time - last_log_time >= LOG_INTERVAL:
            global_log_manager.log_info(
                f"PERF: iter={iteration_count} time={iteration_time_ms:.2f}ms "
                f"angle={estimated_tilt_angle:.2f} torque={target_torque:.2f} "
                f"encL={latest_left_position:.0f} encR={latest_right_position:.0f}",
                location="performance"
            )
            last_log_time = current_time
            
            if iteration_time_ms > 5.0:  # Warn if taking more than 5ms
                global_log_manager.log_warning(
                    f"Slow iteration: {iteration_time_ms:.2f}ms (target: {global_config.main_loop_interval*1000:.1f}ms)",
                    location="performance"
                )

        # === Loop timing ===
        time.sleep(global_config.main_loop_interval)

    motor_left.stop()
    motor_right.stop()
    global_log_manager.log_info("Performance-optimized control loop exited", location="main")
    
def clip(value, min_val, max_val):
    return max(min(value, max_val), min_val)

# === Shutdown Handler ===
def shutdown():
    global RUNNING
    RUNNING = False
    global_log_manager.log_warning("Shutdown initiated by KeyboardInterrupt", location="main")

if __name__ == "__main__":
    try:
        global_log_manager.log_info("Starting PERFORMANCE-OPTIMIZED balancing robot", location="main")
        global_log_manager.log_info(f"Based on timing analysis: IMU=0.67ms, Target loop=10ms", location="main")

        loop_thread = threading.Thread(target=control_loop, daemon=True)
        loop_thread.start()

        from src.user_input.RobotGui import RobotGui
        root = tk.Tk()
        gui = RobotGui(root, pid_manager, get_latest_state)
        root.mainloop()

    except KeyboardInterrupt:
        shutdown()

    finally:
        global_log_manager.log_info("Final cleanup: stopping motors", location="main")
        RUNNING = False
        motor_left.stop()
        motor_right.stop()
        loop_thread.join()
        global_log_manager.log_info("Shutdown complete", location="main")
