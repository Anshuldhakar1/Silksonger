import os
import customtkinter as ctk
from typing import Optional, Dict
import traceback # traceback.print_exc() pritns the stack trace
# import dictdiffer  
from datetime import datetime  

from Managers.FileManager import FileManager
from Managers.AssetManager import AssetManager

from Windows.Dashboard import DashboardWindow
from Windows.Notification import NotificationWindow
from Windows.Change import ChangeWindow
from Windows.Error import ErrorWindow

from Modules.error import BaseAppError
from Modules.Monitor import Monitor
from Modules.types import ChangeDataType, ChangeNotesType
from Modules.DiffLogic import compute_save_diff

class AppManager(ctk.CTk):
    def __init__(self):
        
        super().__init__()

        self.changes: ChangeNotesType = {
            "normal": {},
            "important": {}
        }
        self.previous_data: Optional[Dict] = None
        self.selected_filepath: Optional[str] = None
        # self.notif_test:bool = False
        # self.was_not_monitoring: Optional[bool] = None

        self.resume_monitoring_on_close: bool = False

        self.DashboardWindow: Optional[DashboardWindow] = None
        self.NotificationWindow: Optional[NotificationWindow] = None
        self.ChangeWindow: Optional[ChangeWindow] = None
        self.ErrorWindow: Optional[ErrorWindow] = None

        self.Monitor: Optional[Monitor] = None

        self.begin()    # asset and file managers are instantiated inside this func

    def begin(self):
        self.AssetManager: AssetManager = AssetManager()
        try:
            self.FileManager: FileManager = FileManager()
        except BaseAppError as err:
            traceback.print_exc()  # prints stack trace
            self._error_popup(err)
        except Exception as e:
            # Catch unexpected init errors
            traceback.print_exc()
            self._error_popup(BaseAppError(str(e), "An unexpected error occurred during initialization.", app_close=True))

        self.title("Silksong Save Monitor")
        self.geometry("920x560")

        try:
            icon_path = self.AssetManager._path("assets/icons/tiny_hornet.ico")
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error setting window icon: {e}") # Log if icon fails to load

        self.Monitor = Monitor(self, change_callback=self.handle_change_detected)
        self.DashboardWindow = DashboardWindow(self)

        self.focus()

        # select user4.dat file
        # self.DashboardWindow.on_file_selected("C:/Users/anshu/AppData/LocalLow/Team Cherry/Hollow Knight Silksong/1156132065/user4.dat")
        # start monitoring
        # self.DashboardWindow.toggle_monitoring()

        # self.notifwindow_test()
        # self.change_test()
        # self.sidelogs_test()

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
        self.selected_filepath = filepath

        try:
            self.FileManager.file_selected(filepath)
            change_logs = self.FileManager.load_change_logs(filepath)
            self.previous_data = self.FileManager.load_save(
                filepath, 
                logger=self.DashboardWindow.main_log
            )

            self.changes["normal"] = change_logs[0]
            self.changes["important"] = change_logs[1]

        except BaseAppError as e:
            self._error_popup(e)
            # If initial load fails, we might want to reset selection or stop monitoring
            self.Monitor.release_target()
            self.selected_filepath = None
        except Exception as e:
            traceback.print_exc()
            self._error_popup(BaseAppError(str(e), "An unexpected error occurred while selecting the file."))

    def handle_change_detected(self):
        self.DashboardWindow.status_set_not_monitoring()
        
        try:
            current_data = self.FileManager.load_save(
                self.selected_filepath, 
                logger=self.DashboardWindow.main_log
            )
            
            # load_save now raises exceptions on failure, so if we get here, current_data is valid.
            
            diff = compute_save_diff(self.previous_data, current_data)

            if diff:
                change_data: ChangeDataType = {
                    "filepath": self.selected_filepath, 
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "diff": diff, 
                }
                
                self.DashboardWindow.main_log(f"Found {len(diff)} changes in {os.path.basename(self.selected_filepath)}", "MODIFY")
                self.show_notification(change_data) 
                self.previous_data = current_data
            else:
                self.DashboardWindow.main_log("Change detected, but no data diff found.", "INFO")
                # Even if no diff found, update baseline to prevent loops
                self.Monitor.force_update_baseline()
                
        except BaseAppError as e:
            # Catch known app errors
            self._error_popup(e)
            self.DashboardWindow.main_log(f"Error: {e.user_message}", "ERROR")
        except Exception as e:
            # Catch entirely unexpected errors
            traceback.print_exc()
            self.DashboardWindow.main_log(f"Unexpected Error: {e}", "ERROR")
            self._error_popup(BaseAppError(str(e), "An unexpected error occurred during change detection."))
        finally:
            # If we didn't start the notification window (which stops monitoring), 
            # we might want to ensure baseline is updated or status is reset?
            # If NotificationWindow opens, it handles logic. If not, we fall back here.
            self.Monitor.force_update_baseline()

    def show_notification(self, changeData: ChangeDataType):
        if self.NotificationWindow is None or not self.NotificationWindow.winfo_exists():
            
            self.resume_monitoring_on_close = self.Monitor.is_monitoring
            
            self.Monitor.stop_monitoring()

            self.NotificationWindow = NotificationWindow(
                self, 
                input_change_data = changeData,
                app_manager = self,
                # asset_manager = self.AssetManager,
                window_save_callback = self._on_notif_window_save,
                window_closed_callback = self._on_notif_window_closed
            )

    def show_change(self, note: str, is_imp:bool):
        if self.ChangeWindow is None or not self.ChangeWindow.winfo_exists():
            change : Optional[ChangeDataType] = None
            if not is_imp:
                change = self.changes.get("normal").get(note)
            else:
                change = self.changes.get("important").get(note)

            self.ChangeWindow = ChangeWindow(
                app_manager = self,
                note = note,
                change = change
            )

    def _on_notif_window_save(self, note: str, changes: ChangeDataType, imp: bool):
        try:
            self.FileManager.save_change(
                note= note,
                changes = changes,
                imp = imp   
            )

            if imp:
                self.changes["important"][note] = changes
                self.DashboardWindow.imp_btn_clicked()
            else:            
                self.changes["normal"][note] = changes
                self.DashboardWindow.logs_btn_clicked()

            msg: str = f"Saved {'important ' if imp else ''}change with note: \"{note}\""
            self.DashboardWindow.main_log(msg, "SAVED_IMP" if imp else "SAVED")

            if self.resume_monitoring_on_close:
                self.DashboardWindow.main_log(f"Started monitoring {os.path.basename(self.selected_filepath)}", "START")
                self.DashboardWindow.status_set_monitoring()
                self.Monitor.start_monitoring()
            else:
                self.DashboardWindow.status_set_not_monitoring()

        except BaseAppError as e:
            self._error_popup(e)

    def _on_notif_window_closed(self):
        self.DashboardWindow.main_log("Changes discarded/ignored.", "INFO")
        if self.resume_monitoring_on_close:
            self.DashboardWindow.main_log(f"Started monitoring {os.path.basename(self.selected_filepath)}", "START")
            self.DashboardWindow.status_set_monitoring()
            self.Monitor.start_monitoring()
        else:
            self.DashboardWindow.status_set_not_monitoring()

    def notifwindow_test(self):
        change_data: ChangeDataType = {
            'filepath': 'C:/Users/anshu/AppData/LocalLow/Team Cherry/Hollow Knight Silksong/1156132065/user4.dat', 
            'timestamp': '2025-11-18 16:04:22', 
            'diff': [
                ('change', 'playerData.LastSetFieldName', ('SeenMapperBoneForest', 'disableInventory')), 
                ('change', 'playerData.playTime', (2509.08423, 2554.81787)), 
                ('change', 'playerData.hazardRespawnFacing', (2,0)), 
                ('add', 'playerData.QuestCompletionData.savedData', [
                    (1,{'Name': 'Mossberry Collection Pre', 'Data': {
                            'HasBeenSeen': False, 
                            'IsAccepted': True, 
                            'CompletedCount': 0, 
                            'IsCompleted': True, 
                            'WasEverCompleted': True}
                        }), 
                    (2, {'Name': 'Mossberry Collection 1', 'Data': {
                        'HasBeenSeen': False, 
                        'IsAccepted': True, 
                        'CompletedCount': 0, 
                        'IsCompleted': False, 
                        'WasEverCompleted': False
                        }}
                    )]
                )
            ]
            }
        # self.notif_test = True
        self.show_notification(changeData = change_data)

    def change_test(self):
        self.withdraw()

        self.DashboardWindow.on_file_selected("C:/Users/anshu/AppData/LocalLow/Team Cherry/Hollow Knight Silksong/1156132065/user4.dat")

        note = "testing"
        is_imp = False
        self.show_change(note=note, is_imp=is_imp)

    def sidelogs_test(self):
        # self.DashboardWindow.add_log_entry(
        #     timestamp="2025-11-09 18:28:51",
        #     main_text="note",
        #     sub_text="5 changes detected"
        # )
        self.DashboardWindow.on_file_selected("C:/Users/anshu/AppData/LocalLow/Team Cherry/Hollow Knight Silksong/1156132065/user4.dat")

    def wrap_text( self, input: str, limit: int) -> str:
        limit = limit
        note_text = ""
        start = 0
        for _ in range(len(input) // limit + 1):
            if start >= len(input):
                break
            end = min((start+limit) , len(input))
            if end == len(input):
                note_text = note_text + input[start:end].strip() + "\n"
                start = end 
                continue
            while input[end] not in [" ","\n"]:
                end -= 1
            note_text = note_text + input[start:end].strip() + "\n"
            start = end
        note_text = note_text.rstrip("\n")

        return note_text



