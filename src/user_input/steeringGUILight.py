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

        # === Shutdown ===
        shutdown_frame = ttk.Frame(master)
        shutdown_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        self.btn_shutdown = ttk.Button(shutdown_frame, text="Shutdown", command=self.shutdown)
        self.btn_shutdown.grid(row=0, column=0)

        # === Simplified PID Controls ===
        loop_frame = ttk.LabelFrame(master, text="PID: Tilt Angle → Torque")
        loop_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        pid = self.pid_manager.pid_tilt_angle_to_torque
        params = {"P": pid.kp, "I": pid.ki, "D": pid.kd}
        self.pid_vars = {}

        for i, (param, value) in enumerate(params.items()):
            var = tk.DoubleVar(value=value)
            self.pid_vars[param] = var

            ttk.Label(loop_frame, text=param).grid(row=0, column=i * 3)
            ttk.Entry(loop_frame, textvariable=var, width=8).grid(row=0, column=i * 3 + 1)
            ttk.Button(loop_frame, text="Update", command=lambda p=param, v=var: setattr(pid, p.lower(), v.get())).grid(row=0, column=i * 3 + 2)

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
        metrics = ["Tilt Angle", "Torque"]

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

    # === Shutdown Command ===
    def shutdown(self):
        print("Shutdown command issued")  # Replace with actual shutdown logic if needed

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
