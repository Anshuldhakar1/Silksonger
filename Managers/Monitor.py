import datetime
import os
import time
import dictdiffer
import threading
from typing import Optional

class MonitorThread(threading.Thread):
    def __init__(self, filepath: str, callback, interval: float = 0.1):
        super().__init__()
        self.filepath = filepath
        self.callback = callback
        self.interval = interval
        self.running = True
        self.last_read_time: Optional[float] = None

    def run(self):
        while self.running:
            try:
                with open(self.filepath, 'rb') as f:
                    # If we can open the file, it's not being written to
                    if self.last_read_time is not None:
                        # Call callback with the file handle
                        self.callback(f)
                    self.last_read_time = time.time()
            except (PermissionError, OSError):
                # File is being written to - we'll catch it on the next iteration
                pass
            time.sleep(self.interval)

    def stop(self):
        self.running = False

class Monitor:
    def __init__(self, root):
        self.root = root
        self.is_target_set = False
        self.is_monitoring = False
        self.target_file = None
        self.monitor_thread: Optional[MonitorThread] = None
        self.previous_data = None
        self._is_shutting_down = False

    def set_target(self, filepath: str):
        self.target_file = filepath
        self.is_target_set = True
        self.previous_data = self.root.M_fileHandler.read_file_content(self.target_file)

    def release_target(self):
        self.stop_monitoring()
        self.is_target_set = False
        self.target_file = None
        self.previous_data = None

    def get_target(self):
        return self.target_file

    def start_monitoring(self):
        if not self.is_target_set:
            self.root.W_dashboard.main_log("No file selected to monitor", "ERROR")
            return

        self.is_monitoring = True
        self.monitor_thread = MonitorThread(
            self.target_file,
            self._handle_file_access
        )
        self.monitor_thread.start()
        self.root.W_dashboard.main_log(f"Started monitoring {os.path.basename(self.target_file)}", "START")
        self.root.W_dashboard.main_log("Waiting for changes...", "INFO")

    def cleanup(self):
        """Clean up resources when application is closing"""
        self._is_shutting_down = True
        self.stop_monitoring()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.running = False
            self.monitor_thread.join(timeout=1.0)  # Wait up to 1 second for thread to finish

    def stop_monitoring(self):
        if not self.is_monitoring:
            return
        if not self._is_shutting_down:
            self.root.W_dashboard.main_log("Monitoring stopped", "STOP")
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.stop()
            self.monitor_thread.join()
            self.monitor_thread = None
        self.is_monitoring = False

    def _handle_file_access(self, file_handle):
        try:
            current_data = self.root.M_fileHandler.read_file_content(self.target_file)
            if not current_data:
                self.root.W_dashboard.main_log("No data read from file", "ERROR")
                return

            # Compare old data vs new data
            diff = list(dictdiffer.diff(self.previous_data, current_data))

            if diff:
                change_data = {
                    "filepath": self.target_file,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "diff": diff,
                }
                
                self.root.W_dashboard.main_log(f"Found {len(diff)} changes in {os.path.basename(self.target_file)}", "MODIFY")
                self.root.show_notification(change_data)  # Pass change_data to notification
                self.previous_data = current_data

        except Exception as e:
            self.root.W_dashboard.main_log(f"Error processing changes: {e}", "ERROR")