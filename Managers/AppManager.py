import os
import customtkinter as ctk
from typing import Optional, Dict
import traceback # traceback.print_exc() pritns the stack trace
import dictdiffer  
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
        self.was_not_monitoring: Optional[bool] = None

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

    # def handle_change_detected(self):
    #     self.DashboardWindow.status_set_not_monitoring()
    #     try:
    #         current_data = self.FileManager.load_save(
    #             self.selected_filepath, 
    #             logger=self.DashboardWindow.main_log
    #         )

    #         if not current_data:
    #             self.DashboardWindow.main_log("Something went wrong reading the current save","ERROR")
    #             return
            
    #         diff = list(dictdiffer.diff(self.previous_data, current_data))

    #         if diff:
    #             change_data: ChangeDataType = {
    #                 "filepath": self.selected_filepath, # this is str
    #                 "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # this is str
    #                 "diff": diff, # this is list
    #             }
                
    #             self.DashboardWindow.main_log(f"Found {len(diff)} changes in {os.path.basename(self.selected_filepath)}", "MODIFY")
    #             self.show_notification(change_data) 
    #             # print("\nChange Data:")
    #             # print(change_data)

    #             self.previous_data = current_data
    #         else:
    #             self.DashboardWindow.main_log("Change detected, but no data diff found (e.g., whitespace change)", "INFO")
    #     except Exception as e:
    #         self.DashboardWindow.main_log(f"Error processing changes: {e}", "ERROR")
    #         traceback.print_exec()
    #     finally:
    #         # 4. CRITICAL: Update the detector's baseline.
    #         self.Monitor.force_update_baseline()

    def handle_change_detected(self):
        # Pause monitoring updates while processing
        self.DashboardWindow.status_set_not_monitoring()
        
        try:
            current_data = self.FileManager.load_save(
                self.selected_filepath, 
                logger=self.DashboardWindow.main_log
            )
            
            # load_save now raises exceptions on failure, so if we get here, current_data is valid.
            
            diff = list(dictdiffer.diff(self.previous_data, current_data))

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
        if not self.notif_test and self.was_not_monitoring is not None:

            self.DashboardWindow.main_log("Changes discarded/ignored.", "INFO")
            # CHECK FLAG: Only resume if we were running before
            if self.resume_monitoring_on_close:
                self.DashboardWindow.main_log("Resuming monitoring...", "INFO")
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

#  testing raw cahnges from notificaiton window

