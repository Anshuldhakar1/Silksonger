import customtkinter as ctk

class Dashboard():
    def __init__(self,root):
        print("Created an instance of Dashboard")
        self.root = root

        self.root.grid_columnconfigure(0, weight=0, minsize=300) # Sidebar
        self.root.grid_columnconfigure(1, weight=1) # Main content
        self.root.grid_rowconfigure(0, weight=1) 

        self._gui_createSideBar()
        self._gui_createMain()

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
                                      font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
                                      anchor="w")
        self.title_label.grid(row=0, column=0, sticky="w", pady=0)

        self.subtitle_label = ctk.CTkLabel(text_container, 
                                         text="Real-time file change tracker", 
                                         font=ctk.CTkFont(family="Helvetica", size=11),
                                         anchor="w",
                                         text_color="gray")
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(0,5))

    def _gui_createMain(self):
        pass