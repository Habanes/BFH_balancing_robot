import tkinter as tk
from src.pid.pidManager import pid_manager
import main  # for shared values

class RobotGui:
    def __init__(self, root):
        self.root = root
        self.root.title("PID Controller GUI")

        self.entries = {}
        self.angle_var = tk.StringVar()
        self.error_var = tk.StringVar()
        self.torque_var = tk.StringVar()

        self.build_pid_controls()
        self.build_status_labels()

        self.refresh_values()

    def build_pid_controls(self):
        for i, param in enumerate(["kp", "ki", "kd"]):
            tk.Label(self.root, text=param.upper()).grid(row=i, column=0)
            entry = tk.Entry(self.root)
            entry.insert(0, str(getattr(pid_manager.pid_tilt_angle_to_torque, param)))
            entry.grid(row=i, column=1)
            self.entries[param] = entry
            btn = tk.Button(self.root, text="Update", command=lambda p=param: self.update_pid_value(p))
            btn.grid(row=i, column=2)

    def build_status_labels(self):
        labels = [("Current Angle", self.angle_var),
                  ("Angle Error", self.error_var),
                  ("Torque", self.torque_var)]

        for j, (label, var) in enumerate(labels, start=4):
            tk.Label(self.root, text=label).grid(row=j, column=0)
            tk.Label(self.root, textvariable=var).grid(row=j, column=1)

    def update_pid_value(self, param):
        try:
            val = float(self.entries[param].get())
            setattr(pid_manager.pid_tilt_angle_to_torque, param, val)
        except ValueError:
            print(f"Invalid input for {param}")

    def refresh_values(self):
        current_angle = main.latest_angle
        target_angle = pid_manager.pid_tilt_angle_to_torque.target_angle
        torque = main.latest_torque
        error = target_angle - current_angle

        self.angle_var.set(f"{current_angle:.2f}")
        self.error_var.set(f"{error:.2f}")
        self.torque_var.set(f"{torque:.2f}")

        self.root.after(100, self.refresh_values)
