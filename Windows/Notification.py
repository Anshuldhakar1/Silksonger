import os
import customtkinter as ctk

from Modules.types import ChangeDataType
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from Managers.AssetManager import AssetManager

class NotificaitonWindow(ctk.CTkToplevel):
    def __init__(self, *args, 
                input_change_data: ChangeDataType, 
                asset_manager: 'AssetManager', 
                window_save_callback: Callable,
                window_closed_callback: Callable,
                **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.raw_change_data = input_change_data
        self.window_save_callback = window_save_callback
        self.window_closed_callback = window_closed_callback
        self.icons = {
            "app_icon": asset_manager.get_icon("app_icon"),
            "star_icon": asset_manager.get_icon("star_icon"),
            "arrow": asset_manager.get_icon("arrow_right"),
        }
        self.is_imp: bool = False

        self.title("Change Detected")
        self.geometry("900x550") 
        self.withdraw()  # hide the window till the widgets are added

        self.configure(fg_color="#FAFAFA")

        # --- Main Window Configuration ---
        self.grid_rowconfigure(0, weight=0)  # Header row
        self.grid_rowconfigure(1, weight=1)  # Main content row
        self.grid_columnconfigure(0, weight=1) # Diff column
        self.grid_columnconfigure(1, weight=0) # Notes column

        self._gui_header()
        self._gui_main()

        self.deiconify() 
        self.grab_set()  # Block interaction with other windows
        self.focus()

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
        # Placed slightly closer to the title
        self.subtitle_label.place(x=0, y=20) 

    def _gui_main(self):
        self._gui_diff()
        self._gui_notes()

    def _gui_diff(self):
        # --- Corrected GUI Code ---

        # This frame holds the title and the scrollable area
        self.diff_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0,
            border_width=1, border_color="#d4d4d4"   )
        self.diff_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Configure the frame grid
        self.diff_frame.grid_rowconfigure(0, weight=0)    # Title row
        self.diff_frame.grid_rowconfigure(1, weight=1)    # Scrollable area row
        self.diff_frame.grid_columnconfigure(0, weight=1)

        base_dir = os.path.join(os.path.expanduser("~"), 
            "AppData", 
            "LocalLow", 
            "Team Cherry")
        text = self.raw_change_data['filepath'][len(base_dir):]
        self.diff_title_label = ctk.CTkLabel(
            self.diff_frame,
            # text=f"Changes in {self.raw_change_data['filepath'] if self.raw_change_data else 'Unknown'}",
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

        self._populate_diff()

    def _gui_notes(self):
        # --- 3. Sidebar Frame (Right Column) ---
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
        
        # --- Bind the <KeyRelease> event to the validation function ---
        self.notes_textbox.bind("<KeyRelease>", self._validate_notes)

        # --- Sidebar Action Buttons (Refactored with .grid) ---
        self.button_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Configure columns for 50/50 split
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
        # Full width (spans 2 columns), with 6px padding below it
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
        # Row 1, Column 0. 3px padding on the right.
        self.save_btn.grid(row=1, column=0, sticky="ew", padx=(0, 3))

        self.discard_btn = ctk.CTkButton(
            self.button_frame,
            text="Discard Change",
            fg_color="#ffffff", text_color="#111",
            border_width=1, border_color="#ccc",
            hover_color="#f0f0f0",
            command=self.discard_btn_clicked
        )
        # Row 1, Column 1. 3px padding on the left.
        self.discard_btn.grid(row=1, column=1, sticky="ew", padx=(3, 0))

    def _populate_diff(self):
        for widget in self.diff_scroll_frame.winfo_children():
            widget.destroy()

        for i, item in enumerate(self.change['diff']):

            operation, path, values = item
            del_content, add_content = values

            change_frame = ctk.CTkFrame(
                self.diff_scroll_frame,
                fg_color="#f7f7f7" if i%2 == 0 else "#fcfcfc",
            )
            change_frame.pack( padx=15, pady=5, fill="x", expand=True)
            change_frame.grid_columnconfigure(0, weight=1)

            diff_font = ctk.CTkFont(family="Roboto Mono", size=13, weight="normal")
            diff_font_bold = ctk.CTkFont(family="Roboto Mono", size=13, weight="bold")

            title_frame = ctk.CTkFrame(
                change_frame,
                fg_color="transparent",
            )
            title_frame.grid( row=0, column=0, padx=5, pady=0, sticky="ew")

            arrow_label = ctk.CTkLabel(
                title_frame,
                text="",
                image=self.icons["arrow"]
            )
            arrow_label.grid(row=0, column=0, padx=0, pady=0)

            title_label = ctk.CTkLabel(
                title_frame,
                text=f"{path}",
                fg_color="transparent",
                font=diff_font_bold,
                text_color="#616161"
            )
            title_label.grid(row=0, column=1, padx=(3,0),sticky="w")

            values_frame = ctk.CTkFrame(
                change_frame,
                fg_color="transparent",
            )
            values_frame.grid( row=1, column=0, padx=0, pady=0, sticky="ew")

            def del_widget(col: int = 0):
                values_frame.grid_columnconfigure(col, weight=0)
                del_frame = ctk.CTkFrame(
                    values_frame,
                    fg_color="#fdecec",
                    border_width=2,
                    border_color="#656565",
                )
                del_frame.grid( row=0, column=col, padx=5, pady=0, sticky="w")

                label_del = ctk.CTkLabel(
                    del_frame,
                    text=f" - {del_content} ",
                    text_color="#b81818",
                    font=diff_font,
                )
                label_del.pack(padx=5, pady=2)

            def add_widget(col: int = 1):
                values_frame.grid_columnconfigure(col, weight=0)
                add_frame = ctk.CTkFrame(
                    values_frame,
                    fg_color="#e8f9ef",
                    border_width=2,
                    border_color="#656565",
                )
                add_frame.grid( row=0, column=col, padx=5, pady=0, sticky="w")

                label_add = ctk.CTkLabel(
                    add_frame,
                    text=f" + {add_content} ",
                    text_color="#117e3a",
                    font=diff_font,
                )
                label_add.pack(padx=5, pady=2)

            if operation == "change":
                del_widget()
                add_widget()
            elif operation == "add":
                add_widget(col=0)
            elif operation == "del":
                del_widget()

    def mark_important_btn(self):
        if not self.is_imp:
            self.is_imp = True
            self.mark_important_btn.configure(text="Unmark")
        else:
            self.is_imp = False
            self.mark_important_btn.configure(text="Mark as Important")

    def save_btn(self):
        note = self.notes_textbox.get("1.0", "end").strip()
        if not note:
            return
        self.window_save_callback(note = note, changes=self.raw_change_data, imp=self.is_imp)
        self.destroy()

    def discard_btn_clicked(self):
        self.destroy()
        # self.master.destroy()
        self.window_closed_callback()

    def _validate_notes(self, event=None):
        note_content = self.notes_textbox.get("1.0", "end").strip()
        
        if note_content:
            self.save_btn.configure(state="normal")
        else:
            self.save_btn.configure(state="disabled")

