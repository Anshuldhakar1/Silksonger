import customtkinter as ctk
from typing import Dict, Literal
from PIL import Image
import sys
import os

IconName = Literal[
    "app_icon", "play_icon",
    "pause_icon", "browse_icon",
    "history_icon", "change_log_icon",
    "star_icon", "danger_icon"
]

class AssetManager():
    def __init__(self):

        self._icons: Dict[IconName, ctk.CTkImage] = {}
        self._load_icons()

    def get_icon(self, icon_name: IconName) -> ctk.CTkImage:
        """Fetches an icon by its name."""
        return self._icons[icon_name]
    
    def _path(self, relative_path: str) -> str:
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            # This is for --onefile mode
            base_path = sys._MEIPASS
        except Exception:
            # This is for --onedir mode or running as a .py script
            base_path = os.path.dirname(os.path.abspath(sys.argv[0]))

        return os.path.join(base_path, relative_path)   

    def _load_icons(self):

        self._icons["app_icon"] = ctk.CTkImage(
            light_image=Image.open(self._path("assets/icons/app_icon.png") ),
            dark_image=Image.open(self._path("assets/icons/app_icon.png")),
            size=(48, 48)
        )

        self._icons["play_icon"] = ctk.CTkImage(
            light_image=Image.open(self._path("assets/icons/pause-play.png")),
            dark_image=Image.open(self._path("assets/icons/pause-play.png")),
            size=(16, 16)
        )
        self._icons["pause_icon"] = ctk.CTkImage(
            light_image=Image.open(self._path("assets/icons/end.png")),
            dark_image=Image.open(self._path("assets/icons/end.png")),
            size=(16, 16)
        )
        self._icons["browse_icon"] = ctk.CTkImage(
            light_image=Image.open(self._path("assets/icons/folder.png")),
            dark_image=Image.open(self._path("assets/icons/folder.png")),
            size=(16,16)
        )
        self._icons["history_icon"] = ctk.CTkImage(
            light_image=Image.open(self._path("assets/icons/history.png")),
            dark_image=Image.open(self._path("assets/icons/history.png")),
            size=(16,16)
        )
        self._icons["change_log_icon"] = ctk.CTkImage(
            light_image=Image.open(self._path("assets/icons/document.png")),
            dark_image=Image.open(self._path("assets/icons/document.png")),
            size=(16,16)
        )
        self._icons["star_icon"] = ctk.CTkImage(
            light_image=Image.open(self._path("assets/icons/star.png")),
            dark_image=Image.open(self._path("assets/icons/star.png")),
            size=(16,16)
        )
        self._icons["danger_icon"] = ctk.CTkImage(
            light_image=Image.open(self._path("assets/icons/danger2.png")),
            dark_image=Image.open(self._path("assets/icons/danger2.png")),
            size=(56,56)
        )