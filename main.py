import threading
import time
import tkinter as tk

from src.config.configManager import global_config
from src.pid.pidManager import pidManager
from src.log.logManager import global_log_manager
from src.user_input.steeringGUI import SteeringGUI
from src.hardware.motorEncoder import MotorEncoder
from src.hardware.currentSensor import CurrentSensor

    # === Global GUI reference ===
gui = None

# === Initialization ===
global_log_manager.log_info("Initializing components", location="main")

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
    motor_encoder_left = MotorEncoder(is_left=True)
    motor_encoder_right = MotorEncoder(is_left=False)
    motor_left = MotorController(is_left=True)
    motor_right = MotorController(is_left=False)


pid_manager = pidManager()

# === Control Loop ===
LOG_INTERVAL = 0.25
last_log_time = time.time()
RUNNING = True

# === Loop Timers ===
last_tilt_to_torque_time = 0

def control_loop():
    global last_log_time
    global last_tilt_to_torque_time
    global gui

    start_time = time.time()
    
    motor_left.start()
    motor_right.start()

    while RUNNING:
        current_time = time.time()
        
        # === Sensor readings ===
        estimated_tilt_angle = -imu.read_pitch()

        # === Safety check ===
        if current_time - start_time > global_config.angle_limit_time_delay and abs(estimated_tilt_angle) > global_config.angle_limit:
            global_log_manager.log_critical(f"Angle exceeded safe limit: {estimated_tilt_angle:.2f}. Stopping motors.", location="safety")
            motor_left.stop()
            motor_right.stop()
            break

        # === Control loops ===

        # Loop: Tilt Angle → Torque (always active)
        if current_time - last_tilt_to_torque_time >= global_config.tilt_angle_to_torque_interval:
            target_angle = global_config.angle_neutral
            target_torque = pid_manager.pid_tilt_angle_to_torque.update(estimated_tilt_angle - target_angle)
            last_tilt_to_torque_time = current_time
            
            # === Motor Commands ===
        motor_left.set_speed(target_torque)
        motor_right.set_speed(target_torque)

        # === Dashboard Update ===
        if gui is not None:
            gui.update_dashboard_value("Velocity", pid_manager.pid_velocity_to_tilt_angle.target_velocity, 0.0)
            gui.update_dashboard_value("Tilt Angle", pid_manager.pid_tilt_angle_to_torque.target_angle, estimated_tilt_angle)
            gui.update_dashboard_value("Torque", pid_manager.pid_estimated_torque_to_torque.target_torque, 0.0)
            gui.update_dashboard_value("Z Angular Velocity", pid_manager.pid_angular_velocity_to_torque_differential.target_torque, 0.0 if not global_config.enable_yaw_loop else imu.read_gyro_z())

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
