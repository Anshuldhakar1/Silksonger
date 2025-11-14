import customtkinter as ctk
from typing import Optional, Literal

from Managers.AssetManager import AssetManager
from Managers.FileManager import FileManager
from Windows.Dashboard import DashboardWindow
from Windows.Notification import NotificaitonWindow
from Windows.Change import ChangeWindow

class AppManager(ctk.CTk):
    def __init__(self):
        
        super().__init__()

        self.changes = {  # raw changes?
            "normal": {},
            "important": {},
        }

        self.DashboardWindow: Optional[DashboardWindow] = None
        self.NotificaitonWindow: Optional[NotificaitonWindow] = None
        self.ChangeWindow: Optional[ChangeWindow] = None

        self.begin()    # asset and file managers are instantiated inside this func

    def begin(self):
        self.title("File Monitor")
        self.geometry("920x560")

        self.AssetManager: AssetManager = AssetManager()
        self.FileManager: FileManager = FileManager()

        self.DashboardWindow = DashboardWindow()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        # Log shutdown
        # if self.W_dashboard:
        #     self.W_dashboard.main_log("Application shutting down...", "INFO")
        
        # # Cleanup background tasks
        # if self.M_monitor:
        #     self.M_monitor.cleanup()
        
        # Close window
        self.quit()
        self.destroy()