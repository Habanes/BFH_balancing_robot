import tkinter as tk
import main  # for shared values: main.latest_angle, main.latest_torque

class RobotGui:
    def __init__(self, root, pid_manager):
        self.root = root
        self.root.title("PID Controller GUI")
        
        # Store the actual pid_manager instance passed in from main.py
        self.pid_manager = pid_manager

        self.entries = {}
        self.angle_var = tk.StringVar()
        self.error_var = tk.StringVar()
        self.torque_var = tk.StringVar()

        self.build_pid_controls()
        self.build_status_labels()

        self.refresh_values()

    def build_pid_controls(self):
        # We want to update "kp", "ki", "kd" in self.pid_manager.pid_tilt_angle_to_torque
        for i, param in enumerate(["kp", "ki", "kd"]):
            tk.Label(self.root, text=param.upper()).grid(row=i, column=0)

            entry = tk.Entry(self.root)
            # Insert current value from the actual pid_manager instance
            entry.insert(0, str(getattr(self.pid_manager.pid_tilt_angle_to_torque, param)))
            entry.grid(row=i, column=1)
            self.entries[param] = entry

            # Button updates that single parameter
            btn = tk.Button(self.root, text="Update", command=lambda p=param: self.update_pid_value(p))
            btn.grid(row=i, column=2)

    def build_status_labels(self):
        labels = [
            ("Current Angle", self.angle_var),
            ("Angle Error",  self.error_var),
            ("Torque",       self.torque_var),
        ]

        for j, (label, var) in enumerate(labels, start=4):
            tk.Label(self.root, text=label).grid(row=j, column=0)
            tk.Label(self.root, textvariable=var).grid(row=j, column=1)

    def update_pid_value(self, param):
        try:
            val = float(self.entries[param].get())
            # Update the parameter in the actual pid_manager instance
            setattr(self.pid_manager.pid_tilt_angle_to_torque, param, val)
        except ValueError:
            print(f"Invalid input for {param}")

    def refresh_values(self):
        # Pull the latest sensor/torque values from the main module
        current_angle = main.latest_angle
        torque = main.latest_torque

        # Also read the target angle from the actual PID instance
        target_angle = self.pid_manager.pid_tilt_angle_to_torque.target_angle
        error = target_angle - current_angle

        self.angle_var.set(f"{current_angle:.2f}")
        self.error_var.set(f"{error:.2f}")
        self.torque_var.set(f"{torque:.2f}")

        # Schedule the next update
        self.root.after(100, self.refresh_values)
