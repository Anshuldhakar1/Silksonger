import customtkinter as ctk
from typing import Optional
import traceback  # traceback.print_exc() pritns the stack trace
import sys

from Managers.FileManager import FileManager, GamePathNotFoundError

from Managers.AssetManager import AssetManager
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
        try:
            self.FileManager: FileManager = FileManager()
        except GamePathNotFoundError as err:
            traceback.print_exc()  # prints stack trace
            print("\n"+err)

        self.title("File Monitor")
        self.geometry("920x560")

        self.AssetManager: AssetManager = AssetManager()
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