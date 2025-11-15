import os
import customtkinter as ctk
from typing import Optional, Dict
import traceback # traceback.print_exc() pritns the stack trace
import dictdiffer  
from datetime import datetime  

from Managers.FileManager import FileManager, GamePathNotFoundError
from Managers.AssetManager import AssetManager

from Windows.Dashboard import DashboardWindow
from Windows.Notification import NotificaitonWindow
from Windows.Change import ChangeWindow
from Windows.Error import ErrorWindow

from Modules.error import BaseAppError
from Modules.Monitor import Monitor
from Modules.types import ChangeDataType, ChangeNotesType

class AppManager(ctk.CTk):
    def __init__(self):
        
        super().__init__()

        self.changes: ChangeNotesType = {
            "normal": {},
            "important": {}
        }
        self.previous_data: Optional[Dict] = None
        self.selected_filepath: Optional[str] = None

        self.DashboardWindow: Optional[DashboardWindow] = None
        self.NotificaitonWindow: Optional[NotificaitonWindow] = None
        self.ChangeWindow: Optional[ChangeWindow] = None
        self.ErrorWindow: Optional[ErrorWindow] = None

        self.Monitor: Optional[Monitor] = None

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

        self.Monitor = Monitor(self, change_callback=self.handle_change_detected)
        self.DashboardWindow = DashboardWindow(self)

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        # Log shutdown
        if self.DashboardWindow:
            self.DashboardWindow.main_log("Application shutting down...", "INFO")
        
        # # Cleanup background tasks
        if self.Monitor:
            self.Monitor.cleanup()
        
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
        self.Monitor.set_target_file(filepath)

        change_logs = self.FileManager.load_change_logs(filepath)
        self.previous_data = self.FileManager.read_save(
            filepath, 
            logger=self.DashboardWindow.main_log
        )

        self.changes["normal"] = change_logs[0]
        self.changes["important"] = change_logs[1]

        self.selected_filepath = filepath

    def handle_change_detected(self):
        try:
            current_data = self.FileManager.read_save(
                self.selected_filepath, 
                logger=self.DashboardWindow.main_log
            )

            if not current_data:
                self.DashboardWindow.main_log("Something went wrong reading the current save","ERROR")
                return
            
            diff = list(dictdiffer.diff(self.previous_data, current_data))

            if diff:
                change_data: ChangeDataType = {
                    "filepath": self.selected_filepath, # this is str
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # this is str
                    "diff": diff, # this is list
                }
                
                self.DashboardWindow.main_log(f"Found {len(diff)} changes in {os.path.basename(self.selected_filepath)}", "MODIFY")
                # self.show_notification(change_data) 
                print(change_data)

                self.previous_data = current_data
            else:
                self.DashboardWindow.main_log("Change detected, but no data diff found (e.g., whitespace change)", "INFO")
        except Exception as e:
            self.DashboardWindow.main_log(f"Error processing changes: {e}", "ERROR")
        finally:
            # 4. CRITICAL: Update the detector's baseline.
            self.Monitor.force_update_baseline()

    def show_notificaiton(self, changeData: ChangeDataType):
        if self.NotificaitonWindow is None or not self.NotificaitonWindow.winfo_exists():
            self.NotificaitonWindow = NotificaitonWindow(self, input_change_data = changeData)
