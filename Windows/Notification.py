import os
import traceback
import customtkinter as ctk

from Modules.error import NotificationWindowError
from Modules.types import ChangeDataType
from Modules.DiffLogic import render_diff_view  # Import the new renderer
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from Managers.AppManager import AppManager

class NotificationWindow(ctk.CTkToplevel):
    def __init__(self, *args, 
                input_change_data: ChangeDataType,
                app_manager: 'AppManager',
                window_save_callback: Callable,
                window_closed_callback: Callable,
                **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.app_manager = app_manager
        self.raw_change_data = input_change_data
        self.window_save_callback = window_save_callback
        self.window_closed_callback = window_closed_callback
        self.icons = {
            "app_icon": self.app_manager.AssetManager.get_icon("app_icon"),
            "star_icon": self.app_manager.AssetManager.get_icon("star_icon"),
            "arrow": self.app_manager.AssetManager.get_icon("arrow_right"),
        }
        self.is_imp: bool = False

        self.title("Change Detected")
        self.geometry("900x550") 
        self.withdraw() 

        self.configure(fg_color="#FAFAFA")

        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=0) 

        try:
            self._gui_header()
            self._gui_main()

            self.attributes("-topmost", True) 
            self.lift()                       
            self.focus_force()

            self.deiconify() 
            self.grab_set() 
        except Exception as e:
            traceback.print_exc()
            self.destroy()
            self.app_manager._error_popup(NotificationWindowError(str(e)))

        self.protocol("WM_DELETE_WINDOW", self.discard_btn_clicked)

    def _gui_header(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="white", height=65, corner_radius=0)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        self.icon_label = ctk.CTkLabel(
            self.header_frame, text="", image=self.icons.get("app_icon"), compound="left"
        )
        self.icon_label.place(x=20, y=10)
        
        self.text_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.text_container.place(x=85, y=12)
        
        self.title_text = f"File Change: {os.path.basename(self.raw_change_data['filepath']) if self.raw_change_data else 'Unknown'}"
        self.title_label = ctk.CTkLabel(
            self.text_container,
            text=self.title_text,
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            anchor="w"
        )
        self.title_label.place(x=0, y=-6)
        
        self.subtitle_text = f"Modified at {self.raw_change_data['timestamp'] if self.raw_change_data else 'Unknown time'}"
        self.subtitle_label = ctk.CTkLabel(
            self.text_container,
            text=self.subtitle_text,
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color="gray",
            anchor="w"
        )
        self.subtitle_label.place(x=0, y=20) 

    def _gui_main(self):
        self._gui_diff()
        self._gui_notes()

    def _gui_diff(self):
        self.diff_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0,
            border_width=1, border_color="#d4d4d4"   )
        self.diff_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        self.diff_frame.grid_rowconfigure(0, weight=0)    
        self.diff_frame.grid_rowconfigure(1, weight=1)    
        self.diff_frame.grid_columnconfigure(0, weight=1)

        base_dir = os.path.join(os.path.expanduser("~"), "AppData", "LocalLow", "Team Cherry")
        text = self.raw_change_data['filepath'][len(base_dir):]
        self.diff_title_label = ctk.CTkLabel(
            self.diff_frame,
            text=text,
            font=ctk.CTkFont(family="Roboto Mono", size=14),
            text_color="#555",
            anchor="w"
        )
        self.diff_title_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 5))

        self.diff_scroll_frame = ctk.CTkScrollableFrame(
            self.diff_frame,
            fg_color="transparent",
            border_width=1,
            border_color="#cdcdcd"
        )
        self.diff_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # --- Use Centralized Render Logic ---
        render_diff_view(
            scroll_frame=self.diff_scroll_frame, 
            diff_data=self.raw_change_data['diff'], 
            asset_manager=self.app_manager.AssetManager
        )

    def _gui_notes(self):
        self.sidebar_frame = ctk.CTkFrame(
            self, fg_color="#f8fafc", corner_radius=0,
            border_width=1, border_color="#d4d4d4"    
        )
        self.sidebar_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 1), pady=(0, 1))
        self.sidebar_frame.grid_rowconfigure(1, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        self.notes_label = ctk.CTkLabel(
            self.sidebar_frame, text="Notes",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            anchor="w"
        )
        self.notes_label.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))

        self.notes_textbox = ctk.CTkTextbox(
            self.sidebar_frame, font=("Helvetica", 13),
            border_width=1, border_color="#ccc", fg_color="#ffffff"
        )
        self.notes_textbox.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        self.notes_textbox.bind("<KeyRelease>", self._validate_notes)

        self.button_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        self.button_frame.grid_columnconfigure((0, 1), weight=1) 

        self.mark_important_btn = ctk.CTkButton(
            self.button_frame,
            text="Mark as Important",
            image=self.icons.get("star_icon"), 
            compound="left",
            fg_color="#DC2626",
            hover_color="#b91c1c",
            command=self.mark_important_btn
        )
        self.mark_important_btn.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        self.save_btn = ctk.CTkButton(
            self.button_frame,
            text="Save Change",
            fg_color="#ffffff", text_color="#111",
            border_width=1, border_color="#ccc",
            hover_color="#f0f0f0",
            state="disabled",
            command=self.save_btn
        )
        self.save_btn.grid(row=1, column=0, sticky="ew", padx=(0, 3))

        self.discard_btn = ctk.CTkButton(
            self.button_frame,
            text="Discard Change",
            fg_color="#ffffff", text_color="#111",
            border_width=1, border_color="#ccc",
            hover_color="#f0f0f0",
            command=self.discard_btn_clicked
        )
        self.discard_btn.grid(row=1, column=1, sticky="ew", padx=(3, 0))
  
    def mark_important_btn(self):
        if not self.is_imp:
            self.is_imp = True
            self.mark_important_btn.configure(text="Unmark")
        else:
            self.is_imp = False
            self.mark_important_btn.configure(text="Mark as Important")

    def save_btn(self):
        try:
            note = self.notes_textbox.get("1.0", "end").strip()
            if not note:
                return
            self.window_save_callback(note = note, changes=self.raw_change_data, imp=self.is_imp)
            self.destroy()
        except Exception as e:
            traceback.print_exc()
            self.app_manager._error_popup(NotificationWindowError(f"Save failed: {e}"))

    def discard_btn_clicked(self):
        self.window_closed_callback()
        self.destroy()

    def _validate_notes(self, event=None):
        note_content = self.notes_textbox.get("1.0", "end").strip()
        if note_content:
            self.save_btn.configure(state="normal")
        else:
            self.save_btn.configure(state="disabled")