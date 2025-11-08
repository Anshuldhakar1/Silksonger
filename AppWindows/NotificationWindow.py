import customtkinter as ctk

class NotificationWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("Change Detected")
        self.geometry("600x400")
        
        # Center the window
        self.update_idletasks()
        # Configure rows
        self.grid_rowconfigure(0, weight=0)  # row 0 fixed height for full-width
        self.grid_rowconfigure(1, weight=1)  # row 1 expands vertically
        
        # Configure columns for row 1
        self.grid_columnconfigure(0, weight=1)    # first part expands horizontally
        self.grid_columnconfigure(1, weight=0, minsize=200)  # second part fixed width
        
        # Full width label in row 0 (spanning 2 columns)
        full_width_label = ctk.CTkLabel(self, text="Full Width Row", fg_color="#cccccc", height=30)
        full_width_label.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Left expanding frame in row 1, column 0
        left_frame = ctk.CTkFrame(self, fg_color="#eeeeee", border_width=1, border_color="#888888")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(5,2), pady=5)
        
        # Right fixed frame in row 1, column 1 (300px wide)
        right_frame = ctk.CTkFrame(self, fg_color="#dddddd", width=200, border_width=1, border_color="#888888")
        right_frame.grid(row=1, column=1, sticky="ns", padx=(2,5), pady=5)
        
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        self.attributes('-topmost', True)  # Keep window on top
        self.lift()  # Lift window to top
