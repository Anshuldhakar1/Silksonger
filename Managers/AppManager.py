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
        self.notif_test:bool = False

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
        self.previous_data = self.FileManager.load_save(
            filepath, 
            logger=self.DashboardWindow.main_log
        )

        self.changes["normal"] = change_logs[0]
        self.changes["important"] = change_logs[1]

        self.selected_filepath = filepath

    def handle_change_detected(self):
        try:
            current_data = self.FileManager.load_save(
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
                self.show_notification(change_data) 
                # print(change_data)

                self.previous_data = current_data
            else:
                self.DashboardWindow.main_log("Change detected, but no data diff found (e.g., whitespace change)", "INFO")
        except Exception as e:
            self.DashboardWindow.main_log(f"Error processing changes: {e}", "ERROR")
        finally:
            # 4. CRITICAL: Update the detector's baseline.
            self.Monitor.force_update_baseline()

    def show_notification(self, changeData: ChangeDataType):
        if self.NotificaitonWindow is None or not self.NotificaitonWindow.winfo_exists():
            self.Monitor.stop_monitoring()

            self.NotificaitonWindow = NotificaitonWindow(
                self, 
                input_change_data = changeData,
                asset_manager = self.AssetManager,
                window_save_callback = self._on_notif_window_save,
                window_closed_callback = self._on_notif_window_closed
            )

    def _on_notif_window_save(self, note: str, changes: ChangeDataType, imp: bool):
        
        self.FileManager.save_change(
            note= note,
            changes = changes,
            imp = imp   
        )

        self.DashboardWindow.add_log_entry(
            timestamp=changes['timestamp'],
            main_text=note,
            sub_text=f"{len(changes['diff'])} changes detected"
        )

        # new_data = {
        #     "filepath": changes['filepath'],
        #     "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        #     "diff": changes['diff'],
        # }

        msg = f"Saved change with note: \"{note}\""
        if imp:
            msg = f"Saved important change with note: \"{note}\""
        self.DashboardWindow.main_log( msg, "SAVED" if not imp else "SAVED_IMP")
        self.DashboardWindow.main_log("Waiting for changes...", "INFO")

        self.Monitor.start_monitoring()

    def _on_notif_window_closed(self):
        self.DashboardWindow.main_log("Waiting for changes...", "INFO")
        if not self.notif_test:
            self.Monitor.start_monitoring()

    def notifwindow_test(self):
        change_data: ChangeDataType = {'filepath': 'C:/Users/anshu/AppData/LocalLow/Team Cherry/Hollow Knight Silksong/1156132065/user4.dat', 'timestamp': '2025-11-15 12:36:45', 'diff': [('change', 'playerData.date', ('2025-11-14', '2025-11-15')), ('change', 'playerData.playTime', (1117.3844, 1173.99)), ('change', 'playerData.mapperAway', (False, True)), ('change', 'playerData.pilgrimRestCrowd', (5, 1)), ('change', 'playerData.pilgrimGroupBonegrave', (1, 2)), ('change', 'playerData.pilgrimGroupShellgrave', (1, 2)), ('change', 'playerData.pilgrimGroupGreymoorField', (3, 1)), ('change', 'playerData.enemyGroupAnt04', (2, 1)), ('change', 'playerData.halfwayCrowd', (1, 4)), ('change', 'playerData.FisherWalkerTimer', (-0.007603127, 37.72893)), ('change', 'playerData.FisherWalkerDirection', (True, False)), ('change', 'playerData.FisherWalkerIdleTimeLeft', (32.3923225, -0.007298246))]}
        # self.notif_test = True
        self.show_notification(changeData = change_data)

    def sidelogs_test(self):
        self.DashboardWindow.add_log_entry(
            timestamp="2025-11-09 18:28:51",
            main_text="note",
            sub_text="5 changes detected"
        )

    #     self.FileManager.save_change(
    #         note= "note",
    #         changes = {
    #     "filepath": "C:/Users/anshu/AppData/LocalLow/Team Cherry/Hollow Knight Silksong/1156132065/user4.dat",
    #     "timestamp": "2025-11-09 18:28:51",
    #     "diff": [
    #         [
    #             "change",
    #             "playerData.playTime",
    #             [
    #                 5306.734,
    #                 5452.45264
    #             ]
    #         ],
    #         [
    #             "change",
    #             "playerData.pilgrimRestCrowd",
    #             [
    #                 1,
    #                 4
    #             ]
    #         ],
    #         [
    #             "change",
    #             "playerData.pilgrimGroupBonegrave",
    #             [
    #                 3,
    #                 1
    #             ]
    #         ],
    #         [
    #             "change",
    #             "playerData.pilgrimGroupShellgrave",
    #             [
    #                 1,
    #                 2
    #             ]
    #         ],
    #         [
    #             "change",
    #             "playerData.pilgrimGroupGreymoorField",
    #             [
    #                 3,
    #                 2
    #             ]
    #         ],
    #         [
    #             "change",
    #             "playerData.enemyGroupAnt04",
    #             [
    #                 2,
    #                 3
    #             ]
    #         ],
    #         [
    #             "change",
    #             "playerData.halfwayCrowEnemyGroup",
    #             [
    #                 2,
    #                 1
    #             ]
    #         ],
    #         [
    #             "change",
    #             "playerData.FisherWalkerTimer",
    #             [
    #                 63.0351753,
    #                 21.4648724
    #             ]
    #         ],
    #         [
    #             "change",
    #             "playerData.FisherWalkerDirection",
    #             [
    #                 True,
    #                 False
    #             ]
    #         ],
    #         [
    #             "change",
    #             "playerData.FisherWalkerIdleTimeLeft",
    #             [
    #                 -0.06382179,
    #                 -0.005471822
    #             ]
    #         ]
    #     ]
    # },
    #         imp = False  
    #     )


