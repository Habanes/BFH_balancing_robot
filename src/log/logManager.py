from src.config.configManager import global_config
from src.log.logEntry import LogEntry
import logging

class LogManager:
    def __init__(self, print_to_console=False, debug_mode=False):
        self.print_to_console = print_to_console
        self.debug_mode = debug_mode
        self.log_entries = []

    def log_info(self, message, location=None):
        """ Logs an informational message. """
        self._log_event("INFO", message, location)
        logging.info(message)

    def log_warning(self, message, location=None):
        """ Logs a warning message. """
        self._log_event("WARNING", message, location)
        logging.warning(message)

    def log_error(self, message, location=None):
        """ Logs an error message. """
        self._log_event("ERROR", message, location)
        logging.error(message)

    def log_critical(self, message, location=None):
        """ Logs a critical error message. """
        self._log_event("CRITICAL", message, location)
        logging.critical(message)

    def log_debug(self, message, location=None):
        """ Logs a debug message if debug mode is enabled. """
        if self.debug_mode:
            self._log_event("DEBUG", message, location)
            logging.debug(message)

    def _log_event(self, event_type, message, location):
        """ Internal method to log an event. """
        log_entry = LogEntry(location, event_type, message)
        self.log_entries.append(log_entry)

        if self.print_to_console:
            print(f"[{log_entry.timestamp}] - {log_entry.event_type} - {log_entry.event_location} - {log_entry.message}")

    def get_logs(self):
        """ Returns logs as a list of lists for easy processing (e.g., CSV export). """
        return [entry.to_list() for entry in self.log_entries]
    

global_log_manager = global_log_manager = LogManager(print_to_console=global_config.print_to_console, debug_mode=global_config.debug_mode)
