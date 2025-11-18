import json
import os
import time
from Modules.error import GamePathNotFoundError
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
            traceback.print_exc()
            print(e)

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

        if not os.path.isfile(self.path_norm):
            try:
                with open(self.path_norm,'w') as f:
                    json.dump({},f)
            except Exception as e:
                print(f"Exception occured while creating file slot: {e}")

        if not os.path.isfile(self.path_imp):
            try:
                with open(self.path_imp,'w') as f:
                    json.dump({},f)
            except Exception as e:
                print(f"Exception occured while creating file slot: {e}")

    def load_change_logs(self, filepath: str) -> List[ChangeNotesType]:
        filename = os.path.basename(filepath)

        normal_changes_path = os.path.join(self.saves_dir, filename.replace(".dat",".json"))
        imp_changes_path = os.path.join(self.saves_dir, filename.replace(".dat",".imp.json"))

        logs=[]

        with open(normal_changes_path,'r') as file:
            logs.append(
                json.load(file)
            )
        with open(imp_changes_path,'r') as file:
            logs.append(
                json.load(file)
            )

        return logs

    def load_save(self, filepath: str, logger: Callable) -> Dict:
        max_retries = 5
        retry_delay = 0.2

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
                # File is locked, retry after delay
                time.sleep(retry_delay)
            except Exception as e:
                logger(f"Error reading file: {e}", "ERROR")
                time.sleep(retry_delay)

        logger("Failed to read file after multiple retries", "ERROR")
        return {}

    def save_change(self, note: str, changes: ChangeDataType, imp: bool):
        try:
            data = {}
            if not imp:
                if os.path.isfile(self.path_norm) and os.path.getsize(self.path_norm) > 0:
                    with open(self.path_norm, 'r') as file:
                        data = json.load(file)
                    
                    data[note] = changes
                    with open(self.path_norm, 'w') as file:
                        json.dump(data, file, indent=4)
                    return
            else:
                if os.path.isfile(self.path_imp) and os.path.getsize(self.path_imp) > 0:
                    with open(self.path_imp, 'r') as file:
                        data = json.load(file)
                    
                    data[note] = changes
                    with open(self.path_imp, 'w') as file:
                        json.dump(data, file, indent=4)
                    return
        except Exception as e:
            print(f"Error adding a new change. {e}")

