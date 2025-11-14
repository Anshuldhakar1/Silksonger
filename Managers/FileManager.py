import json
import os
from Modules.error import BaseAppError

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

        with open(self.recent_files_path, 'w') as file:  # instantiates the recent_files file
            json.dump({}, file, indent=4)

