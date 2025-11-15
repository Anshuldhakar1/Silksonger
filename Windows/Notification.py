import customtkinter as ctk

from Modules.types import ChangeDataType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Managers.AssetManager import AssetManager

class NotificaitonWindow(ctk.CTkToplevel):
    def __init__(self, *args, 
                input_change_data: ChangeDataType, 
                asset_manager: 'AssetManager', 
                **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.raw_change_data = input_change_data
        self.icons = {
            "app_icon": asset_manager.get_icon("app_icon"),
            "star_icon": asset_manager.get_icon("star_icon")
        }

        self.title("Change Detected")
        self.geometry("900x550") 
        self.withdraw()  

        self.configure(fg_color="#FAFAFA")

        # --- Main Window Configuration ---
        self.grid_rowconfigure(0, weight=0)  # Header row
        self.grid_rowconfigure(1, weight=1)  # Main content row
        self.grid_columnconfigure(0, weight=2) # Diff column
        self.grid_columnconfigure(1, weight=1) # Notes column

        self._gui_header()
        self._gui_main()

    def _gui_header(self):
        pass

    def _gui_main(self):
        self._gui_diff()
        self._gui_notes()

    def _gui_diff(self):
        pass

    def _gui_notes(self):
        pass