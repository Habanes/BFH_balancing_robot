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
latest_velocity = 0.0
latest_target_velocity = 0.0

# === Initialization ===
global_log_manager.log_info("Initializing components", location="main")

imu = IMU()
motor_left = MotorController(is_left=True)
motor_right = MotorController(is_left=False)
motor_encoder_left = MotorEncoder(is_left=True)
motor_encoder_right = MotorEncoder(is_left=False)
pid_manager = pidManager()
wait_until_correct_angle = True

# === Control Loop ===
last_log_time = time.time()
RUNNING = True
last_tilt_to_torque_time = 0

def entire_control_loop():
    global last_log_time, last_tilt_to_torque_time
    global latest_angle, latest_torque, latest_velocity, latest_target_velocity
    global wait_until_correct_angle

    start_time = time.time()
    target_torque = 0.0

    velocity_loop_counter = 0
    VELOCITY_LOOP_DIVIDER = 50

    motor_left.start()
    motor_right.start()

    while RUNNING:
        loop_start = time.time()
        current_time = time.time()

        # === Sensor readings ===
        t0 = time.time()
        estimated_tilt_angle = -imu.read_pitch()
        t1 = time.time()

        # === Safety check ===
        if abs(estimated_tilt_angle) > global_config.angle_limit:
            global_log_manager.log_critical(
                f"Angle exceeded safe limit: {estimated_tilt_angle:.2f}. Stopping motors.", location="safety"
            )
            motor_left.stop()
            motor_right.stop()
            wait_until_correct_angle = True

        if  abs(estimated_tilt_angle) < global_config.angle_limit and wait_until_correct_angle:
            motor_left.start()
            motor_right.start()
            wait_until_correct_angle = False
        t2 = time.time()

        # === Outer velocity loop (runs slower) ===
        velocity_loop_counter = (velocity_loop_counter + 1) % VELOCITY_LOOP_DIVIDER
        if velocity_loop_counter == 0:
            motor_encoder_left.update()
            motor_encoder_right.update()

            avg_velocity = (motor_encoder_left.get_velocity() + motor_encoder_right.get_velocity()) / 2.0
            target_tilt_angle = pid_manager.pid_velocity_to_tilt_angle.update(avg_velocity)

            if not global_config.only_inner_loop:
                pid_manager.pid_tilt_angle_to_torque.target_angle = target_tilt_angle

            latest_velocity = avg_velocity
            latest_target_velocity = pid_manager.pid_velocity_to_tilt_angle.target_velocity
        t3 = time.time()

        # === Inner tilt-angle-to-torque loop ===
        target_torque = pid_manager.pid_tilt_angle_to_torque.update(estimated_tilt_angle)
        t4 = time.time()

        # === Motor Commands ===
        motor_left.set_speed(target_torque)
        motor_right.set_speed(target_torque)
        t5 = time.time()

        # === Update shared values for GUI ===
        latest_angle = estimated_tilt_angle
        latest_torque = target_torque
        t6 = time.time()

        # === Log timings ===
        if global_config.log_timings:
            total = t6 - loop_start
            steps = {
                "Read pitch": t1 - t0,
                "Safety checks": t2 - t1,
                "Velocity loop": t3 - t2,
                "Torque PID": t4 - t3,
                "Motor speed set": t5 - t4,
                "GUI update": t6 - t5,
            }

            print(f"\nLoop total time: {total:.6f}s")
            for name, duration in steps.items():
                pct = (duration / total) * 100 if total > 0 else 0
                print(f"{name:20s}: {duration:.6f}s ({pct:5.1f}%)")

    motor_left.stop()
    motor_right.stop()
    global_log_manager.log_info("Control loop exited", location="main")

# === Shutdown Handler ===
def shutdown():
    global RUNNING
    RUNNING = False
    global_log_manager.log_warning("Shutdown initiated by KeyboardInterrupt", location="main")
    
def get_latest_state():
    return latest_angle, latest_torque, latest_velocity, latest_target_velocity

if __name__ == "__main__":
    try:
        global_log_manager.log_info("Starting motors", location="main")

        loop_thread = threading.Thread(target=entire_control_loop, daemon=True)
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
