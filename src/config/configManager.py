import os
from typing import List
import logging

class ConfigManager:
    def __init__(self):
        print("LOADING CONFIG")
        
        self.test_mode = False

        # Logging
        self.debug_mode = True
        self.print_to_console = True

        self.valid = True
        logging.info("CONFIG LOAD SUCCESS")
        
# Create a single ConfigManager instance
global_config = ConfigManager()