# {'filepath': 'C:/Users/anshu/AppData/LocalLow/Team Cherry/Hollow Knight Silksong/1156132065/user4.dat', 'timestamp': '2025-11-18 16:00:35', 'diff': [('change', 'playerData.playTime', (2173.38037, 2466.70386)), ('change', 'playerData.geo', (0, 182)), ('change', 'playerData.silk', (0, 9)), ('change', 'playerData.atBench', (True, False)), ('change', 'playerData.respawnScene', ('Bonetown', 'Mosstown_02')), ('change', 'playerData.mapZone', (12, 19)), ('change', 'playerData.respawnMarkerName', ('RestBench', 'Death Respawn Marker')), ('change', 'playerData.respawnType', (1, 0)), ('change', 'playerData.hazardRespawnFacing', (1, 0)), ('change', 'playerData.HeroCorpseScene', ('Mosstown_01', '')), 
# ('change', 'playerData.HeroCorpseMoneyPool', (48, 0)), ('change', 'playerData.hasSilkSpecial', (False, True)), ('change', 'playerData.hasNeedleThrow', (False, True)), ('change', ['playerData', 'EnemyJournalKillData', 'list', 4, 'Record', 'Kills'], (3, 7)), ('change', ['playerData', 'EnemyJournalKillData', 'list', 5, 'Record', 'Kills'], (1, 2)), ('change', ['playerData', 'EnemyJournalKillData', 'list', 6, 'Record', 'Kills'], (1, 4)), ('change', ['playerData', 'EnemyJournalKillData', 'list', 7, 'Record', 'Kills'], (1, 2)), ('add', 'playerData.EnemyJournalKillData.list', [(8, 
# {'Name': 'Bone Flyer', 'Record': {'Kills': 1, 'HasBeenSeen': False}}), (9, {'Name': 'Pilgrim 03', 'Record': {'Kills': 4, 'HasBeenSeen': False}}), (10, {'Name': 'Aspid Collector', 'Record': {'Kills': 1, 'HasBeenSeen': False}})]), ('change', 'playerData.currentArea', ('BONEBOTTOM', 'MOSSTOWN')), ('add', 'playerData.scenesVisited', [(11, 'Bone_01c'), (12, 'Bone_01c_top'), (13, 'Mosstown_02')]), ('change', 'playerData.environmentType', (0, 6)), ('change', 'playerData.mosstown01_shortcut', (False, True)), ('change', 'playerData.FisherWalkerTimer', (68.51077, 68.51352)), ('change', 'playerData.FisherWalkerIdleTimeLeft', (31.6293373, 72.16206)), ('change', 'playerData.completionPercentage', (0.0, 1.0)), ('change', 'playerData.ToolPaneHasNew', (False, True)), ('add', ['playerData', 'ToolEquips', 'savedData', 
# 0, 'Data'], [('Slots', [{'EquippedTool': '', 'IsUnlocked': False}, {'EquippedTool': '', 'IsUnlocked': False}, {'EquippedTool': '', 'IsUnlocked': False}, {'EquippedTool': 'Silk Spear', 'IsUnlocked': False}, {'EquippedTool': '', 'IsUnlocked': False}, {'EquippedTool': '', 'IsUnlocked': False}, {'EquippedTool': '', 'IsUnlocked': False}])]), ('change', 'playerData.ShellShards', (93, 139)), ('remove', 'playerData', [('HeroCorpseMarkerGuid', '9hdmALwmB0+MNBDU/nJnwQ==')]), ('change', ['sceneData', 'persistentBools', 'serializedList', 43, 'Value'], (False, True)), ('change', ['sceneData', 'persistentBools', 'serializedList', 69, 'Value'], (False, True)), ('change', ['sceneData', 'persistentBools', 'serializedList', 70, 'Value'], (False, True)), ('add', 'sceneData.persistentBools.serializedList', [(71, {'SceneName': 'Bone_01c', 'ID': 'Inverse Remasker', 'Value': False, 'Mutator': 0}), (72, {'SceneName': 'Bone_01c', 'ID': 'Inverse Remasker (1)', 'Value': True, 'Mutator': 0}), (73, {'SceneName': 'Bone_01c', 'ID': 'bell_toll_machine', 'Value': False, 'Mutator': 0}), (74, {'SceneName': 'Bone_01c', 'ID': 'Geo Med Persistent', 'Value': False, 'Mutator': 0}), (75, {'SceneName': 'Bone_01c', 'ID': 'Geo Small Persistent (2)', 'Value': False, 'Mutator': 0}), (76, {'SceneName': 'Bone_01c', 'ID': 'Geo Small Persistent (1)', 'Value': False, 'Mutator': 0}), (77, {'SceneName': 'Mosstown_02', 'ID': 'Breakable Wall', 'Value': False, 'Mutator': 0}), (78, {'SceneName': 'Mosstown_02', 'ID': 'Vine Platform', 'Value': False, 'Mutator': 0}), (79, {'SceneName': 'Mosstown_02', 'ID': 'moss_bone_plaque', 'Value': False, 'Mutator': 0}), (80, {'SceneName': 'Mosstown_02', 'ID': 'Collectable Item Pickup', 'Value': False, 'Mutator': 0}), (81, {'SceneName': 'Mosstown_02', 'ID': 'Remasker New Sharp', 'Value': False, 'Mutator': 0}), (82, {'SceneName': 'Mosstown_02', 'ID': 'Silkfly Ambient (2)', 'Value': True, 'Mutator': 0}), (83, {'SceneName': 'Mosstown_02', 'ID': 'Silkfly Ambient (1)', 'Value': True, 'Mutator': 0}), (84, {'SceneName': 'Mosstown_02', 'ID': 'Silkfly Ambient', 'Value': True, 'Mutator': 0}), (85, {'SceneName': 'Mosstown_02', 'ID': 'Thick Silk Vines', 'Value': False, 'Mutator': 0}), (86, {'SceneName': 'Mosstown_02', 'ID': 'Thick Silk Vines (1)', 'Value': False, 'Mutator': 0}), (87, {'SceneName': 'Mosstown_02', 'ID': 'Reminder Silk Skill (1)', 'Value': False, 'Mutator': 0}), (88, {'SceneName': 'Mosstown_02', 'ID': 'Reminder Silk Skill', 'Value': False, 'Mutator': 0})]), ('change', ['sceneData', 'persistentInts', 'serializedList', 20, 'Value'], (-1, 2)), ('change', ['sceneData', 'persistentInts', 'serializedList', 21, 'Value'], (-1, 2)), ('add', 'sceneData.persistentInts.serializedList', [(22, {'SceneName': 'Bone_01c', 'ID': 'rosary_string_small_half (1)', 'Value': -1, 'Mutator': 0}), (23, {'SceneName': 'Bone_01c', 'ID': 'rosary_string_medium', 'Value': -1, 'Mutator': 0}), (24, {'SceneName': 'Mosstown_02', 'ID': 'rosary_string_small', 'Value': 3, 'Mutator': 0}), (25, {'SceneName': 'Mosstown_02', 
# 'ID': 'rosary_string_small_half', 'Value': 2, 'Mutator': 0})]), ('add', 'sceneData.geoRocks.serializedList', [(1, {'SceneName': 'Bone_01c', 'ID': 'Geo Rock 3', 'Value': 0, 'Mutator': 0}), (2, {'SceneName': 'Bone_01c', 'ID': 'Geo Rock 1 (1)', 'Value': 0, 'Mutator': 0})])]}

