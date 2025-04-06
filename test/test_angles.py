import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading
import numpy as np
from imu import IMU  # Your hardware interface
import smbus2 as smbus

# === CONFIG ===
PLOT_DURATION = 20  # seconds
PLOT_INTERVAL = 0.01  # seconds (100 Hz)
ANGLE_RANGE = (-45, 45)

class InertiaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Moment of Inertia Measurement")

        self.bus = smbus.SMBus(1)
        self.imu = IMU(self.bus)

        self.running = False
        self.setup_widgets()     # Moved up
        self.reset_data()        # Moved down
        self.update_labels_loop()

    def reset_data(self):
        self.start_time = None
        self.times = []
        self.angles = []
        self.period_var.set("Estimated Period: N/A")

    def setup_widgets(self):
        # Time & Angle Labels
        self.time_label = ttk.Label(self.root, text="Time: 0.00 s")
        self.time_label.pack()

        self.angle_label = ttk.Label(self.root, text="Angle: 0.00 °")
        self.angle_label.pack()

        self.period_var = tk.StringVar()
        self.period_label = ttk.Label(self.root, textvariable=self.period_var)
        self.period_label.pack()

        # Matplotlib Figure
        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.ax.set_xlim(0, PLOT_DURATION)
        self.ax.set_ylim(*ANGLE_RANGE)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Pitch Angle (°)")
        self.line, = self.ax.plot([], [], lw=2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_recording)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_recording)
        self.stop_btn.pack(side="left", padx=5)

        self.reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset)
        self.reset_btn.pack(side="left", padx=5)

        self.calc_period_btn = ttk.Button(btn_frame, text="Calc Period", command=self.calculate_period)
        self.calc_period_btn.pack(side="left", padx=5)

    def update_labels_loop(self):
        pitch = self.imu.read_pitch()
        current_time = time.time() - self.start_time if self.start_time else 0

        self.time_label.config(text=f"Time: {current_time:.2f} s")
        self.angle_label.config(text=f"Angle: {pitch:.2f} °")

        if self.running:
            self.times.append(current_time)
            self.angles.append(pitch)
            self.update_plot()

            if current_time >= PLOT_DURATION:
                self.running = False
                self.calculate_period()

        self.root.after(int(PLOT_INTERVAL * 1000), self.update_labels_loop)

    def update_plot(self):
        self.line.set_data(self.times, self.angles)
        self.ax.set_xlim(0, max(PLOT_DURATION, self.times[-1]))
        self.canvas.draw()

    def start_recording(self):
        if not self.running:
            self.running = True
            if not self.start_time:
                self.start_time = time.time()

    def stop_recording(self):
        self.running = False

    def reset(self):
        self.running = False
        self.reset_data()
        self.line.set_data([], [])
        self.canvas.draw()

    def calculate_period(self):
        if len(self.times) < 3:
            self.period_var.set("Estimated Period: Not enough data")
            return

        angles = np.array(self.angles)
        times = np.array(self.times)

        # Simple peak detection without scipy
        peaks = []
        for i in range(1, len(angles) - 1):
            if angles[i - 1] < angles[i] > angles[i + 1] and angles[i] > 2.0:
                peaks.append(i)

        if len(peaks) < 2:
            self.period_var.set("Estimated Period: Too few peaks")
            return

        peak_times = times[peaks]
        periods = [peak_times[i+1] - peak_times[i] for i in range(len(peak_times)-1)]
        avg_period = sum(periods) / len(periods)

        self.period_var.set(f"Estimated Period: {avg_period:.3f} s")

if __name__ == "__main__":
    root = tk.Tk()
    app = InertiaGUI(root)
    root.mainloop()
