import customtkinter as ctk
import os
from Managers.JsonManager import JsonManager
from AppWindows.Dashboard import Dashboard
from PIL import Image

class AppManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.data_dir = ".trackerdata"
        self.recent_files_path = os.path.join(self.data_dir, "recent_files.json")
        self.saved_notes_path = os.path.join(self.data_dir, "saved.json")
        self.imp_path = os.path.join(self.data_dir, "star_changes.json")

        self.important_changes = {} 
        self.saved_notes = {}

        self.important_changes_path = self.imp_path 

        self.init_icons()
        self.init_data()
        self.init_window()

    def init_icons(self):
        self.app_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/app_icon.png"),
            dark_image=Image.open("assets/icons/app_icon.png"),
            size=(48, 48)
        )

    def init_data(self):
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            
            if os.path.exists(self.important_changes_path):
                self.important_changes = JsonManager.load_json(self.imp_path)

            if os.path.exists(self.saved_notes_path):
                self.saved_notes = JsonManager.load_json(self.saved_notes_path)
                    
        except Exception as e:
            print(f"Error initializing data storage: {e}")

    def init_window(self):

        self.title("File Monitor")
        self.geometry("1100x700")

        self.dashboard_window = Dashboard(self)