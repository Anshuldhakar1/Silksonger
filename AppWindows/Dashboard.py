import customtkinter as ctk
import os
import tkinter as tk

class Dashboard():
    def __init__(self,root):
        self.root = root

        self.root.grid_columnconfigure(0, weight=0, minsize=300) # Sidebar
        self.root.grid_columnconfigure(1, weight=1) # Main content
        self.root.grid_rowconfigure(0, weight=1) 

        self._gui_createSideBar()
        self._gui_createMain()

        self.root.fileHandler.set_callback(self.on_file_selected)
        self.dropdown_frame = None # Good, you already had this

    def get_filename(self, filepath):
        return os.path.basename(filepath)

    def on_file_selected(self, filepath):
        self.file_entry.delete(0, "end")
        self.file_entry.insert(0, self.get_filename(filepath))
        self.full_filepath = filepath  # Store the full path for later use

    def _gui_createSideBar(self):
        self.sidebar_frame = ctk.CTkFrame(self.root, width=300, corner_radius=0, fg_color="white")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Scrollable frame expands

        header_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="new", padx=20, pady=(10, 0))

        app_icon_label = ctk.CTkLabel(header_frame,
                                    text="",
                                    image=self.root.app_icon,
                                    anchor="w")
        app_icon_label.grid(row=0, rowspan=2, column=0, padx=(0, 12), pady=(0,13))

        text_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        text_container.grid(row=0, column=1, sticky="sw")

        self.title_label = ctk.CTkLabel(text_container, 
                                      text="File Monitor", 
                                      font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, sticky="w", pady=0)

        self.subtitle_label = ctk.CTkLabel(text_container, 
                                         text="Real-time file change tracker", 
                                         font=ctk.CTkFont(family="Helvetica", size=11),
                                         anchor="w",
                                         text_color="gray")
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(0,5))

        #### File browser

        self.file_entry_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.file_entry_frame.grid(row=2, column=0, sticky="nwe", padx=20, pady=(15,0))
        self.file_entry_frame.grid_columnconfigure(0, weight=1)

        self.file_entry = ctk.CTkEntry(self.file_entry_frame, 
                                     placeholder_text="C:\\...\\save.dat", 
                                     border_width=1,
                                     fg_color="white",
                                     border_color="#D2D2D2",
                                     font=ctk.CTkFont(family="Helvetica", size=12))
        self.file_entry.grid(row=0, column=0, sticky="we")

        self.history_button = ctk.CTkButton(self.file_entry_frame,
                                        text="",
                                        image=self.root.history_icon, 
                                        fg_color="#DEDEDE",
                                        hover_color="#DEDEDE",
                                        width=24,
                                        font=ctk.CTkFont(family="Helvetica", size=13),
                                        command=self.open_last_file)
        self.history_button.grid(row=0, column=1, sticky="w", padx=(5,0))

        self.browse_button = ctk.CTkButton(self.file_entry_frame,
                                         text="",
                                         image=self.root.browse_icon, 
                                         fg_color="#de0707",
                                         hover_color="#de0707",
                                         width=24,
                                         font=ctk.CTkFont(family="Helvetica", size=13),
                                         command=self.root.fileHandler.browse)
        
        self.browse_button.grid(row=0, column=2, sticky="w", padx=5)

    def _gui_createMain(self):
        pass

    def show_recent_files_menu(self, widget):
        if self.dropdown_frame:
            self.close_dropdown()
            return 
            
        recent_files = self.root.fileHandler.get_recent_files()
        if not recent_files:
            return
        
        dropdown_width = widget.winfo_width() 
            
        self.dropdown_frame = ctk.CTkFrame(
            self.root,
            fg_color="white",
            border_width=1,
            border_color="#D2D2D2",
            width=dropdown_width, 
            height=len(recent_files) * 32  
        )
        
        x = widget.winfo_rootx() - self.root.winfo_rootx()
        y = widget.winfo_rooty() - self.root.winfo_rooty() + widget.winfo_height() + 2 # Place *below*
        self.dropdown_frame.place(x=x, y=y)
        
        # Add recent files as buttons
        for i, filepath in enumerate(recent_files):
            btn = ctk.CTkButton(
                self.dropdown_frame,
                text=self.get_filename(filepath),
                fg_color="transparent",
                text_color="black",
                hover_color="#f0f0f0",
                anchor="w",
                height=30,
                width=dropdown_width - 2,  
                command=lambda f=filepath: self.select_recent_file(f)
            )
            btn.place(x=1, y=1 + (i * 31))

        self.dropdown_frame.bind("<FocusOut>", self.on_dropdown_focus_out)
        self.dropdown_frame.focus_set()

    def select_recent_file(self, filepath):
        self.on_file_selected(filepath)
        
    def open_last_file(self):
        recent_files = self.root.fileHandler.get_recent_files()
        if not recent_files:
            return

        menu = tk.Menu(self.root, tearoff=0)

        for filepath in recent_files:
            filename = self.get_filename(filepath)
            menu.add_command(
                label=filename,
                command=lambda f=filepath: self.select_recent_file(f)
            )

        widget = self.history_button
        x = widget.winfo_rootx() - 100
        y = widget.winfo_rooty() + widget.winfo_height() + 2 

        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def close_dropdown(self):
        """Destroys the dropdown frame if it exists."""
        if self.dropdown_frame:
            self.dropdown_frame.destroy()
            self.dropdown_frame = None

    def on_dropdown_focus_out(self, event):
        self.root.after(50, self._check_focus)

    def _check_focus(self):
        """Helper method to check focus after a short delay."""
        if not self.dropdown_frame:
            return # Frame was already closed

        new_focus_widget = self.root.focus_get()
        master = new_focus_widget
        while master:
            if master == self.dropdown_frame:
                return 
            master = getattr(master, 'master', None)
        self.close_dropdown()