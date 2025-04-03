import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

from src.config.configManager import global_config

class steeringGUI:
    def __init__(self, master, controller, imu):
        self.master = master
        self.master.title("Self-Balancing Robot Control")
        self.controller = controller
        self.imu = imu

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

        # Angle Y Offset Configuration
        offset_frame = ttk.LabelFrame(master, text="Angle Y Offset")
        offset_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.angleYOffset = tk.DoubleVar(value=self.controller.getAngleYOffset())
        ttk.Label(offset_frame, text="Offset").grid(row=0, column=0)
        ttk.Entry(offset_frame, textvariable=self.angleYOffset).grid(row=0, column=1)
        ttk.Button(offset_frame, text="Update", command=self.update_angle_y_offset).grid(row=0, column=2)

        # === Live Plot Frame ===
        plot_frame = ttk.LabelFrame(master, text="Live PID Plot")
        plot_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(6, 3), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack()

        self.set_angles = deque(maxlen=100)
        self.est_angles = deque(maxlen=100)
        self.errors = deque(maxlen=100)

        self.ani = FuncAnimation(self.fig, self.update_plot, interval=200)

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

    def update_angle_y_offset(self):
        new_offset = self.angleYOffset.get()
        self.controller.setAngleYOffset(new_offset)
        print(f"[OFFSET] angleYOffset updated to {new_offset}")

    def log_angles(self, action):
        print(f"[{action}] angleY = {self.controller.getAngleY()}, angleZ = {self.controller.getAngleZ()}")

    def update_plot(self, frame):
        try:
            est_angle = -self.imu.read_pitch()
            set_angle = self.controller.getAngleY()
            error = set_angle - est_angle

            self.set_angles.append(set_angle)
            self.est_angles.append(est_angle)
            self.errors.append(error)

            self.ax.clear()
            self.ax.plot(self.set_angles, label="Setpoint")
            self.ax.plot(self.est_angles, label="Estimated")
            self.ax.plot(self.errors, label="Error")
            self.ax.set_ylim(-90, 90)
            self.ax.legend(loc="upper right")
            self.ax.set_title("Live PID Tracking")
        except Exception as e:
            print(f"[PLOT ERROR] {e}")
