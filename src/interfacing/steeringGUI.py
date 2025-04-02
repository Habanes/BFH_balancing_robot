import tkinter as tk
from tkinter import ttk
from src.config.configManager import global_config

class steeringGUI:
    def __init__(self, master, controller):
        self.master = master
        self.master.title("Self-Balancing Robot Control")
        self.controller = controller

        # Control Buttons (Direction)
        control_frame = ttk.LabelFrame(master, text="Directional Controls")
        control_frame.grid(row=0, column=0, padx=20, pady=20)

        ttk.Button(control_frame, text="Forward", command=self.go_forward).grid(row=0, column=1)
        ttk.Button(control_frame, text="Left", command=self.rotate_left).grid(row=1, column=0)
        ttk.Button(control_frame, text="Right", command=self.rotate_right).grid(row=1, column=2)
        ttk.Button(control_frame, text="Back", command=self.go_backward).grid(row=2, column=1)

        # Motor Control Buttons (Start/Stop)
        motor_frame = ttk.LabelFrame(master, text="Motor Control")
        motor_frame.grid(row=0, column=1, padx=20, pady=20, sticky="n")

        ttk.Button(motor_frame, text="Start", command=lambda: self.send_command("start")).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(motor_frame, text="Stop", command=lambda: self.send_command("stop")).grid(row=1, column=0, padx=10, pady=5)

        # PID Controls
        pid_frame = ttk.LabelFrame(master, text="PID Settings")
        pid_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.kp = tk.DoubleVar(value=global_config.init_kp)
        self.ki = tk.DoubleVar(value=global_config.init_ki)
        self.kd = tk.DoubleVar(value=global_config.init_kd)

        ttk.Label(pid_frame, text="Kp").grid(row=0, column=0)
        ttk.Entry(pid_frame, textvariable=self.kp).grid(row=0, column=1)
        ttk.Button(pid_frame, text="Update", command=self.update_kp).grid(row=0, column=2)

        ttk.Label(pid_frame, text="Ki").grid(row=1, column=0)
        ttk.Entry(pid_frame, textvariable=self.ki).grid(row=1, column=1)
        ttk.Button(pid_frame, text="Update", command=self.update_ki).grid(row=1, column=2)

        ttk.Label(pid_frame, text="Kd").grid(row=2, column=0)
        ttk.Entry(pid_frame, textvariable=self.kd).grid(row=2, column=1)
        ttk.Button(pid_frame, text="Update", command=self.update_kd).grid(row=2, column=2)

    def go_forward(self):
        self.controller.goForward()
        self.log_angles("Forward")

    def go_backward(self):
        self.controller.goBackward()
        self.log_angles("Backward")

    def rotate_left(self):
        self.controller.rotateLeft()
        self.log_angles("Left")

    def rotate_right(self):
        self.controller.rotateRight()
        self.log_angles("Right")

    def send_command(self, command):
        print(f"[COMMAND] {command}")
        self.log_angles(command)

    def update_kp(self):
        new_kp = self.kp.get()
        self.controller.setKpY(new_kp)
        print(f"[PID] Kp updated to {new_kp}")

    def update_ki(self):
        new_ki = self.ki.get()
        self.controller.setKiY(new_ki)
        print(f"[PID] Ki updated to {new_ki}")

    def update_kd(self):
        new_kd = self.kd.get()
        self.controller.setKdY(new_kd)
        print(f"[PID] Kd updated to {new_kd}")

    def log_angles(self, action):
        print(f"[{action}] angleY = {self.controller.getAngleY()}, angleZ = {self.controller.getAngleZ()}")
        