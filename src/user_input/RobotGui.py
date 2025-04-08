import tkinter as tk
from src.config.configManager import global_config
from src.pid.pidManager import pidManager

class RobotGui:
    def __init__(self, root, pid_manager: pidManager, get_state_callback):
        self.root = root
        self.root.title("PID Controller GUI")

        self.pid_manager = pid_manager
        self.get_state = get_state_callback

        self.entries = {}
        self.angle_var = tk.StringVar()
        self.tgtangle_var = tk.StringVar()
        self.error_var = tk.StringVar()
        self.torque_var = tk.StringVar()
        self.vel_var = tk.StringVar()
        self.tgtvel_var = tk.StringVar()
        self.velerror_var = tk.StringVar()
        self.offset_entry = None

        self.build_pid_controls_angle()
        if not global_config.only_inner_loop:
            self.build_pid_controls_velocity()
        self.build_status_labels()
        self.build_control_buttons()
        self.build_offset_input()
        if global_config.only_inner_loop:
            self.build_joystick_angle()
        else:
            self.build_joystick_velocity()
        self.bind_keys()
        self.refresh_values()

    def build_pid_controls_angle(self):
        for i, param in enumerate(["kp", "ki", "kd"]):
            tk.Label(self.root, text=param.upper()).grid(row=i, column=0)

            entry = tk.Entry(self.root)
            entry.insert(0, str(getattr(self.pid_manager.pid_tilt_angle_to_torque, param)))
            entry.grid(row=i, column=1)
            self.entries[param] = entry

            btn = tk.Button(self.root, text="Update", command=lambda p=param: self.update_pid_value_angle(p))
            btn.grid(row=i, column=2)

    def build_pid_controls_velocity(self):
        base_row = 0
        for i, param in enumerate(["kp", "ki", "kd"]):
            tk.Label(self.root, text=f"VEL {param.upper()}").grid(row=i, column=4)

            entry = tk.Entry(self.root)
            entry.insert(0, str(getattr(self.pid_manager.pid_velocity_to_tilt_angle, param)))
            entry.grid(row=i, column=5)
            self.entries[f"vel_{param}"] = entry

            btn = tk.Button(self.root, text="Update", command=lambda p=param: self.update_pid_value_velocity(p))
            btn.grid(row=i, column=6)

    def build_status_labels(self):
        labels = [
            ("Current Angle", self.angle_var),
            ("Target Angle", self.tgtangle_var),
            ("Angle Error",  self.error_var),
            ("Torque",       self.torque_var),
        ]

        velocity_labels = [
            ("Current Velocity", self.vel_var),
            ("Target Velocity", self.tgtvel_var),
            ("Velocity Error",  self.velerror_var),
        ]

        for j, (label, var) in enumerate(labels, start=4):
            tk.Label(self.root, text=label).grid(row=j, column=0)
            tk.Label(self.root, textvariable=var).grid(row=j, column=1)

        for j, (label, var) in enumerate(velocity_labels, start=4):
            tk.Label(self.root, text=label).grid(row=j, column=4)
            tk.Label(self.root, textvariable=var).grid(row=j, column=5)


    def build_control_buttons(self):
        button_config = [
            ("Stop (SPACE)", self.pid_manager.stop),
            ("Go Forward (W)", self.pid_manager.goForward),
            ("Go Backward (S)", self.pid_manager.goBackward),
        ]

        for i, (label, command) in enumerate(button_config, start=8):
            tk.Button(self.root, text=label, command=command).grid(row=i, column=0, columnspan=3, sticky="we", pady=2)

    def build_offset_input(self):
        tk.Label(self.root, text="Dynamic Offset").grid(row=7, column=0)
        self.offset_entry = tk.Entry(self.root)
        self.offset_entry.grid(row=7, column=1)

        tk.Button(self.root, text="Set Dynamic Offset", command=self.set_dynamic_offset).grid(row=7, column=2)

    def build_joystick_angle(self):
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

    def build_joystick_velocity(self):
        tk.Label(self.root, text="Joystick (Y-axis)").grid(row=11, column=0)
        self.joystick = tk.Scale(
            self.root,
            from_=15,
            to=-15,
            orient=tk.VERTICAL,
            resolution=0.1,
            command=self.update_control_velocity
        )
        self.joystick.set(0)
        self.joystick.grid(row=12, column=0, rowspan=3)

    def update_control_angle(self, value):
        try:
            val = float(value)
            self.pid_manager.setTargetAngle(val)
        except ValueError:
            print("Invalid joystick input.")

    def update_control_velocity(self, value):
        try:
            val = float(value)
            self.pid_manager.base_target_velocity(value)
        except ValueError:
            print("Invalid joystick input.")

    def set_dynamic_offset(self):
        try:
            offset_value = float(self.offset_entry.get())
            self.pid_manager.set_dynamic_target_angle_offset(offset_value)
        except ValueError:
            print("Invalid input for dynamic offset.")

    def bind_keys(self):
        self.root.bind("<w>", lambda event: self.pid_manager.goForward())
        self.root.bind("<s>", lambda event: self.pid_manager.goBackward())
        self.root.bind("<space>", lambda event: self.pid_manager.stop())

    def update_pid_value_angle(self, param):
        try:
            val = float(self.entries[param].get())
            setattr(self.pid_manager.pid_tilt_angle_to_torque, param, val)
        except ValueError:
            print(f"Invalid input for {param}")

    def update_pid_value_velocity(self, param):
        try:
            val = float(self.entries[f"vel_{param}"].get())
            setattr(self.pid_manager.pid_velocity_to_tilt_angle, param, val)
        except ValueError:
            print(f"Invalid input for velocity PID {param}")

    def refresh_values(self):
        current_angle, torque, current_velocity, target_velocity = self.get_state()
        target_angle = self.pid_manager.pid_tilt_angle_to_torque.target_angle
        error = target_angle - current_angle

        self.angle_var.set(f"{current_angle:.2f}")
        self.tgtangle_var.set(f"{target_angle:.2f}")
        self.error_var.set(f"{error:.2f}")
        self.torque_var.set(f"{torque:.2f}")

        vel_error = target_velocity - current_velocity
        self.vel_var.set(f"{current_velocity:.2f}")
        self.tgtvel_var.set(f"{target_velocity:.2f}")
        self.velerror_var.set(f"{vel_error:.2f}")

        self.root.after(100, self.refresh_values)
