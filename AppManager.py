import customtkinter as ctk
import os
from PIL import Image

from AppWindows.Dashboard import Dashboard
from Managers.JsonManager import JsonManager
from Managers.FileHandler import FileHandler

class AppManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.fileHandler = FileHandler()

        self.important_changes = {} 
        self.saved_notes = {}

        self.init_icons()
        self.init_data()
        self.init_window()

    def init_icons(self):
        self.app_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/app_icon.png"),
            dark_image=Image.open("assets/icons/app_icon.png"),
            size=(48, 48)
        )
        
        self.play_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/pause-play.png"),
            dark_image=Image.open("assets/icons/pause-play.png"),
            size=(16, 16)
        )
        self.pause_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/end.png"),
            dark_image=Image.open("assets/icons/end.png"),
            size=(16, 16)
        )
        self.browse_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/folder.png"),
            dark_image=Image.open("assets/icons/folder.png"),
            size=(16,16)
        )
        self.history_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/history.png"),
            dark_image=Image.open("assets/icons/history.png"),
            size=(16,16)
        )
        self.change_log_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/document.png"),
            dark_image=Image.open("assets/icons/document.png"),
            size=(16,16)
        )
        self.star_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/star.png"),
            dark_image=Image.open("assets/icons/star.png"),
            size=(16,16)
        )

    def init_data(self):
        try:
            os.makedirs(self.fileHandler.data_dir, exist_ok=True)
            
            if os.path.exists(self.fileHandler.imp_path):
                self.important_changes = JsonManager.load_json(self.fileHandler.imp_path)

            if os.path.exists(self.fileHandler.saved_notes_path):
                self.saved_notes = JsonManager.load_json(self.fileHandler.saved_notes_path)
                    
        except Exception as e:
            print(f"Error initializing data storage: {e}")

    def init_window(self):

        self.title("File Monitor")
        self.geometry("920x560")

        self.dashboard_window = Dashboard(self)