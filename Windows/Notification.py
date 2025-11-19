import os
import customtkinter as ctk

from Modules.types import ChangeDataType
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from Managers.AppManager import AppManager

class NotificationWindow(ctk.CTkToplevel):
    def __init__(self, *args, 
                input_change_data: ChangeDataType,
                app_manager: 'AppManager',
                # asset_manager: 'AssetManager', 
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

        # print(self.raw_change_data)

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

        self.attributes("-topmost", True) # Keeps the window above others
        self.lift()                       # Moves window to top of stack
        self.focus_force()

        self.deiconify() 
        self.grab_set()  # Block interaction with other windows
        # self.focus()

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
  
    def populate_diff(self):
        for widget in self.diff_scroll_frame.winfo_children():
            widget.destroy()

        for i, item in enumerate(self.change['diff']):
            operation, path, values = item

            if len(values) > 2 and operation == "add":
                total_items = len(values)
                for idx, sub_item in enumerate(values):
                    batch_info = f"  [{idx + 1}/{total_items}]"
                    
                    self._create_change_row(
                        index=i, 
                        path=path,
                        del_content=None, 
                        add_content=sub_item,
                        operation=operation,
                        suffix_title=batch_info
                    )
            elif len(values) > 2 and operation == "remove":
                total_items = len(values)
                for idx, sub_item in enumerate(values):
                    batch_info = f"  [{idx + 1}/{total_items}]"
                    
                    self._create_change_row(
                        index=i, 
                        path=path,
                        del_content=sub_item, 
                        add_content=None,
                        operation=operation,
                        suffix_title=batch_info
                    )   
            elif len(values) == 2 and operation == "change":
                del_content, add_content = values
                self._create_change_row(
                    index=i, 
                    path=path, 
                    del_content=del_content, 
                    add_content=add_content, 
                    operation=operation
                )
            elif len(values) == 1 and operation == "remove":
                del_content = values
                self._create_change_row(
                    index=i, 
                    path=path, 
                    del_content=del_content, 
                    add_content=None, 
                    operation=operation
                )
            elif len(values) == 1 and operation == "add":
                add_content = values
                self._create_change_row(
                    index=i, 
                    path=path, 
                    del_content=None, 
                    add_content=add_content, 
                    operation=operation
                )

    def _create_change_row(self, index, path, del_content, add_content, operation, suffix_title=""):
        """
        Helper function to draw a single row. 
        """
        # Determine background color (Alternating)
        bg_color = "#f7f7f7" if index % 2 == 0 else "#fcfcfc"

        change_frame = ctk.CTkFrame(self.diff_scroll_frame, fg_color=bg_color)
        change_frame.pack(padx=15, pady=5, fill="x", expand=True)
        change_frame.grid_columnconfigure(0, weight=1)

        diff_font = ctk.CTkFont(family="Roboto Mono", size=13, weight="normal")
        diff_font_bold = ctk.CTkFont(family="Roboto Mono", size=13, weight="bold")

        # --- Title Section ---
        title_frame = ctk.CTkFrame(change_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=5, pady=0, sticky="ew")

        arrow_label = ctk.CTkLabel(title_frame, text="", image=self.icons["arrow"])
        arrow_label.grid(row=0, column=0, padx=0, pady=0)

        # Combine Path + Suffix
        full_title_text = f"{path}{suffix_title}"
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=full_title_text,
            fg_color="transparent",
            font=diff_font_bold,
            text_color="#616161" if not suffix_title else "#888888" # Lighter if it's a sub-item
        )
        title_label.grid(row=0, column=1, padx=(3, 0), sticky="w")

        # --- Values Section ---
        values_frame = ctk.CTkFrame(change_frame, fg_color="transparent")
        values_frame.grid(row=1, column=0, padx=0, pady=0, sticky="ew")

        # -- Internal Helper: Draw Deletion (Red) --
        def draw_del(col=0):
            values_frame.grid_columnconfigure(col, weight=0)
            del_frame = ctk.CTkFrame(
                values_frame, fg_color="#fdecec", 
                border_width=2, border_color="#656565"
            )
            del_frame.grid(row=0, column=col, padx=5, pady=0, sticky="w")

            content = f"{del_content} "
            label_del = ctk.CTkLabel(
                del_frame, text=content, text_color="#b81818", font=diff_font
            )
            label_del.pack(padx=5, pady=2)

        # -- Internal Helper: Draw Addition (Green) --
        def draw_add(col=1):
            values_frame.grid_columnconfigure(col, weight=0)
            add_frame = ctk.CTkFrame(
                values_frame, fg_color="#e8f9ef", 
                border_width=2, border_color="#656565"
            )
            add_frame.grid(row=0, column=col, padx=5, pady=0, sticky="w")

            # Use the recursive formatter we made earlier
            formatted_text = self.expanded_format(add_content)
            content = f" {formatted_text}"

            label_add = ctk.CTkLabel(
                add_frame,
                text=content,
                text_color="#117e3a",
                font=diff_font,
                justify="left",
                anchor="w",
            )
            label_add.pack(padx=(5,8), pady=2)

        # --- Render logic ---
        if operation == "change":
            if del_content is not None: draw_del()
            if add_content is not None: draw_add()
        elif operation == "add":
            draw_add(col=0)
        elif operation == "remove":
            draw_del()

    # def _populate_diff(self):
    #     for widget in self.diff_scroll_frame.winfo_children():
    #         widget.destroy()

    #     for i, item in enumerate(self.raw_change_data['diff']):

    #         operation, path, values = item
    #         del_content, add_content = values

    #         change_frame = ctk.CTkFrame(
    #             self.diff_scroll_frame,
    #             fg_color="#f7f7f7" if i%2 == 0 else "#fcfcfc",
    #         )
    #         change_frame.pack( padx=15, pady=5, fill="x", expand=True)
    #         change_frame.grid_columnconfigure(0, weight=1)

    #         diff_font = ctk.CTkFont(family="Roboto Mono", size=13, weight="normal")
    #         diff_font_bold = ctk.CTkFont(family="Roboto Mono", size=13, weight="bold")

    #         title_frame = ctk.CTkFrame(
    #             change_frame,
    #             fg_color="transparent",
    #         )
    #         title_frame.grid( row=0, column=0, padx=5, pady=0, sticky="ew")

    #         arrow_label = ctk.CTkLabel(
    #             title_frame,
    #             text="",
    #             image=self.icons["arrow"]
    #         )
    #         arrow_label.grid(row=0, column=0, padx=0, pady=0)

    #         title_label = ctk.CTkLabel(
    #             title_frame,
    #             text=f"{path}",
    #             fg_color="transparent",
    #             font=diff_font_bold,
    #             text_color="#616161"
    #         )
    #         title_label.grid(row=0, column=1, padx=(3,0),sticky="w")

    #         values_frame = ctk.CTkFrame(
    #             change_frame,
    #             fg_color="transparent",
    #         )
    #         values_frame.grid( row=1, column=0, padx=0, pady=0, sticky="ew")

    #         def del_widget(col: int = 0):
    #             values_frame.grid_columnconfigure(col, weight=0)
    #             del_frame = ctk.CTkFrame(
    #                 values_frame,
    #                 fg_color="#fdecec",
    #                 border_width=2,
    #                 border_color="#656565",
    #             )
    #             del_frame.grid( row=0, column=col, padx=5, pady=0, sticky="w")

    #             # text = self.app_manager.wrap_text(input=del_content, limit=30)
    #             content = f" - {del_content} "
    #             label_del = ctk.CTkLabel(
    #                 del_frame,
    #                 text=content,
    #                 text_color="#b81818",
    #                 font=diff_font,
    #             )
    #             label_del.pack(padx=5, pady=2)

    #         def add_widget(col: int = 1):
    #             values_frame.grid_columnconfigure(col, weight=0)
    #             add_frame = ctk.CTkFrame(
    #                 values_frame,
    #                 fg_color="#e8f9ef",
    #                 border_width=2,
    #                 border_color="#656565",
    #             )
    #             add_frame.grid( row=0, column=col, padx=5, pady=0, sticky="w")

    #             # text = self.app_manager.wrap_text(input=str(add_content), limit=40)
    #             formatted_text = self.expanded_format(add_content)
    #             # content = f"{formatted_text} "
    #             # content = f" + {add_content} "
    #             label_add = ctk.CTkLabel(
    #                 add_frame,
    #                 text=formatted_text,
    #                 text_color="#117e3a",
    #                 font=diff_font,
    #                 justify="left",
    #                 anchor="nw",
    #             )
    #             label_add.pack(padx=5, pady=2)

    #         if operation == "change":
    #             del_widget()
    #             add_widget()
    #         elif operation == "add":
    #             add_widget(col=0)
    #         elif operation == "del":
    #             del_widget()

    def expanded_format(self, data, indent:int = 0):

        # Define indentation size (e.g., 4 spaces)
        step = "    " 
        current_indent = step * indent
        next_indent = step * (indent + 1)

        if isinstance(data, dict):
            if not data: return "{}" # Handle empty dicts
            lines = ["{"]
            for key, value in data.items():
                # Format: 'Key': Value (recursively formatted)
                lines.append(f"{next_indent}{repr(key)}: {self.expanded_format(value, indent + 1)},")
            lines.append(f"{current_indent}}}")
            return "\n".join(lines)

        elif isinstance(data, (list, tuple)):
            is_list = isinstance(data, list)
            if not data: return "[]" if is_list else "()"
            
            open_char = "[" if is_list else "("
            close_char = "]" if is_list else ")"
            
            lines = [open_char]
            for item in data:
                lines.append(f"{next_indent}{self.expanded_format(item, indent + 1)},")
            lines.append(f"{current_indent}{close_char}")
            return "\n".join(lines)

        else:
            # Base case: Integers, Strings, Booleans, None
            return repr(data)

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

