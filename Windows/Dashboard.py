import customtkinter as ctk

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Managers.AppManager import AppManager

class DashboardWindow(ctk.CTk):
    def __init__(self, app_manager: 'AppManager'):

        self.app_manager = app_manager

        self.app_manager.grid_columnconfigure(0, weight=0, minsize=300) # Sidebar
        self.app_manager.grid_columnconfigure(1, weight=1) # Main content
        self.app_manager.grid_rowconfigure(0, weight=1) 

        self._gui_createSideBar()
        self._gui_createMain()
        
    def _gui_createSideBar(self):
        self.sidebar_frame = ctk.CTkFrame(self.app_manager, width=300, corner_radius=0, fg_color="white")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Scrollable frame expands

        header_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="new", padx=20, pady=(10, 0))

        app_icon_label = ctk.CTkLabel(header_frame,
                                    text="",
                                    image=self.app_manager.AssetManager.get_icon("app_icon"),
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
                                        image=self.app_manager.AssetManager.get_icon("history_icon"), 
                                        fg_color="#DEDEDE",
                                        hover_color="#DEDEDE",
                                        width=24,
                                        font=ctk.CTkFont(family="Helvetica", size=13),
                                        command=self.open_last_file)
        self.history_button.grid(row=0, column=1, sticky="w", padx=(5,0))

        self.browse_button = ctk.CTkButton(self.file_entry_frame,
                                         text="",
                                         image=self.app_manager.AssetManager.get_icon("browse_icon"), 
                                         fg_color="#de0707",
                                         hover_color="#de0707",
                                         width=24,
                                         font=ctk.CTkFont(family="Helvetica", size=13),
                                         command=self.browse)
        
        self.browse_button.grid(row=0, column=2, sticky="w", padx=5)

        divider = ctk.CTkFrame(self.sidebar_frame,
                            height=1, # the height here means nothing, the border makes it visible   
                            fg_color="#DEDEDE",
                            border_width=1)   

        # Use sticky="ew" to make it stretch horizontally (East-West)
        divider.grid(row=3, column=0, sticky="ew", pady=(10,0))

        self.change_logs_frame = ctk.CTkFrame(self.sidebar_frame, 
                                              fg_color="#F7F7F7",
                                              border_width=1,
                                              border_color="#e4e4e4")
        self.change_logs_frame.grid(row=4,column=0,sticky="nwes",padx=5,pady=5)
        self.change_logs_frame.grid_columnconfigure(0, weight=1)
        self.change_logs_frame.grid_columnconfigure(1, weight=1)
        self.change_logs_frame.grid_rowconfigure(1, weight=1)

        self.change_to_logs_btn = ctk.CTkButton(
            self.change_logs_frame,
            text="Change Logs",
            fg_color="#fee2e2",
            hover_color="#fee2e2",
            text_color="#801e1e",
            command=self.logs_btn_clicked
        )
        self.change_to_logs_btn.grid(row=0, column=0, padx=(5, 2), pady=5, sticky="ew")

        self.change_to_imp_btn = ctk.CTkButton(
            self.change_logs_frame,
            text="Important",
            fg_color="#EFEFEF",
            hover_color="#efefef",
            text_color="#838383",
            command=self.imp_btn_clicked
        )
        self.change_to_imp_btn.grid(row=0, column=1, padx=(2, 5), pady=5, sticky="ew")

        self.log_list_frame = ctk.CTkScrollableFrame(self.change_logs_frame,
                                                      fg_color="#F7F7F7",
                                                    #   fg_color="green"
                                                      )
        self.log_list_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=(0, 5))

    def _gui_createMain(self):
        self.main_frame = ctk.CTkFrame(self.app_manager, fg_color="white")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
        self.main_frame.grid_columnconfigure(0, weight=1)  # Changed from 3 to 0
        self.main_frame.grid_rowconfigure(1, weight=1)  # Textbox expands

        # New header frame with border
        self.monitoring_header = ctk.CTkFrame(self.main_frame, 
                                            fg_color="white", 
                                            border_width=1,
                                            border_color="#E5E7EB",
                                            corner_radius=8)
        self.monitoring_header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        self.monitoring_header.grid_columnconfigure(2, weight=1)  # Space between title and buttons

        # Move existing widgets to header frame
        self.main_title = ctk.CTkLabel(self.monitoring_header, 
                                     text="Monitoring Log", 
                                     font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
                                     text_color="black")
        self.main_title.grid(row=0, column=0, sticky="w", padx=(20,5), pady=15)

        self.status_indicator_label = ctk.CTkLabel(self.monitoring_header, 
                                                text="\u25cf Not Monitoring", 
                                                font=ctk.CTkFont(family="Helvetica",size=12, weight="bold"),
                                                text_color="#DC2626",
                                                corner_radius=8)
        self.status_indicator_label.grid(row=0, column=1, sticky="w", padx=(5,10), pady=15)
        
        # Right-side controls frame
        controls_frame = ctk.CTkFrame(self.monitoring_header, fg_color="transparent")
        controls_frame.grid(row=0, column=3, sticky="e", padx=20, pady=15)
        
        # Update start button (now a toggle)
        self.monitor_toggle_button = ctk.CTkButton(controls_frame, 
                                       text="",
                                       image=self.app_manager.AssetManager.get_icon("play_icon"),
                                       width=32,
                                       height=32,
                                    #    state="disabled",
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       fg_color="#b3b3b3", 
                                       hover_color="#b3b3b3",
                                       border_width=1,
                                       border_color="#c4c4c4",
                                       command=self.toggle_monitoring)
        self.monitor_toggle_button.grid(row=0, column=0, sticky="e", padx=5)
        # self.monitor_toggle_button.configure
        
        # Update stop button text and colors to indicate it's for releasing the file
        self.stop_button = ctk.CTkButton(controls_frame, 
                                      text="",
                                      image=self.app_manager.AssetManager.get_icon("pause_icon"),
                                      width=32,
                                      height=32,
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      fg_color="#DC2626",
                                      hover_color="#DC2626",
                                      command=self.release_file,
                                      state="disabled",
                                      )
        self.stop_button.grid(row=0, column=1, sticky="e", padx=5)

        # Main log area with slightly off-white background
        self.output_textbox = ctk.CTkTextbox(self.main_frame, 
                                          font=("Consolas", 13),
                                          corner_radius=8,
                                          fg_color="#F8FAFC",  # Slightly off-white
                                          text_color="black",
                                          border_width=1,
                                          border_color="#E5E7EB",
                                          state="disabled")
        self.output_textbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Configure tags for main log
        self.output_textbox._textbox.tag_configure("timestamp", foreground="gray")
        self.output_textbox._textbox.tag_configure("START", foreground="#059669", font=("Consolas", 13, "bold")) # Green
        self.output_textbox._textbox.tag_configure("STOP", foreground="#DC2626", font=("Consolas", 13, "bold")) # Red
        self.output_textbox._textbox.tag_configure("MODIFY", foreground="#D97706", font=("Consolas", 13, "bold")) # Amber
        self.output_textbox._textbox.tag_configure("SAVED", foreground="#D9B906", font=("Consolas", 13, "bold")) # Yellow
        self.output_textbox._textbox.tag_configure("SAVED_IMP", foreground="#7706D9", font=("Consolas", 13, "bold")) # Purple
        self.output_textbox._textbox.tag_configure("INFO", foreground="gray")
        self.output_textbox._textbox.tag_configure("ERROR", foreground="red")

    def open_last_file(self):
        pass

    def browse(self):
        pass

    def logs_btn_clicked(self):
        pass

    def imp_btn_clicked(self):
        pass

    def toggle_monitoring(self):
        pass

    def release_file(self):
        pass
