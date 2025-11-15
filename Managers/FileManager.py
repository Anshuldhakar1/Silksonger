import json
import os
import time
from Modules.error import BaseAppError
import traceback  # traceback.print_exc() pritns the stack trace
from typing import List, Dict, Callable
from Modules.SaveDecoder import decrypt_hollow_knight_save

class GamePathNotFoundError(BaseAppError):
    """Exception raised when the expected game directory is not found."""
    def __init__(self, msg: str):
        # 1. Define the friendly info
        dev_msg = msg
        user_msg = ("The game directory could not be found.\n"
                    "Please ensure the game is installed and "
                    "has been run at least once.")
        title = "Game Not Found"

        super().__init__(dev_message=dev_msg, user_message=user_msg, title=title, app_close=True)

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

    def file_selected(self, filepath: str) -> None:
        self.save_to_recents(filepath)
        self.create_file_slot(filepath)

    def save_to_recents(self, filepath: str) -> None:
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
    
    def create_file_slot(self, filepath: str) -> None:
        new_filename_normal = os.path.basename(filepath).replace(".dat",".json")
        new_filename_imp = os.path.basename(filepath).replace(".dat",".imp.json")

        path_norm = os.path.join(self.data_dir,"files",new_filename_normal)
        path_imp = os.path.join(self.data_dir,"files",new_filename_imp)

        if not os.path.isfile(path_norm):
            try:
                with open(path_norm,'w') as f:
                    json.dump({},f)
            except Exception as e:
                print(f"Exception occured while creating file slot: {e}")

        if not os.path.isfile(path_imp):
            try:
                with open(path_imp,'w') as f:
                    json.dump({},f)
            except Exception as e:
                print(f"Exception occured while creating file slot: {e}")

    def load_change_logs(self, filepath: str) -> List:
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

