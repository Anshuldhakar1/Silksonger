import customtkinter as ctk
from typing import Optional
import traceback  # traceback.print_exc() pritns the stack trace
import sys

from Managers.FileManager import FileManager, GamePathNotFoundError
from Managers.AssetManager import AssetManager

from Windows.Dashboard import DashboardWindow
from Windows.Notification import NotificaitonWindow
from Windows.Change import ChangeWindow
from Windows.Error import ErrorWindow

from Modules.error import BaseAppError

class AppManager(ctk.CTk):
    def __init__(self):
        
        super().__init__()

        self.changes = {  # raw changes?
            "normal": {},
            "important": {},
        }
        self.is_file_selected = False

        self.DashboardWindow: Optional[DashboardWindow] = None
        self.NotificaitonWindow: Optional[NotificaitonWindow] = None
        self.ChangeWindow: Optional[ChangeWindow] = None
        self.ErrorWindow: Optional[ErrorWindow] = None

        self.begin()    # asset and file managers are instantiated inside this func

    def begin(self):

        self.AssetManager: AssetManager = AssetManager()

        try:
            self.FileManager: FileManager = FileManager()
        except GamePathNotFoundError as err:
            traceback.print_exc()  # prints stack trace
            self._error_popup(err)

        self.title("File Monitor")
        self.geometry("920x560")
        self.DashboardWindow = DashboardWindow(self)

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

    def _error_popup(self, error: BaseAppError):
        if self.ErrorWindow is None or not self.ErrorWindow.winfo_exists():
            self.ErrorWindow = ErrorWindow(
                self, 
                error=error, 
                asset_manager=self.AssetManager,
            )

    def file_selected(self, filepath: str):
        change_logs = self.FileManager.load_change_logs(filepath)

        self.changes["normal"] = change_logs[0]
        self.changes["important"] = change_logs[1]

        self.is_file_selected = True