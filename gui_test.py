import tkinter as tk
from src.pid.pidManager import pidManager
from src.user_input.steeringGUI import SteeringGUI  # Adjust path if needed
import random  # for demo purposes; replace with real data in actual control loop

def update_dashboard(gui: SteeringGUI, controller: pidManager):
    # For testing, you can replace the below with real sensor readings or internal state
    # These are dummy measured values to simulate dynamic updates:
    velocity_measured = random.uniform(0, 10)
    velocity_target = controller.pid_velocity_to_tilt_angle.target_tilt_angle

    tilt_measured = random.uniform(-10, 10)
    tilt_target = controller.pid_tilt_angle_to_torque.target_angle

    yaw_rate_measured = random.uniform(-1, 1)
    yaw_target = controller.pid_angular_velocity_to_torque_differential.target_torque

    current = random.uniform(0, 2)
    torque_target = controller.pid_estimated_torque_to_torque.target_torque

    # Update GUI
    gui.update_dashboard_value("Velocity", velocity_target, velocity_measured)
    gui.update_dashboard_value("Tilt Angle", tilt_target, tilt_measured)
    gui.update_dashboard_value("Z Angular Velocity", yaw_target, yaw_rate_measured)
    gui.update_dashboard_value("Torque", torque_target, current)

    # Call again after delay
    gui.master.after(500, update_dashboard, gui, controller)

if __name__ == "__main__":
    root = tk.Tk()
    controller = pidManager()
    gui = SteeringGUI(root, controller)

    # Start dashboard updater
    update_dashboard(gui, controller)

    root.mainloop()
