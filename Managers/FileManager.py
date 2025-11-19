import json
import os
import time
from Modules.error import FileOperationError, GamePathNotFoundError, SaveFileError
import traceback  # traceback.print_exc() pritns the stack trace
from typing import List, Dict, Callable
from Modules.SaveDecoder import decrypt_hollow_knight_save
from Modules.types import ChangeNotesType, ChangeDataType


class FileManager():
    def __init__(self):

        self.target_directory = os.path.join(
            os.path.expanduser("~"), 
            "AppData", 
            "LocalLow", 
            "Team Cherry", 
            "Hollow Knight Silksong"
        )

        if not os.path.exists(self.target_directory):
            raise GamePathNotFoundError(
                f"Game path not found. The directory does not exist:\n{self.target_directory}"
            )

        self.data_dir = ".trackerdata"
        self.saves_dir = os.path.join(self.data_dir, "files")

        os.makedirs(self.data_dir, exist_ok=True)  # creates data_dir
        os.makedirs(self.saves_dir, exist_ok=True)  # creates saves_dir

        self.recent_files_path = os.path.join(self.data_dir, "recent_files.json")

        if not os.path.exists(self.recent_files_path):
            with open(self.recent_files_path, 'w') as file:  # instantiates the recent_files file
                json.dump([], file, indent=4)

    def file_selected(self, filepath: str):
        self.save_to_recents(filepath)
        self.create_file_slot(filepath)

    def save_to_recents(self, filepath: str):
        try:
            recent_files = []
            with open(self.recent_files_path, 'r') as file:
                recent_files = json.load(file)

            if filepath in recent_files:
                recent_files.remove(filepath)

            recent_files.insert(0, filepath)
            recent_files = recent_files[:3]

            with open(self.recent_files_path, 'w') as file:
                json.dump(recent_files, file, indent=4)
        except Exception as e:
            # Wrap general IO errors
            raise FileOperationError(f"Failed to save recent files: {e}", context="History Update")

    def get_recent_files(self) -> List:
        try:
            with open(self.recent_files_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            return []
    
    def create_file_slot(self, filepath: str):
        new_filename_normal = os.path.basename(filepath).replace(".dat",".json")
        new_filename_imp = os.path.basename(filepath).replace(".dat",".imp.json")

        self.path_norm = os.path.join(self.data_dir,"files",new_filename_normal)
        self.path_imp = os.path.join(self.data_dir,"files",new_filename_imp)

        try:
            if not os.path.isfile(self.path_norm):
                with open(self.path_norm,'w') as f:
                    json.dump({},f)
            if not os.path.isfile(self.path_imp):
                with open(self.path_imp,'w') as f:
                    json.dump({},f)
        except Exception as e:
            raise FileOperationError(f"Failed to create change logs slots: {e}", context="File Slot Creation")

    def load_change_logs(self, filepath: str) -> List[ChangeNotesType]:
        filename = os.path.basename(filepath)

        normal_changes_path = os.path.join(self.saves_dir, filename.replace(".dat",".json"))
        imp_changes_path = os.path.join(self.saves_dir, filename.replace(".dat",".imp.json"))

        logs=[]

        try:
            with open(normal_changes_path,'r') as file:
                logs.append(
                    json.load(file)
                )
            with open(imp_changes_path,'r') as file:
                logs.append(
                    json.load(file)
                )
        except Exception as e:
            raise FileOperationError(f"Failed to load existing change logs: {e}", context="Loading Logs")

        return logs

    def load_save(self, filepath: str, logger: Callable) -> Dict:
        max_retries = 5
        retry_delay = 0.2
        last_error = None

        for attempt in range(max_retries):
            try:
                with open(filepath, 'rb') as f:
                    encrypted_data = f.read()
                
                if not encrypted_data:
                    logger(f"File is empty, retrying... ({attempt+1}/{max_retries})", "ERROR")
                    time.sleep(retry_delay)
                    continue

                decrypted_json = decrypt_hollow_knight_save(encrypted_data)
                return json.loads(decrypted_json)

            except (PermissionError, OSError):
                # File is locked, retry
                time.sleep(retry_delay)
            except SaveFileError as e:
                # If decryption fails, we usually don't retry unless we suspect a partial write
                # For now, we let it bubble up immediately or retry if you prefer.
                # Let's assume a corrupted file implies we stop immediately.
                raise e 
            except Exception as e:
                last_error = e
                logger(f"Error reading file: {e}", "ERROR")
                time.sleep(retry_delay)

        # If we exit the loop, we failed. Raise a custom error.
        raise FileOperationError(f"Failed to read save file after retries. Last error: {last_error}", context="Load Save")

    def save_change(self, note: str, changes: ChangeDataType, imp: bool):
        try:
            data = {}
            target_path = self.path_imp if imp else self.path_norm

            if os.path.isfile(target_path) and os.path.getsize(target_path) > 0:
                with open(target_path, 'r') as file:
                    data = json.load(file)
            
            data[note] = changes
            with open(target_path, 'w') as file:
                json.dump(data, file, indent=4)
                
        except Exception as e:
             raise FileOperationError(f"Failed to save change log: {e}", context="Save Change Log")

