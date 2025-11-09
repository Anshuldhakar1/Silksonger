from PIL import Image
import customtkinter as ctk
import os

from PIL import Image
import customtkinter as ctk
import os

class NotificationWindow(ctk.CTkToplevel):
    def __init__(self, *args, change_data=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("Change Detected")
        self.geometry("900x550") 
        self.app_root = args[0]
        
        # --- Main Window Configuration ---
        self.grid_rowconfigure(0, weight=0)  # Header row
        self.grid_rowconfigure(1, weight=1)  # Main content row
        self.grid_columnconfigure(0, weight=2) # Diff column
        self.grid_columnconfigure(1, weight=1) # Notes column

        # --- Load Assets ---
        self.app_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/app_icon.png"),
            dark_image=Image.open("assets/icons/app_icon.png"),
            size=(24, 24)
        )
        self.star_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/star.png"),
            dark_image=Image.open("assets/icons/star.png"),
            size=(12, 12)
        )

        # --- 1. Header Frame ---
        header_frame = ctk.CTkFrame(self, fg_color="white", height=60, corner_radius=0)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        icon_label = ctk.CTkLabel(
            header_frame, text="", image=self.app_icon, compound="left"
        )
        icon_label.place(x=20, y=18)
        
        text_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        text_container.place(x=60, y=12)
        
        title_text = f"File Change: {os.path.basename(change_data['filepath']) if change_data else 'Unknown'}"
        title_label = ctk.CTkLabel(
            text_container,
            text=title_text,
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            anchor="w"
        )
        title_label.place(x=0, y=0)
        
        subtitle_text = f"Modified at {change_data['timestamp'] if change_data else 'Unknown time'}"
        subtitle_label = ctk.CTkLabel(
            text_container,
            text=subtitle_text,
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color="gray",
            anchor="w"
        )
        # Placed slightly closer to the title
        subtitle_label.place(x=0, y=20) 

        # close_btn = ctk.CTkButton(
        #     header_frame, text="✕", font=ctk.CTkFont(size=16),
        #     fg_color="transparent", text_color="gray", hover_color="#eee",
        #     width=30, height=30, command=self.destroy
        # )
        # close_btn.place(relx=1.0, y=15, x=-15, anchor="ne")

        # --- 2. Diff Frame (Left Column) ---
        diff_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        diff_frame.grid(row=1, column=0, sticky="nsew", padx=(1, 0), pady=(0, 1))
        diff_frame.grid_rowconfigure(1, weight=1)
        diff_frame.grid_columnconfigure(0, weight=1)

        diff_title_label = ctk.CTkLabel(
            diff_frame,
            text=f"Changes in {change_data['filepath'] if change_data else 'Unknown'}",
            font=ctk.CTkFont(family="Helvetica", size=13),
            text_color="#555",
            anchor="w"
        )
        diff_title_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 5))
        
        self.diff_textbox = ctk.CTkTextbox(
            diff_frame, font=("Consolas", 13), fg_color="#f8f8f8",
            wrap="none", border_width=1, border_color="#e0e0e0"
        )
        self.diff_textbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.diff_textbox.tag_config("add", background="#e6ffed", foreground="#006d00")
        self.diff_textbox.tag_config("del", background="#ffeef0", foreground="#b30000")
        self.diff_textbox.tag_config("context", foreground="#555")

        self._populate_diff(change_data)

        # --- 3. Sidebar Frame (Right Column) ---
        sidebar_frame = ctk.CTkFrame(self, fg_color="#f8fafc", corner_radius=0)
        sidebar_frame.grid(row=1, column=1, sticky="nsew", padx=(1, 1), pady=(0, 1))
        sidebar_frame.grid_rowconfigure(1, weight=1)
        sidebar_frame.grid_columnconfigure(0, weight=1)

        notes_label = ctk.CTkLabel(
            sidebar_frame, text="Notes",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            anchor="w"
        )
        notes_label.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))

        self.notes_textbox = ctk.CTkTextbox(
            sidebar_frame, font=("Helvetica", 13),
            border_width=1, border_color="#ccc", fg_color="#ffffff"
        )
        self.notes_textbox.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # --- Sidebar Action Buttons (Refactored with .grid) ---
        button_frame = ctk.CTkFrame(sidebar_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Configure columns for 50/50 split
        button_frame.grid_columnconfigure((0, 1), weight=1) 

        mark_important_btn = ctk.CTkButton(
            button_frame,
            text="Mark as Important",
            image=self.star_icon, 
            compound="left",
            fg_color="#DC2626",
            hover_color="#b91c1c",
            command=self.mark_important_btn
        )
        # Full width (spans 2 columns), with 6px padding below it
        mark_important_btn.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Change",
            fg_color="#ffffff", text_color="#111",
            border_width=1, border_color="#ccc",
            hover_color="#f0f0f0",
            command=self.save_btn
        )
        # Row 1, Column 0. 3px padding on the right.
        save_btn.grid(row=1, column=0, sticky="ew", padx=(0, 3))

        discard_btn = ctk.CTkButton(
            button_frame,
            text="Discard Change",
            fg_color="#ffffff", text_color="#111",
            border_width=1, border_color="#ccc",
            hover_color="#f0f0f0",
            command=self.discard_btn
        )
        # Row 1, Column 1. 3px padding on the left.
        discard_btn.grid(row=1, column=1, sticky="ew", padx=(3, 0))

        # --- Final Window Setup ---
        self.attributes('-topmost', True)
        self.lift()

    def _populate_diff(self, change_data):
        """
        Populates the diff textbox.
        This function is streamlined to *only* handle the
        structured tuple format (list[tuple]) that your app provides.
        """
        self.diff_textbox.configure(state="normal")
        self.diff_textbox.delete("1.0", "end")
        
        # Check for valid diff data
        if not (change_data and 'diff' in change_data and len(change_data['diff']) > 0):
            self.diff_textbox.insert("end", "No diff data available.")
            self.diff_textbox.configure(state="disabled")
            return

        # Check the type of the first item to ensure it's a tuple
        first_item = change_data['diff'][0]

        if not isinstance(first_item, tuple):
             self.diff_textbox.insert("end", "Error: Diff data is not in the expected tuple format.")
             self.diff_textbox.configure(state="disabled")
             return
             
        # --- Process the list of tuples ---
        # This translates your original code's logic into the new textbox
        for item in change_data['diff']:
            if not isinstance(item, tuple):
                self.diff_textbox.insert("end", f"Error: Invalid diff item: {item}\n", "del")
                continue

            try:
                operation, path, values = item
                
                # Add a header for *what* changed (e.g., PlayerStats.Health)
                # This matches your old logic.
                self.diff_textbox.insert("end", f"{path}\n", "context")
                
                if operation == "change":
                    old_val, new_val = values
                    # Show the old value, indented
                    self.diff_textbox.insert("end", f"  - {old_val}\n", "del")
                    # Show the new value, indented
                    self.diff_textbox.insert("end", f"  + {new_val}\n", "add")
                
                elif operation == "add":
                   # Show added value, indented
                   self.diff_textbox.insert("end", f"  + {values}\n", "add")
                
                elif operation == "remove":
                   # Show removed value, indented
                   self.diff_textbox.insert("end", f"  - {values}\n", "del")
                    
                else:
                    # Fallback for other operations
                    self.diff_textbox.insert("end", f"  {values}\n", "context")
                
                # Add a blank line for spacing between entries
                self.diff_textbox.insert("end", "\n", "context")
                    
            except Exception as e:
                # Catch malformed tuples
                self.diff_textbox.insert("end", f"Error processing tuple: {item} | {e}\n", "del")
        
        self.diff_textbox.configure(state="disabled") # Make read-only

    def mark_important_btn(self):
        pass

    def save_btn(self):
        pass

    def discard_btn(self):
        pass