import os
import json
import uuid
import socket
import threading
import traceback
import datetime
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"

class Logger:
    def __init__(self, logger_name="App"):
        self.logger_name = logger_name
        # Use absolute path for logs to avoid CWD issues
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.log_dir = os.path.join(self.base_dir, "logs")
        self.max_file_size = 100 * 1024 * 1024 # 100MB
        
        self.system_id = self._get_system_id()
        self.host = socket.gethostname()
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _get_system_id(self):
        try:
            return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
            for ele in range(0,8*6,8)][::-1])
        except:
            return "unknown"

    def _get_log_filename(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"{today}.log")

    def _rotate_log(self, current_file):
        # Rename current to part X
        base_name = os.path.basename(current_file) # 2023-10-27.log
        name_part, ext = os.path.splitext(base_name) # 2023-10-27, .log
        
        part = 1
        while True:
            new_name = os.path.join(self.log_dir, f"{name_part}_part{part}{ext}")
            if not os.path.exists(new_name):
                try:
                    os.rename(current_file, new_name)
                except OSError:
                    # Could happen if file is locked or race condition
                    pass 
                break
            part += 1

    def log(self, level, message, stack_trace=None):
        try:
            entry = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "system_id": self.system_id,
                "level": level,
                "logger_name": self.logger_name,
                "host": self.host,
                "message": str(message),
                "tid": threading.get_ident(),
                "pid": os.getpid(),
            }
            
            if stack_trace:
                entry["stack_trace"] = stack_trace
                
            json_entry = json.dumps(entry)
            
            # Write to file
            filename = self._get_log_filename()
            
            # Check rotation
            if os.path.exists(filename):
                if os.path.getsize(filename) >= self.max_file_size:
                    self._rotate_log(filename)
            
            with open(filename, "a", encoding="utf-8") as f:
                f.write(json_entry + "\n")
                
            # Also print to console for dev visibility
            print(f"[{level}] {message}") 
            
        except Exception as e:
            # Fallback if logging fails
            print(f"LOGGING FAILED: {e}")

    def debug(self, msg): self.log(LogLevel.DEBUG, msg)
    def info(self, msg): self.log(LogLevel.INFO, msg)
    def warn(self, msg): self.log(LogLevel.WARN, msg)
    def warning(self, msg): self.log(LogLevel.WARN, msg)
    def error(self, msg, exc_info=False): 
        stack = traceback.format_exc() if exc_info else None
        self.log(LogLevel.ERROR, msg, stack)
    def fatal(self, msg, exc_info=True):
        stack = traceback.format_exc() if exc_info else None
        self.log(LogLevel.FATAL, msg, stack)

# Global factory
_loggers = {}

def get_logger(name="App"):
    if name not in _loggers:
        _loggers[name] = Logger(name)
    return _loggers[name]
