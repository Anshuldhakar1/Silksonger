import datetime
import os
import time
import dictdiffer
import threading
import hashlib
from typing import Optional, Literal
from abc import ABC, abstractmethod

# --- Helper Function for HashDetector ---

def calculate_file_hash(filepath: str) -> Optional[str]:
    """Calculates the SHA-256 hash of a file, handling potential read errors."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read in chunks to handle large files efficiently
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (PermissionError, OSError, FileNotFoundError):
        # File might be locked or may have been deleted
        return None

# --- Strategy Pattern: Abstract Base Class ---

class ChangeDetector(ABC):
    """
    Abstract base class for a file change detection strategy.
    This defines the contract for all detection methods.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        # Initialize the baseline on creation
        self.update_baseline()

    @abstractmethod
    def has_changed(self) -> bool:
        """Checks if the file has changed since the last baseline."""
        pass

    @abstractmethod
    def update_baseline(self):
        """Updates the baseline to the current file state."""
        pass

# --- Concrete Strategy 1: Modification Time (mtime) ---

class MTimeDetector(ChangeDetector):
    """Detects changes based on the file's last modification time."""
    def __init__(self, filepath: str):
        self.last_mtime: float = 0.0
        super().__init__(filepath)

    def _get_mtime(self) -> float:
        """Safely get the modification time."""
        try:
            return os.path.getmtime(self.filepath)
        except (FileNotFoundError, PermissionError):
            return 0.0 # Return a default, non-triggering value

    def has_changed(self) -> bool:
        current_mtime = self._get_mtime()
        # A new, valid mtime that is different from the last one indicates a change.
        return current_mtime > 0 and current_mtime != self.last_mtime

    def update_baseline(self):
        self.last_mtime = self._get_mtime()

# --- Concrete Strategy 2: File Hash (SHA-256) ---

class HashDetector(ChangeDetector):
    """Detects changes based on the file's SHA-256 hash."""
    def __init__(self, filepath: str):
        self.last_hash: Optional[str] = None
        super().__init__(filepath)

    def has_changed(self) -> bool:
        current_hash = calculate_file_hash(self.filepath)
        # A new, valid hash that is different from the last one indicates a change.
        return current_hash is not None and current_hash != self.last_hash

    def update_baseline(self):
        self.last_hash = calculate_file_hash(self.filepath)


# --- Refactored MonitorThread ---

class MonitorThread(threading.Thread):
    """
    A simple thread that runs a loop, using an injected ChangeDetector
    strategy to check for file modifications.
    """
    def __init__(self, detector: ChangeDetector, callback, interval: float = 1.0):
        super().__init__()
        self.detector = detector  # Injected dependency
        self.callback = callback
        self.interval = interval
        self.running = True

    def run(self):
        while self.running:
            try:
                if self.detector.has_changed():
                    # If a change is detected, call the main class's
                    # handler function to process the diff.
                    self.callback()
            except Exception as e:
                # Log errors from the detector itself (e.g., file deleted)
                print(f"Error in MonitorThread: {e}")
            
            time.sleep(self.interval)

    def stop(self):
        self.running = False

# --- Refactored Main Monitor Class ---

DetectionMethod = Literal["hash", "mtime"]

class Monitor:
    """
    Manages file monitoring using a specified detection strategy.
    """
    def __init__(self, root, detection_method: DetectionMethod = "mtime"):
        """
        Initializes the Monitor.
        
        Args:
            root: The root application object (used for callbacks).
            detection_method: The strategy to use.
                - "hash": (Default) Robust, checks file content via SHA-256.
                - "mtime": Faster, checks file modification time.
        """
        self.root = root
        self.is_target_set = False
        self.is_monitoring = False
        self.target_file: Optional[str] = None
        self.monitor_thread: Optional[MonitorThread] = None
        self.previous_data: Optional[dict] = None # Assuming JSON/dict data
        self._is_shutting_down = False

        # --- Dependency Injection ---
        self.detection_method: DetectionMethod = detection_method
        self.detector: Optional[ChangeDetector] = None
        # ----------------------------

    def _create_detector(self, filepath: str) -> ChangeDetector:
        """
        Factory method to create the appropriate detector strategy.
        This is where the "injection" logic lives.
        """
        if self.detection_method == "mtime":
            self.root.W_dashboard.main_log("Using 'Modification Time' detector", "INFO")
            return MTimeDetector(filepath)
        elif self.detection_method == "hash":
            self.root.W_dashboard.main_log("Using 'File Hash (SHA-256)' detector", "INFO")
            return HashDetector(filepath)
        else:
            raise ValueError(f"Unknown detection method: {self.detection_method}")

    def set_target(self, filepath: str):
        self.target_file = filepath
        self.is_target_set = True
        
        # Perform initial read and create the detector strategy
        try:
            self.previous_data = self.root.M_fileHandler.read_file_content(self.target_file)
            # Create and inject the chosen detector
            self.detector = self._create_detector(filepath)
        except Exception as e:
            self.root.W_dashboard.main_log(f"Failed to set target {filepath}: {e}", "ERROR")
            self.is_target_set = False


    def release_target(self):
        self.stop_monitoring()
        self.is_target_set = False
        self.target_file = None
        self.previous_data = None
        self.detector = None # Clean up the detector object

    def get_target(self):
        return self.target_file

    def start_monitoring(self):
        if not self.is_target_set or not self.detector or not self.target_file:
            self.root.W_dashboard.main_log("No file selected or detector set", "ERROR")
            return

        self.is_monitoring = True
        self.monitor_thread = MonitorThread(
            detector=self.detector,
            callback=self._handle_file_change,
            interval=1.0 # You could make this interval configurable
        )
        self.monitor_thread.start()
        self.root.W_dashboard.main_log(f"Started monitoring {os.path.basename(self.target_file)}", "START")
        self.root.W_dashboard.main_log(f"Waiting for changes via '{self.detection_method}' method...", "INFO")

    def cleanup(self):
        """Clean up resources when application is closing"""
        self._is_shutting_down = True
        self.stop_monitoring()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.running = False
            self.monitor_thread.join(timeout=1.0) 

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

    def _handle_file_change(self):
        """
        Callback triggered by MonitorThread when a change is detected.
        This function reads the file, calculates the diff, and shows the notification.
        """
        if not self.target_file or not self.detector:
            return
            
        try:
            # 1. Read the new content
            current_data = self.root.M_fileHandler.read_file_content(self.target_file)
            if not current_data:
                self.root.W_dashboard.main_log("Change detected but no data read", "ERROR")
                return

            # 2. Compare old data vs new data
            diff = list(dictdiffer.diff(self.previous_data, current_data))

            if diff:
                change_data = {
                    "filepath": self.target_file,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "diff": diff,
                }
                
                self.root.W_dashboard.main_log(f"Found {len(diff)} changes in {os.path.basename(self.target_file)}", "MODIFY")
                self.root.show_notification(change_data) 
                
                # 3. Update the 'previous' data state for the *next* comparison
                self.previous_data = current_data
            else:
                self.root.W_dashboard.main_log("Change detected, but no data diff found (e.g., whitespace change)", "INFO")

        except Exception as e:
            self.root.W_dashboard.main_log(f"Error processing changes: {e}", "ERROR")
        finally:
            # 4. CRITICAL: Update the detector's baseline.
            # This tells the detector that we have processed this change,
            # preventing an infinite loop of notifications.
            self.detector.update_baseline()