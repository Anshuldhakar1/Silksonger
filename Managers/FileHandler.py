import os
from tkinter import filedialog
from Managers.JsonManager import JsonManager

class FileHandler():
    def __init__(self):
        base_path = os.path.join(os.path.expanduser("~"), "AppData", "LocalLow", "Team Cherry")
        silksong_path = os.path.join(base_path, "Hollow Knight Silksong", "1156132065")

        self.target_directory = os.path.expanduser("~")
        if os.path.exists(silksong_path):
            self.target_directory = silksong_path
        elif os.path.exists(base_path):
            self.target_directory = base_path

        self.file_selected_callback = None

        self.data_dir = ".trackerdata"
        self.recent_files_path = os.path.join(self.data_dir, "recent_files.json")
        self.saved_notes_path = os.path.join(self.data_dir, "saved.json")
        self.imp_path = os.path.join(self.data_dir, "star_changes.json")

    def set_callback(self, callback):
        self.file_selected_callback = callback

    def save_to_recents(self, filepath):
        try:
            # Load existing recents or create empty list
            recent_files = JsonManager.load_json(self.recent_files_path)
            
            if filepath in recent_files:
                recent_files.remove(filepath)
                
            # Add new filepath to start of list
            recent_files.insert(0, filepath)
            recent_files = recent_files[:3]
            
            # Save updated list
            JsonManager.save_json(self.recent_files_path, recent_files)
            
        except Exception as e:
            print(f"Error saving to recents: {e}")

    def browse(self):
        filename = filedialog.askopenfilename(
            initialdir=self.target_directory,
            title="Select Save File",
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")]
        )
        if filename:
            self.save_to_recents(filename)
            if self.file_selected_callback:
                self.file_selected_callback(filename)

    def get_recent_files(self):
        try:
            return JsonManager.load_json(self.recent_files_path)
        except Exception as e:
            print(f"Error loading recent files: {e}")
            return []