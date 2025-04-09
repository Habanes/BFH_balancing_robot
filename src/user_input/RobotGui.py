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
        self.build_offset_input()
        self.build_analog_joystick()
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

    def build_offset_input(self):
        tk.Label(self.root, text="Dynamic Offset").grid(row=7, column=0)
        self.offset_entry = tk.Entry(self.root)
        self.offset_entry.grid(row=7, column=1)

        tk.Button(self.root, text="Set Dynamic Offset", command=self.set_dynamic_offset).grid(row=7, column=2)

    def build_analog_joystick(self):
        tk.Label(self.root, text="Analog Joystick").grid(row=11, column=0, columnspan=2)

        self.joystick_canvas = tk.Canvas(self.root, width=150, height=150, bg="lightgray")
        self.joystick_canvas.grid(row=12, column=0, columnspan=2, rowspan=3)

        self.joystick_radius = 60
        self.knob_radius = 10
        self.center = (75, 75)
        self.knob = self.joystick_canvas.create_oval(
            75 - self.knob_radius, 75 - self.knob_radius,
            75 + self.knob_radius, 75 + self.knob_radius,
            fill="blue"
        )

        self.joystick_canvas.bind("<B1-Motion>", self.on_joystick_drag)
        self.joystick_canvas.bind("<ButtonRelease-1>", self.reset_joystick)

    def on_joystick_drag(self, event):
        dx = event.x - self.center[0]
        dy = event.y - self.center[1]
        dist = (dx**2 + dy**2)**0.5

        if dist > self.joystick_radius:
            scale = self.joystick_radius / dist
            dx *= scale
            dy *= scale

        x = self.center[0] + dx
        y = self.center[1] + dy
        self.joystick_canvas.coords(
            self.knob,
            x - self.knob_radius, y - self.knob_radius,
            x + self.knob_radius, y + self.knob_radius
        )

        norm_x = dx / self.joystick_radius   # for future use (steering)
        norm_y = -dy / self.joystick_radius  # inverted Y for logical control

        try:
            self.pid_manager.setTargetAngle(norm_y)
            # self.pid_manager.setSteering(norm_x)  # for future use
        except AttributeError:
            pass

    def reset_joystick(self, _event):
        self.joystick_canvas.coords(
            self.knob,
            self.center[0] - self.knob_radius, self.center[1] - self.knob_radius,
            self.center[0] + self.knob_radius, self.center[1] + self.knob_radius
        )
        try:
            self.pid_manager.setTargetAngle(0.0)
            # self.pid_manager.setSteering(0.0)  # for future use
        except AttributeError:
            pass

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
