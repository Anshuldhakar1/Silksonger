import os
import threading
import hashlib
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Managers.AppManager import AppManager

class MonitorThread(threading.Thread):
    def __init__(self):
        pass

class Monitor():
    def __init__(self, app_manager: 'AppManager'):
        self.target_file: Optional[str] = None
        self.is_monitoring: bool = False
        self.app_manager = app_manager

    def set_target_file(self, filepath: str):
        self.target_file = filepath

    def release_target(self):
        self.target_file = None

    def start_monitoring(self):
        self.is_monitoring = True

    def stop_monitoring(self):
        self.is_monitoring = False