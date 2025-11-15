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
            "star_icon": asset_manager.get_icon("star_icon")
        }
        self.is_imp: bool = False

        self.title("Change Detected")
        self.geometry("900x550") 
        self.withdraw()  # hide the window till the widgets are added

        self.configure(fg_color="#FAFAFA")

        # --- Main Window Configuration ---
        self.grid_rowconfigure(0, weight=0)  # Header row
        self.grid_rowconfigure(1, weight=1)  # Main content row
        self.grid_columnconfigure(0, weight=2) # Diff column
        self.grid_columnconfigure(1, weight=1) # Notes column

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
        self.diff_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        self.diff_frame.grid(row=1, column=0, sticky="nsew", padx=(1, 0), pady=(0, 1))
        self.diff_frame.grid_rowconfigure(1, weight=1)
        self.diff_frame.grid_columnconfigure(0, weight=1)

        self.diff_title_label = ctk.CTkLabel(
            self.diff_frame,
            text=f"Changes in {self.raw_change_data['filepath'] if self.raw_change_data else 'Unknown'}",
            font=ctk.CTkFont(family="Helvetica", size=13),
            text_color="#555",
            anchor="w"
        )
        self.diff_title_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 5))
        
        self.diff_textbox = ctk.CTkTextbox(
            self.diff_frame, font=("Consolas", 13), fg_color="#f8f8f8",
            wrap="none", border_width=1, border_color="#e0e0e0"
        )
        self.diff_textbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.diff_textbox.tag_config("add", background="#e6ffed", foreground="#006d00")
        self.diff_textbox.tag_config("del", background="#ffeef0", foreground="#b30000")
        self.diff_textbox.tag_config("context", foreground="#555")

        self._populate_diff()

    def _gui_notes(self):
        # --- 3. Sidebar Frame (Right Column) ---
        self.sidebar_frame = ctk.CTkFrame(self, fg_color="#f8fafc", corner_radius=0)
        self.sidebar_frame.grid(row=1, column=1, sticky="nsew", padx=(1, 1), pady=(0, 1))
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
        self.diff_textbox.configure(state="normal")
        self.diff_textbox.delete("1.0", "end")
        
        # Check for valid diff data
        if not (self.raw_change_data and 'diff' in self.raw_change_data and len(self.raw_change_data['diff']) > 0):
            self.diff_textbox.insert("end", "No diff data available.")
            self.diff_textbox.configure(state="disabled")
            return

        first_item = self.raw_change_data['diff'][0]

        if not isinstance(first_item, tuple):
             self.diff_textbox.insert("end", "Error: Diff data is not in the expected tuple format.")
             self.diff_textbox.configure(state="disabled")
             return
             
        for item in self.raw_change_data['diff']:
            if not isinstance(item, tuple):
                self.diff_textbox.insert("end", f"Error: Invalid diff item: {item}\n", "del")
                continue

            try:
                operation, path, values = item
                self.diff_textbox.insert("end", f"{path}\n", "context")
                
                if operation == "change":
                    old_val, new_val = values
                    self.diff_textbox.insert("end", f"  - {old_val}\n", "del")
                    self.diff_textbox.insert("end", f"  + {new_val}\n", "add")
                elif operation == "add":
                   self.diff_textbox.insert("end", f"  + {values}\n", "add")
                elif operation == "remove":
                   self.diff_textbox.insert("end", f"  - {values}\n", "del")
                    
                else:
                    self.diff_textbox.insert("end", f"  {values}\n", "context")
                
                self.diff_textbox.insert("end", "\n", "context")
                    
            except Exception as e:
                self.diff_textbox.insert("end", f"Error processing tuple: {item} | {e}\n", "del")
        
        self.diff_textbox.configure(state="disabled") # Make read-only

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
        pass
    
        self.window_save_callback(note = note, changes=self.raw_change_data, imp=self.is_imp)
        self.destroy()

        # self.app_root.M_fileHandler.save_new_change(
        #     self.change_data['filepath'],
        #     note,
        #     self.change_data,
        #     self.is_imp
        # )

        # self.app_root.W_dashboard.add_log_entry(
        #     timestamp=self.change_data['timestamp'],
        #     main_text=note,
        #     sub_text=f"{len(self.change_data['diff'])} changes detected",

        # )

        # # print(self.change_data)

        # new_data = {
        #     "filepath": self.change_data['filepath'],
        #     "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        #     "diff": self.change_data['diff'],
        # }

        # # print(self.app_root.saved_notes)

        # msg = f"Saved change with note: \"{note}\""
        # if self.is_imp:
        #     msg = f"Saved important change with note: \"{note}\""
        # self.app_root.W_dashboard.main_log( msg, "SAVED" if not self.is_imp else "SAVED_IMP")
        # self.app_root.W_dashboard.main_log("Waiting for changes...", "INFO")

        # self.app_root.M_monitor.start_monitoring()
        # self.destroy()

    def discard_btn_clicked(self):
        print("discard method called")
        self.destroy()
        self.window_closed_callback()

    def _validate_notes(self, event=None):
        note_content = self.notes_textbox.get("1.0", "end").strip()
        
        if note_content:
            self.save_btn.configure(state="normal")
        else:
            self.save_btn.configure(state="disabled")

