class ConfigManager:
    def __init__(self):
        print("LOADING CONFIG")
        
        self.test_mode = False
        
        self.only_inner_loop = True

        # === Main loop tick rate (can be used as base loop) ===
        self.main_loop_rate = 500
        self.main_loop_interval = 1 / self.main_loop_rate

        # === Motion and angle settings ===
        self.base_velocity = 0.1
        self.angle_neutral = 0.0
        self.angle_offset = 6.7
        self.angle_rotation_speed = 90.0  # degrees per second
        self.angle_rotation = self.angle_rotation_speed / self.main_loop_rate
        self.angle_limit = 45.0
        self.tilt_angle_soft_limit = 0.9 * self.angle_limit

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
