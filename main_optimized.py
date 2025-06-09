#!/usr/bin/env python3
"""
OPTIMIZED MAIN.PY FOR ENCODER INTEGRATION
Test version with different timing optimization strategies

CHANGES FROM ORIGINAL:
1. Reduced main loop from 10kHz to 5kHz for better stability
2. Encoder reads at 1kHz (every 5th iteration) to reduce timing pressure
3. Added timing monitoring to detect performance issues
4. Smart encoder update strategy to maintain position tracking accuracy

Run this version to test improved stability with encoder integration.
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
global_log_manager.log_info("Initializing components (OPTIMIZED VERSION)", location="main")

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

# === Optimized Control Loop ===
LOG_INTERVAL = 0.25
TIMING_LOG_INTERVAL = 5.0  # Log timing stats every 5 seconds
last_log_time = time.time()
last_timing_log_time = time.time()
RUNNING = True

# === Encoder timing optimization ===
ENCODER_READ_DECIMATION = 5  # Read encoders every 5th iteration (1kHz instead of 5kHz)
encoder_read_counter = 0

# === Timing monitoring ===
loop_times = []
max_timing_samples = 1000

def control_loop():
    global last_log_time, last_timing_log_time, encoder_read_counter
    global latest_angle, latest_torque
    global latest_left_position, latest_right_position, latest_left_travel, latest_right_travel
    global wait_until_correct_angle, loop_times

    start_time = time.time()
    target_torque = 0.0

    motor_left.start()
    motor_right.start()

    global_log_manager.log_info(f"Starting optimized control loop at {global_config.main_loop_rate}Hz", location="main")
    global_log_manager.log_info(f"Encoder read rate: {global_config.main_loop_rate/ENCODER_READ_DECIMATION}Hz", location="main")

    while RUNNING:
        loop_start_time = time.perf_counter()
        current_time = time.time()        
        
        # === Sensor readings (every iteration) ===
        raw_imu_reading = imu.read_pitch_raw()
        estimated_tilt_angle = imu.read_pitch()
        
        # === Encoder readings (decimated for timing optimization) ===
        encoder_read_counter += 1
        if encoder_read_counter >= ENCODER_READ_DECIMATION:
            encoder_read_counter = 0
            
            # Read all encoder values at reduced frequency
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

        # === Timing monitoring ===
        loop_end_time = time.perf_counter()
        loop_duration = (loop_end_time - loop_start_time) * 1000  # Convert to ms
        
        if len(loop_times) < max_timing_samples:
            loop_times.append(loop_duration)
        else:
            loop_times[len(loop_times) % max_timing_samples] = loop_duration

        # === Logging ===
        if current_time - last_log_time >= LOG_INTERVAL:
            global_log_manager.log_debug(
                f"raw_imu={raw_imu_reading:.2f} "
                f"corrected={estimated_tilt_angle:.2f} "
                f"set={pid_manager.pid_tilt_angle_to_torque.target_angle:.2f} "
                f"tgtT={target_torque:.2f} "
                f"encL={latest_left_position:.0f} "
                f"encR={latest_right_position:.0f} "
                f"travL={latest_left_travel:.0f} "
                f"travR={latest_right_travel:.0f}",
                location="debug"
            )
            last_log_time = current_time

        # === Timing performance logging ===
        if current_time - last_timing_log_time >= TIMING_LOG_INTERVAL and len(loop_times) > 100:
            avg_time = sum(loop_times) / len(loop_times)
            max_time = max(loop_times)
            target_time = global_config.main_loop_interval * 1000  # Convert to ms
            
            global_log_manager.log_info(
                f"TIMING: Avg={avg_time:.3f}ms Max={max_time:.3f}ms Target={target_time:.3f}ms "
                f"OverBudget={max_time/target_time:.1f}x EncoderRate={global_config.main_loop_rate/ENCODER_READ_DECIMATION}Hz",
                location="performance"
            )
            
            if max_time > target_time * 1.5:
                global_log_manager.log_warning(
                    f"Loop timing over budget! Consider reducing frequency or encoder read rate.",
                    location="performance"
                )
            
            last_timing_log_time = current_time
            # Reset timing buffer periodically
            loop_times = loop_times[-100:]  # Keep last 100 samples

        # === Loop timing ===
        time.sleep(global_config.main_loop_interval)

    motor_left.stop()
    motor_right.stop()
    global_log_manager.log_info("Optimized control loop exited", location="main")
    
def clip(value, min_val, max_val):
    return max(min(value, max_val), min_val)

# === Shutdown Handler ===
def shutdown():
    global RUNNING
    RUNNING = False
    global_log_manager.log_warning("Shutdown initiated by KeyboardInterrupt", location="main")

if __name__ == "__main__":
    try:
        global_log_manager.log_info("Starting OPTIMIZED balancing robot", location="main")
        global_log_manager.log_info(f"Main loop: {global_config.main_loop_rate}Hz, Encoder decimation: 1/{ENCODER_READ_DECIMATION}", location="main")

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
