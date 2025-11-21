import os
import traceback
from typing import Callable, TYPE_CHECKING
import customtkinter as ctk

from Modules.error import ChangeWindowError
from Modules.types import ChangeDataType
from Modules.DiffLogic import render_diff_view # Import the new renderer

if TYPE_CHECKING:
    from Managers.AppManager import AppManager

class ChangeWindow(ctk.CTkToplevel):
    def __init__(self, *args, 
                app_manager: 'AppManager',
                note: str, 
                change: ChangeDataType,
                **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.app_manager = app_manager
        self.note: str = note
        self.change: ChangeDataType = change

        self.title("Change")
        self.geometry("700x550") 
        self.resizable(False, False)
        self.withdraw()

        self.configure(fg_color="white")

        self.grid_rowconfigure(0, weight=0)  
        self.grid_rowconfigure(1, weight=1)  
        self.grid_rowconfigure(2, weight=0)  

        self.grid_columnconfigure(0, weight=1)

        try:
            self._gui_header()
            self._gui_main()
            self._gui_footer()

            self.deiconify()
            self.grab_set()  
            self.focus()
            
            self.protocol("WM_DELETE_WINDOW", self.closing)
        except Exception as e:
            traceback.print_exc()
            self.destroy() 
            self.app_manager._error_popup(ChangeWindowError(str(e)))
    
    def _gui_header(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="#f0f0f0", corner_radius=0)
        self.header_frame.grid(row=0, column=0,  sticky="ew")

        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)

        self.header_frame.grid_rowconfigure(0, weight=0)  
        self.header_frame.grid_rowconfigure(1, weight=0)  
        self.header_frame.grid_rowconfigure(2, weight=0)

        divider = ctk.CTkFrame(self.header_frame,
                            height=1, 
                            fg_color="#B8B8B8",
                            border_width=1)   

        divider.grid(row=0, column=0, sticky="ew", pady=0, columnspan=2)

        base_dir = os.path.join(os.path.expanduser("~"), "AppData", "LocalLow", "Team Cherry")
        filepath = self.change.get("filepath")[len(base_dir):]

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=filepath,
            fg_color="transparent",
            font=ctk.CTkFont(family="Roboto Mono", size=14),
            text_color="#4E4E4E",
            anchor="w",
            justify="left"
        )
        self.title_label.grid(row=1,column=0,padx=(15,0), pady=8, sticky="w")

        self.timestamp_label = ctk.CTkLabel(
            self.header_frame,
            fg_color="transparent",
            text=self.change.get("timestamp"),
            font=ctk.CTkFont(family="Roboto Mono", size=14),
            text_color="#5f6675",
            anchor="w"
        )
        self.timestamp_label.grid(row=1,column=1,padx=(0,15), pady=8)

        divider = ctk.CTkFrame(self.header_frame,
                            height=1, 
                            fg_color="#5C5C5C",
                            border_width=1)   

        divider.grid(row=2, column=0, sticky="ew", pady=0, columnspan=2)

    def _gui_main(self):
        self.diff_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        self.diff_frame.grid(row=1, column=0, sticky="nsew", padx=0)

        self.diff_frame.grid_rowconfigure(0, weight=1)
        self.diff_frame.grid_columnconfigure(0, weight=1)

        self.diff_scroll_frame = ctk.CTkScrollableFrame(
            self.diff_frame,
            fg_color="transparent",
        )
        self.diff_scroll_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=10)

        # --- Use Centralized Render Logic ---
        render_diff_view(
            scroll_frame=self.diff_scroll_frame, 
            diff_data=self.change['diff'], 
            asset_manager=self.app_manager.AssetManager
        )

    def _gui_footer(self):
        FOOTER_COLOR = "#f0f0f0"
        self.footer_frame = ctk.CTkFrame(self, fg_color=FOOTER_COLOR)
        self.footer_frame.grid( padx=0, pady=0, sticky="ew")

        FOOTER_PADDING = 10

        self.footer_frame.grid_columnconfigure(0,weight=1)
        self.footer_frame.grid_columnconfigure(1,weight=0)

        divider = ctk.CTkFrame(self.footer_frame,
                            height=1, 
                            fg_color="#5C5C5C",
                            border_width=1)   

        divider.grid(row=0, column=0, sticky="ew", pady=0, columnspan=2)

        self.note_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.note_frame.grid( row=1, column=0, sticky="ew", pady=FOOTER_PADDING, padx=(10,0))

        self.btn_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.btn_frame.grid( row=1, column=1, sticky="w", pady=FOOTER_PADDING, padx=(0,10))

        font_bold = ctk.CTkFont(family="Roboto Mono", size=14, weight="bold")
        font_normal = ctk.CTkFont(family="Roboto Mono", size=14, weight="normal")

        self.note_frame.grid_columnconfigure(0,weight=0)
        self.note_frame.grid_columnconfigure(1,weight=1)

        note_label1 = ctk.CTkLabel(self.note_frame, text="Note:", font=font_bold)
        note_label1.grid( row=0, column=0, padx=0, pady=0)

        note_label2 = ctk.CTkLabel(
            self.note_frame,
            text=self.app_manager.wrap_text(input=self.note, limit=80),
            font=font_normal,
            justify="left",
            text_color="#4E4E4E",
        )
        note_label2.grid( row=0, column=1, padx=(15,0), pady=0, sticky="w")

        self.btn_frame.grid_columnconfigure(0,weight=0)
        self.btn_frame.grid_columnconfigure(1,weight=0)
        self.btn_frame.grid_columnconfigure(2,weight=0)

        btn3 = ctk.CTkButton(
            self.btn_frame,
            text=" Close ",
            font=font_normal,
            width=0,
            fg_color="#D92626",
            hover_color="#CC2525",
            command=self.closing,
        )
        btn3.grid( row=0, column=2, padx=(10,15), pady=0)

    def closing(self):
        self.destroy()