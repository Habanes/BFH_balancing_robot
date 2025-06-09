class ConfigManager:
    def __init__(self):
        print("LOADING CONFIG")
        
        # === Basic settings ===
        self.test_mode = False
        self.debug_mode = True
        self.print_to_console = True

        # === IMU and angle settings ===
        self.imu_angle_offset = 6.7
        self.angle_neutral = 0.0
        self.angle_limit = 60.0
        self.tilt_angle_soft_limit = 30.0
        self.angle_move = 3
        self.angle_limit_time_delay = 1.0

        # === Torque settings ===
        self.torque_differential = 0.1
        self.torque_limit = 1.0
        self.torque_differential_limit = 0.1

        # === Control loop update rates (Hz) ===
        self.velocity_to_tilt_angle_rate = 1000             # velocity → desired tilt angle
        self.tilt_angle_to_torque_rate = 5000               # measured tilt angle → torque
        self.estimated_torque_to_actual_torque_rate = 10000 # estimated torque → corrected torque
        self.angular_velocity_to_torque_diff_rate = 1000    # yaw rate → torque differential

        # === Control loop intervals (s) ===
        self.velocity_to_tilt_angle_interval = 1 / self.velocity_to_tilt_angle_rate
        self.tilt_angle_to_torque_interval = 1 / self.tilt_angle_to_torque_rate
        self.estimated_torque_to_actual_torque_interval = 1 / self.estimated_torque_to_actual_torque_rate
        self.angular_velocity_to_torque_diff_interval = 1 / self.angular_velocity_to_torque_diff_rate

        # === Main loop tick rate ===
        self.main_loop_rate = 10000
        self.main_loop_interval = 1 / self.main_loop_rate


# Create a single ConfigManager instance
global_config = ConfigManager()