# testing change_data

# {'filepath': 'C:/Users/anshu/AppData/LocalLow/Team Cherry/Hollow Knight Silksong/1156132065/user4.dat', 'timestamp': '2025-11-18 16:04:22', 'diff': [('change', 'playerData.LastSetFieldName', ('SeenMapperBoneForest', 'disableInventory')), ('change', 'playerData.playTime', (2509.08423, 2554.81787)), ('change', 'playerData.hazardRespawnFacing', (2, 
# 0)), ('change', 'playerData.mapperAway', (True, False)), ('change', 'playerData.metDruid', (False, True)), ('change', 'playerData.pilgrimRestCrowd', (4, 3)), ('change', 'playerData.pilgrimGroupBonegrave', (3, 2)), ('change', 'playerData.pilgrimGroupGreymoorField', (2, 1)), ('change', 'playerData.halfwayCrowd', (4, 3)), ('change', 'playerData.halfwayCrowEnemyGroup', (2, 1)), ('change', 'playerData.FisherWalkerTimer', (68.51352, 52.91661)), ('change', 'playerData.FisherWalkerDirection', (False, True)), ('change', 'playerData.FisherWalkerIdleTimeLeft', (30.1708431, -0.0125436988)), ('change', 'playerData.promisedFirstWish', (False, True)), ('add', 'playerData.QuestCompletionData.savedData', [(1, {'Name': 'Mossberry Collection Pre', 'Data': {'HasBeenSeen': False, 'IsAccepted': True, 'CompletedCount': 0, 'IsCompleted': True, 'WasEverCompleted': True}}), (2, {'Name': 'Mossberry Collection 1', 'Data': {'HasBeenSeen': False, 'IsAccepted': True, 'CompletedCount': 0, 'IsCompleted': False, 'WasEverCompleted': False}})])]}



