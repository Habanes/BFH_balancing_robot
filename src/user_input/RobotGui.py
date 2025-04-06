import tkinter as tk

class RobotGui:
    def __init__(self, root, pid_manager, get_state_callback):
        self.root = root
        self.root.title("PID Controller GUI")

        self.pid_manager = pid_manager
        self.get_state = get_state_callback

        self.entries = {}
        self.angle_var = tk.StringVar()
        self.error_var = tk.StringVar()
        self.torque_var = tk.StringVar()

        self.build_pid_controls()
        self.build_status_labels()
        self.build_control_buttons()
        self.bind_keys()
        self.refresh_values()

    def build_pid_controls(self):
        for i, param in enumerate(["kp", "ki", "kd"]):
            tk.Label(self.root, text=param.upper()).grid(row=i, column=0)

            entry = tk.Entry(self.root)
            entry.insert(0, str(getattr(self.pid_manager.pid_tilt_angle_to_torque, param)))
            entry.grid(row=i, column=1)
            self.entries[param] = entry

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

    def build_control_buttons(self):
        button_config = [
            ("Stop (SPACE)", self.pid_manager.stop),
            ("Go Forward (W)", self.pid_manager.goForward),
            ("Go Backward (S)", self.pid_manager.goBackward),
        ]

        for i, (label, command) in enumerate(button_config, start=7):
            tk.Button(self.root, text=label, command=command).grid(row=i, column=0, columnspan=3, sticky="we", pady=2)

    def bind_keys(self):
        self.root.bind("<w>", lambda event: self.pid_manager.goForward())
        self.root.bind("<s>", lambda event: self.pid_manager.goBackward())
        self.root.bind("<space>", lambda event: self.pid_manager.stop())

    def update_pid_value(self, param):
        try:
            val = float(self.entries[param].get())
            setattr(self.pid_manager.pid_tilt_angle_to_torque, param, val)
        except ValueError:
            print(f"Invalid input for {param}")

    def refresh_values(self):
        current_angle, torque = self.get_state()
        target_angle = self.pid_manager.pid_tilt_angle_to_torque.target_angle
        error = target_angle - current_angle

        self.angle_var.set(f"{current_angle:.2f}")
        self.error_var.set(f"{error:.2f}")
        self.torque_var.set(f"{torque:.2f}")

        self.root.after(100, self.refresh_values)
