import customtkinter as ctk
from Modules.error import BaseAppError
from Managers.AssetManager import AssetManager

class ErrorWindow(ctk.CTkToplevel):
    def __init__(self, *args, error: BaseAppError, asset_manager: AssetManager, **kwargs):
        super().__init__(*args, **kwargs)

        self.icon = asset_manager.get_icon(icon_name="danger_icon")
        self.base_err = error
        self.result = "close"  # Default result if window is 'X'ed out

        self.title("Error")
        self.geometry("480x280")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")

        # Configure grid layout
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Main Content
        self.grid_rowconfigure(2, weight=0)  # Footer
        self.grid_columnconfigure(0, weight=1)

        self.withdraw()  

        self._gui_header()
        self._gui_main()
        self._gui_footer()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.deiconify()  # Show the window
        self.grab_set()  # Block interaction with other windows
        if not self.base_err.app_close:
            self.wait_window()  # Halt execution until this window is destroyed

    def _gui_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=0)  
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_rowconfigure(0, weight=1)
        header_frame.grid_rowconfigure(1, weight=1)
        
        # Simple icon label - no background frame needed
        self.icon_label = ctk.CTkLabel(
            header_frame,
            text="",
            image=self.icon,
            fg_color="transparent"
        )
        self.icon_label.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 15), pady=0)
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text=self.base_err.title,
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            anchor="w",
            justify="left"  
        )
        self.title_label.grid(row=0, column=1, sticky="ew")
        
        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text=self.base_err.user_message,
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color="gray",
            anchor="w",
            justify="left"  
        )
        self.subtitle_label.grid(row=1, column=1, sticky="ew", pady=(0, 5))
        
        def update_wraplength(event):
            wrap_width = event.width - 5
            if wrap_width > 0:
                self.title_label.configure(wraplength=wrap_width)
                self.subtitle_label.configure(wraplength=wrap_width)
        
        self.subtitle_label.bind("<Configure>", update_wraplength)
        self.title_label.bind("<Configure>", update_wraplength)
        
    def _gui_main(self):
        main_frame = ctk.CTkFrame(self, fg_color="white")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(5, 0))
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        main_content = self.base_err.dev_message

        textbox = ctk.CTkTextbox(main_frame,fg_color="#eeeeee", activate_scrollbars=True, wrap="word")
        textbox.grid(row=0, column=0, sticky="nsew")

        textbox.insert("1.0", main_content)
        textbox.configure(state="disabled")  # Make it read-only

    def _gui_footer(self):
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 20))

        # Create a spacer column to push buttons to the right
        footer_frame.grid_columnconfigure(0, weight=1)
        footer_frame.grid_columnconfigure(1, weight=0)
        footer_frame.grid_columnconfigure(2, weight=0)

        # Close Button
        close_button = ctk.CTkButton(
            footer_frame,
            text="Close",
            command=self._on_close,
            fg_color="#D92626",  # Dark gray
            hover_color="#AD1F1F",
            text_color="white"
        )
        close_button.grid(row=0, column=1, sticky="e", padx=(0, 10))

    def _on_close(self):
        self.result = "close"
        self.grab_release()

        if self.base_err.app_close:
            # self.master refers to the root window (the main app)
            # Use .quit() or .destroy() depending on your app structure
            # .destroy() is usually safer for CTk
            self.master.destroy()
        else:
            # Only destroy this popup window
            self.destroy()