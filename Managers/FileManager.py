import json
import os

class GamePathNotFoundError(Exception):
    """Exception raised when the expected game directory is not found."""
    pass

class FileManager():
    def __init__(self):

        self.target_directory = os.path.join(
            os.path.expanduser("~"), 
            "AppData", 
            "LocalLow", 
            "Team Cherry", 
            "Hollow Knight Silksong"
        )

        if os.path.exists(self.target_directory):
        # if not os.path.exists(self.target_directory):
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

