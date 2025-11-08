from datetime import time
import json
import customtkinter as ctk
import os
from PIL import Image

from AppWindows.Dashboard import Dashboard
from AppWindows.NotificationWindow import NotificationWindow
from Managers.JsonManager import JsonManager
from Managers.FileHandler import FileHandler
from Managers.Monitor import Monitor

class AppManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.console_logging = False

        self.M_fileHandler = None
        self.M_monitor = None
        self.W_dashboard = None
        self.notification_window = None

        self.important_changes = {} 
        self.saved_notes = {}

        self.init_icons()
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
            os.makedirs(self.M_fileHandler.data_dir, exist_ok=True)
            
            if os.path.exists(self.M_fileHandler.imp_path):
                self.important_changes = JsonManager.load_json(self.M_fileHandler.imp_path)

            if os.path.exists(self.M_fileHandler.saved_notes_path):
                self.saved_notes = JsonManager.load_json(self.M_fileHandler.saved_notes_path)
                    
        except Exception as e:
            print(f"Error initializing data storage: {e}")

    def init_window(self):
        self.title("File Monitor")
        self.geometry("920x560")

        # Setup managers and UI
        self.M_fileHandler = FileHandler()
        self.init_data()
        self.M_monitor = Monitor(self)
        self.W_dashboard = Dashboard(self)

        # Register window close handler
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """Handles application shutdown"""
        # Log shutdown
        if self.W_dashboard:
            self.W_dashboard.main_log("Application shutting down...", "INFO")
        
        # Cleanup background tasks
        if self.M_monitor:
            self.M_monitor.cleanup()
        
        # Close window
        self.quit()
        self.destroy()

    def show_notification(self):
        if self.notification_window is None or not self.notification_window.winfo_exists():
            self.notification_window = NotificationWindow(self)