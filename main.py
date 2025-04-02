import threading
import time
import tkinter as tk

from src.interfacing.imu import IMU
from src.interfacing.motorController import MotorController
from src.interfacing.currentSensor import CurrentSensor
from src.control.imu import AngleEstimator
from src.control.angleController import AngleController
from src.interfacing.steeringController import steeringController
from src.config.configManager import global_config
from src.log.logManager import global_log_manager
from src.interfacing.steeringGUI import steeringGUI  # adjust path if needed

# === Initialization ===
global_log_manager.log_info("Initializing components", location="main")

imu = IMU()
motor_left = MotorController(is_left=True)
motor_right = MotorController(is_left=False)
steeringControl = steeringController()

angle_pid = AngleController(
    steeringControl.getKpY(),
    steeringControl.getKiY(),
    steeringControl.getKdY(),
    steeringControl.getAngleY()
)

# === Control Loop ===
LOG_INTERVAL = 0.25
last_log_time = time.time()
RUNNING = True  # Flag for stopping the control loop safely

def control_loop():
    global last_log_time
    while RUNNING:
        estimatedAngle = imu.read_pitch()

        if abs(estimatedAngle) > global_config.angleLimit:
            global_log_manager.log_critical(f"Angle exceeded safe limit: {estimatedAngle:.2f}. Stopping motors.", location="safety")
            motor_left.stop()
            motor_right.stop()
            break

        # Update PID target from steeringController
        angle_pid.setTargetAngle(steeringControl.getAngleY())

        # Update PID parameters from steeringController
        angle_pid.setKp(steeringControl.getKpY())
        angle_pid.setKi(steeringControl.getKiY())
        angle_pid.setKd(steeringControl.getKdY())

        target_torque = angle_pid.update(estimatedAngle)
        motor_left.set_speed(target_torque)
        motor_right.set_speed(target_torque)

        if time.time() - last_log_time >= LOG_INTERVAL:
            set_angle = angle_pid.pid.setpoint
            est_angle = estimatedAngle
            angle_error = set_angle - est_angle

            global_log_manager.log_debug(
                f"set={set_angle:.2f}  est={est_angle:.2f} err={angle_error:.2f} "
                f"tgtT={target_torque:.2f}",
                location="loop"
            )
            last_log_time = time.time()

        time.sleep(global_config.loopInterval)

    motor_left.stop()
    motor_right.stop()
    global_log_manager.log_info("Control loop exited", location="main")

# === GUI Thread Setup ===
def start_gui():
    root = tk.Tk()
    gui = steeringGUI(root, steeringControl)
    
    # Add update methods to link GUI to live controller
    def sync_kp(): steeringControl.setKpY(gui.kp.get())
    def sync_ki(): steeringControl.setKiY(gui.ki.get())
    def sync_kd(): steeringControl.setKdY(gui.kd.get())
    
    gui.update_kp = sync_kp
    gui.update_ki = sync_ki
    gui.update_kd = sync_kd

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
        motor_left.start()
        motor_right.start()

        loop_thread = threading.Thread(target=control_loop, daemon=True)
        loop_thread.start()

        start_gui()  # Runs in main thread

    except KeyboardInterrupt:
        shutdown()

    loop_thread.join()
    global_log_manager.log_info("Shutdown complete", location="main")
