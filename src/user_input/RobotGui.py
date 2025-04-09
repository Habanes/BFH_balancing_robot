import tkinter as tk

class RobotGui:
    def __init__(self, root, pid_manager, get_state_callback):
        self.root = root
        self.root.title("PID Controller GUI")

        self.pid_manager = pid_manager
        self.get_state = get_state_callback

        self.entries = {}
        self.angle_var = tk.StringVar()
        self.tgtangle_var = tk.StringVar()
        self.error_var = tk.StringVar()
        self.torque_var = tk.StringVar()
        self.offset_entry = None

        self.build_pid_controls()
        self.build_status_labels()
        self.build_control_buttons()
        self.build_offset_input()
        self.build_joystick()
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
            ("Target Angle", self.tgtangle_var),
            ("Angle Error",  self.error_var),
            ("Torque",       self.torque_var),
        ]

        for j, (label, var) in enumerate(labels, start=4):
            tk.Label(self.root, text=label).grid(row=j, column=0)
            tk.Label(self.root, textvariable=var).grid(row=j, column=1)

    def build_control_buttons(self):
        tk.Button(self.root, text="Stop (SPACE)", command=self.pid_manager.stop)\
            .grid(row=8, column=0, columnspan=3, sticky="we", pady=2)

    def build_offset_input(self):
        tk.Label(self.root, text="Dynamic Offset").grid(row=7, column=0)
        self.offset_entry = tk.Entry(self.root)
        self.offset_entry.grid(row=7, column=1)

        tk.Button(self.root, text="Set Dynamic Offset", command=self.set_dynamic_offset).grid(row=7, column=2)

    def build_joystick(self):
        tk.Label(self.root, text="Joystick (Y-axis)").grid(row=11, column=0)
        self.joystick = tk.Scale(
            self.root,
            from_=15,
            to=-15,
            orient=tk.VERTICAL,
            resolution=0.1,
            command=self.update_control_angle
        )
        self.joystick.set(0)
        self.joystick.grid(row=12, column=0, rowspan=3)

    def update_control_angle(self, value):
        try:
            val = float(value)
            self.pid_manager.setTargetAngle(val)
        except ValueError:
            print("Invalid joystick input.")

    def set_dynamic_offset(self):
        try:
            offset_value = float(self.offset_entry.get())
            self.pid_manager.set_dynamic_target_angle_offset(offset_value)
        except ValueError:
            print("Invalid input for dynamic offset.")

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
        self.tgtangle_var.set(f"{target_angle:.2f}")
        self.error_var.set(f"{error:.2f}")
        self.torque_var.set(f"{torque:.2f}")

        self.root.after(100, self.refresh_values)
