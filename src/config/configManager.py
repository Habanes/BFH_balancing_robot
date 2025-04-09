class ConfigManager:
    def __init__(self):
        print("LOADING CONFIG")
        
        self.only_inner_loop = True
        self.log_timings = False

        # === Main loop tick rate (can be used as base loop) ===
        self.main_loop_rate = 1000
        self.main_loop_interval = 1 / self.main_loop_rate
        self.base_velocity_loop_interval = self.main_loop_interval * 10
        self.log_interval = self.base_velocity_loop_interval / 2

        # === Motion and angle settings ===
        self.base_velocity = 0.0
        self.angle_neutral = 6.7
        self.angle_limit = 45.0
        self.tilt_angle_soft_limit = 0.9 * self.angle_limit

        # === Output limitations ===
        self.torque_limit = 1.0

        # === Other ===
        self.print_to_console = True
        self.debug_mode = True
        
# Create a single ConfigManager instance
global_config = ConfigManager()
