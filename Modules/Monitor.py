import os
import threading
import hashlib
from typing import TYPE_CHECKING, Optional, Callable

if TYPE_CHECKING:
    from Managers.AppManager import AppManager

def calculate_partial_hash(filepath: str, chunk_size: int = 4096) -> Optional[str]:
    """Calculates the SHA-256 hash of the first 'chunk_size' bytes of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            byte_block = f.read(chunk_size)
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (PermissionError, OSError, FileNotFoundError):
        return None

class MonitorThread(threading.Thread):
    def __init__(self, target_file: str, callback: Callable, logger: Callable, app_manager, polling_interval: float = 1.0):
        super().__init__(daemon=True)  # Set as daemon thread
        self.callback = callback
        self.POLLING_INTERVAL = polling_interval
        self.target_file = target_file
        self.chunk_size = 4096
        self.logger = logger
        self.app_manager = app_manager  # Need this to schedule GUI updates

        self.last_mtime: float = 0.0
        self.last_partial_hash: Optional[str] = None

        # Use a single Event for stop control
        self._stop_event = threading.Event()

    def _log_safe(self, message: str, tag: str = None):
        if self.app_manager:
            self.app_manager.after(0, lambda: self.logger(message, tag))
        else:
            print(f"[MONITOR] {tag}: {message}")

    def _get_mtime(self) -> float:
        try:
            return os.path.getmtime(self.target_file)
        except (FileNotFoundError, PermissionError):
            return 0.0

    def stop(self):
        self._stop_event.set()

    def run(self):
        
        while not os.path.exists(self.target_file):
            if self._stop_event.is_set(): 
                self._log_safe("MonitorThread Stopped while waiting for file.", "INFO")
                return
            self._log_safe(f"MonitorThread Waiting for file: {self.target_file}...", "INFO")
            self._stop_event.wait(self.POLLING_INTERVAL)

        try:
            self.update_baseline()
        except Exception as e:
            self._log_safe(f"Error setting initial baseline: {e}", "ERROR")
            return 

        while not self._stop_event.is_set():
            try:
                if self.has_changed():
                    self._log_safe(f"MonitorThread Change detected in {self.target_file}", "INFO")
                    self.update_baseline() 
                    self.callback()

                self._stop_event.wait(self.POLLING_INTERVAL)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                self._log_safe(f"Error in MonitorThread loop: {e}", "ERROR")
                self._stop_event.wait(self.POLLING_INTERVAL)
        
        try:
            self._log_safe("MonitorThread Stopped.", "INFO")
        except Exception as e:
            import traceback
            traceback.print_exc()
            
    def has_changed(self) -> bool:
        current_mtime = self._get_mtime()

        # Fast check: If mtime changed, file likely changed
        if current_mtime != self.last_mtime:
            return True
        
        # Fallback: Check partial hash in case mtime strategy fails
        # (some systems/filesystems may not update mtime reliably)
        current_partial_hash = calculate_partial_hash(self.target_file, self.chunk_size)
        
        if current_partial_hash is None:
            return False  # Can't read file, don't report as change
            
        return current_partial_hash != self.last_partial_hash

    def update_baseline(self):
        self.last_mtime = self._get_mtime()
        self.last_partial_hash = calculate_partial_hash(self.target_file, self.chunk_size)

class Monitor:
    def __init__(self, app_manager: 'AppManager', change_callback: Callable):
        self.target_file: Optional[str] = None
        self.is_monitoring: bool = False
        self.app_manager = app_manager
        self.ui_change_callback = change_callback
        
        self.monitor_thread: Optional[MonitorThread] = None
        self.POLLING_INTERVAL = 1.0  

    def _on_change_detected_from_thread(self):
        if self.app_manager:
            # Schedule self.ui_change_callback (which is AppManager.handle_change_detected)
            # to run on the main thread.
            self.app_manager.after(0, self.ui_change_callback)

    def set_target_file(self, filepath: str):
        if self.is_monitoring:
            return
        self.target_file = filepath

    def release_target(self):
        if self.is_monitoring:
            return
        self.target_file = None

    def force_update_baseline(self):
        if self.monitor_thread is not None:
            self.monitor_thread.update_baseline()

    def start_monitoring(self):
        if self.is_monitoring:
            return

        if self.target_file is None:
            self.app_manager.DashboardWindow.main_log("Monitor Error: No target file set. Call set_target_file() first.","ERROR")
            return
        
        self.monitor_thread = MonitorThread(
            logger = self.app_manager.DashboardWindow.main_log,
            target_file=self.target_file,
            callback=self._on_change_detected_from_thread,
            app_manager=self.app_manager,  # Pass app_manager for safe logging
            polling_interval=self.POLLING_INTERVAL
        )
        self.monitor_thread.start()
        self.is_monitoring = True

    def stop_monitoring(self):
        if not self.is_monitoring or self.monitor_thread is None:
            return

        self.monitor_thread.stop()
        self.monitor_thread.join(timeout=2.0)  # Add timeout to prevent hanging
        
        self.monitor_thread = None
        self.is_monitoring = False

    def cleanup(self):
        if self.monitor_thread is None:
            return
        self.stop_monitoring()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.running = False
            self.monitor_thread.join(timeout=1.0) 