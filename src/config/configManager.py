class ConfigManager:
    def __init__(self):
        print("LOADING CONFIG")
        
        self.test_mode = False
        
        # === IMU Calibration (CONSOLIDATED) ===
        # Angle IMU reads when robot is perfectly upright - used to correct mounting offset
        self.imu_mounting_offset = -6.7
        
        self.torque_differential = 0.1

        # === Control loop update rates (Hz) ===
        self.velocity_to_tilt_angle_rate = 1000             # velocity → desired tilt angle
        self.tilt_angle_to_torque_rate = 5000               # measured tilt angle → torque
        self.angular_velocity_to_torque_diff_rate = 1000    # yaw rate → torque differential

        # === Control loop intervals (s) ===
        self.velocity_to_tilt_angle_interval = 1 / self.velocity_to_tilt_angle_rate
        self.tilt_angle_to_torque_interval = 1 / self.tilt_angle_to_torque_rate
        self.angular_velocity_to_torque_diff_interval = 1 / self.angular_velocity_to_torque_diff_rate        # === Main loop tick rate (can be used as base loop) ===
        # PERFORMANCE NOTE: Timing analysis shows severe performance issues:
        # - IMU reads: 0.67ms average (67% of 1ms budget)
        # - Total loop: 7.3ms average vs 0.2ms target
        # - Max delays: 1200ms (6000x over budget!)
        # 
        # Conservative approach: 50Hz main loop (20ms interval)
        # This provides 30x safety margin over worst-case measurements
        self.main_loop_rate = 50  # Ultra-conservative based on actual performance data
        self.main_loop_interval = 1 / self.main_loop_rate        # === Motion and angle settings ===
        self.base_velocity = 0.1
        self.angle_neutral = 0.0
        self.angle_rotation_speed = 90.0  # degrees per second
        # Updated for 50Hz main loop rate
        self.angle_rotation = self.angle_rotation_speed / self.main_loop_rate  # Now 1.8 degrees per loop
        self.angle_limit = 60.0
        self.tilt_angle_soft_limit = 30.0

        # === Output limitations ===
        self.torque_limit = 1.0
        self.torque_differential_limit = 0.1

        # === Other ===
        self.angle_limit_time_delay = 1.0
        self.print_to_console = True
        self.debug_mode = True
        
        self.angle_move = 3


# Create a single ConfigManager instance
global_config = ConfigManager()
