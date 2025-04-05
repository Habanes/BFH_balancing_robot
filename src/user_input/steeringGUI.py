import tkinter as tk
from tkinter import ttk
from src.pid.pidManager import pidManager
from src.config.configManager import global_config

class SteeringGUI:
    def __init__(self, master, pid_manager: pidManager):
        self.master = master
        self.master.title("Robot Control Panel")
        self.pid_manager = pid_manager

        # Style
        self.style = ttk.Style()
        self.style.configure("Flashing.TButton", background="yellow")

        # === Steering Controls ===
        direction_frame = ttk.LabelFrame(master, text="Steering Controls")
        direction_frame.grid(row=0, column=0, padx=10, pady=10)

        # Only show forward/backward if velocity loop is enabled
        if global_config.enable_velocity_loop:
            self.btn_forward = ttk.Button(direction_frame, text="Move Forward", command=self.move_forward)
            self.btn_forward.grid(row=0, column=1)

            self.btn_backward = ttk.Button(direction_frame, text="Move Backward", command=self.move_backward)
            self.btn_backward.grid(row=2, column=1)
        else:
            self.btn_forward = None
            self.btn_backward = None

        # Always show Halt
        self.btn_halt = ttk.Button(direction_frame, text="Halt", command=self.halt)
        self.btn_halt.grid(row=1, column=1)

        # Only show rotate left/right if yaw loop is enabled
        if global_config.enable_yaw_loop:
            self.btn_left = ttk.Button(direction_frame, text="Rotate Left", command=self.rotate_left)
            self.btn_left.grid(row=1, column=0)

            self.btn_right = ttk.Button(direction_frame, text="Rotate Right", command=self.rotate_right)
            self.btn_right.grid(row=1, column=2)
        else:
            self.btn_left = None
            self.btn_right = None

        # === Shutdown ===
        shutdown_frame = ttk.Frame(master)
        shutdown_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        self.btn_shutdown = ttk.Button(shutdown_frame, text="Shutdown", command=self.shutdown)
        self.btn_shutdown.grid(row=0, column=0)

        # === PID Controls ===
        self.pid_vars = []

        pid_loop_configs = [
            (global_config.enable_velocity_loop, "Velocity → Tilt Angle", self.pid_manager.pid_velocity_to_tilt_angle),
            (True, "Tilt Angle → Torque", self.pid_manager.pid_tilt_angle_to_torque),  # always active
            (global_config.enable_torque_feedback_loop, "Estimated Torque → Torque", self.pid_manager.pid_estimated_torque_to_torque),
            (global_config.enable_yaw_loop, "Yaw Rate → Torque Diff", self.pid_manager.pid_angular_velocity_to_torque_differential),
        ]

        loop_row = 1
        for enabled, label, pid in pid_loop_configs:
            if not enabled:
                continue

            loop_frame = ttk.LabelFrame(master, text=f"PID: {label}")
            loop_frame.grid(row=loop_row, column=0, columnspan=2, padx=10, pady=5, sticky="w")
            loop_row += 1

            loop_vars = []
            for i, param in enumerate(["P", "I", "D"]):
                var = tk.DoubleVar()
                if param == "P":
                    var.set(pid.kp)
                elif param == "I":
                    var.set(pid.ki)
                elif param == "D":
                    var.set(pid.kd)
                loop_vars.append(var)

                ttk.Label(loop_frame, text=param).grid(row=0, column=i * 3)
                ttk.Entry(loop_frame, textvariable=var, width=8).grid(row=0, column=i * 3 + 1)
                ttk.Button(loop_frame, text="Update", command=lambda p=param, pid_obj=pid: setattr(pid_obj, p.lower(), var.get())).grid(row=0, column=i * 3 + 2)

            self.pid_vars.append(loop_vars)

        # === Y Angle Offset ===
        y_angle_frame = ttk.LabelFrame(master, text="Y Angle Offset")
        y_angle_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.y_offset_var = tk.DoubleVar(value=self.pid_manager.angle_y_offset)
        ttk.Label(y_angle_frame, text="Offset").grid(row=0, column=0)
        ttk.Entry(y_angle_frame, textvariable=self.y_offset_var, width=8).grid(row=0, column=1)
        ttk.Button(y_angle_frame, text="Update", command=self.update_y_offset).grid(row=0, column=2)

        # === Dashboard ===
        dashboard_frame = ttk.LabelFrame(master, text="Value Dashboard")
        dashboard_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.dashboard_vars = {}
        metrics = ["Velocity", "Tilt Angle", "Z Angular Velocity", "Torque"]

        for i, metric in enumerate(metrics):
            ttk.Label(dashboard_frame, text=metric).grid(row=i, column=0, sticky="w")
            self.dashboard_vars[metric] = {
                "target": tk.StringVar(value="0.0"),
                "measured": tk.StringVar(value="0.0"),
                "diff": tk.StringVar(value="0.0")
            }
            ttk.Label(dashboard_frame, text="Target").grid(row=i, column=1)
            ttk.Entry(dashboard_frame, textvariable=self.dashboard_vars[metric]["target"], width=10, state="readonly").grid(row=i, column=2)

            ttk.Label(dashboard_frame, text="Measured").grid(row=i, column=3)
            ttk.Entry(dashboard_frame, textvariable=self.dashboard_vars[metric]["measured"], width=10, state="readonly").grid(row=i, column=4)

            ttk.Label(dashboard_frame, text="Diff").grid(row=i, column=5)
            ttk.Entry(dashboard_frame, textvariable=self.dashboard_vars[metric]["diff"], width=10, state="readonly").grid(row=i, column=6)

        # === Key bindings ===
        # If a button doesn't exist (disabled loop), the binding won't matter, but it's safe to leave them
        master.bind("<w>", lambda e: self._flash(self.btn_forward, self.move_forward) if self.btn_forward else None)
        master.bind("<a>", lambda e: self._flash(self.btn_left, self.rotate_left) if self.btn_left else None)
        master.bind("<s>", lambda e: self._flash(self.btn_backward, self.move_backward) if self.btn_backward else None)
        master.bind("<d>", lambda e: self._flash(self.btn_right, self.rotate_right) if self.btn_right else None)
        master.bind("<space>", lambda e: self._flash(self.btn_halt, self.halt))
        master.bind("<q>", lambda e: self._flash(self.btn_shutdown, self.shutdown))

    def _flash(self, button, action_fn):
        """Simple 'flash' effect if the button exists."""
        if not button:
            return
        button.configure(style="Flashing.TButton")
        self.master.after(150, lambda: button.configure(style="TButton"))
        action_fn()

    # === Movement Commands ===
    def move_forward(self):
        self.pid_manager.goForward()
        print("Move Forward")

    def move_backward(self):
        self.pid_manager.goBackward()
        print("Move Backward")

    def rotate_left(self):
        self.pid_manager.rotateLeft()
        print("Rotate Left")

    def rotate_right(self):
        self.pid_manager.rotateRight()
        print("Rotate Right")

    def halt(self):
        self.pid_manager.stop()
        print("Halt")

    def shutdown(self):
        print("Shutdown")

    # === PID Update Command ===
    def update_pid(self, loop_index, param_index):
        """(Unused by the new approach, but left for reference)"""
        value = self.pid_vars[loop_index][param_index].get()
        pid_loops = [
            self.pid_manager.pid_velocity_to_tilt_angle,
            self.pid_manager.pid_tilt_angle_to_torque,
            self.pid_manager.pid_estimated_torque_to_torque,
            self.pid_manager.pid_angular_velocity_to_torque_differential
        ]
        pid = pid_loops[loop_index]
        param = ["kp", "ki", "kd"][param_index]
        setattr(pid, param, value)
        print(f"Updated PID {loop_index + 1} - {param.upper()} set to {value}")

    # === Angle Offset Update ===
    def update_y_offset(self):
        value = self.y_offset_var.get()
        self.pid_manager.angle_y_offset = value
        print(f"Y Angle Offset updated to {value}")

    # === Dashboard Update ===
    def update_dashboard_value(self, category, target, measured):
        if category in self.dashboard_vars:
            self.dashboard_vars[category]["target"].set(f"{target:.2f}")
            self.dashboard_vars[category]["measured"].set(f"{measured:.2f}")
            diff = measured - target
            self.dashboard_vars[category]["diff"].set(f"{diff:.2f}")
