from datetime import datetime

class LogEntry:
    def __init__(self, event_location, event_type, message):
        try:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except:
            self.timestamp = "Failed to get date"

        self.event_location = event_location
        self.event_type = event_type
        self.message = message

    def to_list(self):
        """ Returns log entry as a list for easy CSV export """
        return [self.timestamp, self.event_location, self.event_type, self.message]

    def __str__(self):
        """ Returns a formatted log entry string """
        return f"[{self.timestamp}] {self.event_location} {self.event_type} {self.message}"
