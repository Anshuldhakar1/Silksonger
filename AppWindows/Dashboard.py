import datetime
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

        self.root.M_fileHandler.set_callback(self.on_file_selected)
        self.dropdown_frame = None

        self.main_log("Application started")
        self.add_simple_msg_to_log_entry("-------- Select a File to continue --------")

    def get_filename(self, filepath):
        return os.path.basename(filepath)

    def on_file_selected(self, filepath):
        self.file_entry.delete(0, "end")
        self.file_entry.insert(0, self.get_filename(filepath))
        self.full_filepath = filepath  
        self.root.M_monitor.set_target(filepath)

        self.main_log(f"Selected File {self.get_filename(filepath)}", "MODIFY")

        self.enable_monitor_btn(True)
        self.enable_stop_btn(True)

        self.clear_log_entries()
        if self.root.M_monitor.is_target_set:
            self.logs = self.root.M_fileHandler.get_logs(self.root.M_monitor.get_target())
            self.root.load_logs(self.logs)
            self.load_normal_logs()

    def load_normal_logs(self):
        # print(self.logs[0]["adasdasdasd"])
        for log_key in self.logs[0].keys():
            log = self.logs[0][log_key]
            timestamp = log['timestamp'][-8:]
            num_diffs = len(log['diff'])
            self.add_log_entry(
                timestamp=timestamp,
                main_text=log_key, 
                sub_text=f"{num_diffs} changes detected",
                log_id=log_key
            )
        pass
        
    def toggle_monitoring(self):  # means that the user pressed the play/pause btn
        if self.root.M_monitor.is_target_set:
            if not self.root.M_monitor.is_monitoring:
                self.status_indicator_label.configure(text="\u25cf Monitoring Active", text_color="#059669")
                self.root.M_monitor.start_monitoring()
                # self.main_log(f"Started to monitor {self.get_filename(self.full_filepath)}", "START")
            else:
                self.status_indicator_label.configure(text="\u25cf Not Monitoring", text_color="#DC2626")
                self.main_log(f"Stopped monitoring {self.get_filename(self.full_filepath)}", "STOP")
                self.root.M_monitor.stop_monitoring()
        else:
            self.main_log("No File Selected!!", "ERROR")

        # implement logic for monirtoring activation

    def release_file(self):
        if self.root.M_monitor.is_target_set:
            if self.root.M_monitor.is_monitoring:
                self.toggle_monitoring()
            self.root.M_monitor.release_target()

            self.enable_monitor_btn(False)
            self.enable_stop_btn(False)

            self.main_log(f"Released File {self.get_filename(self.full_filepath)}", "MODIFY")

            self.file_entry.delete(0, "end")
            self.file_entry.configure(placeholder_text="C:\\...\\save.dat")
        else:
            self.main_log("No File Selected!!", "ERROR")

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
                                         command=self.root.M_fileHandler.browse)
        
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
            # font=ctk.CTkFont(weight="bold"),
        )
        # self.change_to_logs_btn.pack(padx=5,pady=(5,0))
        # self.change_to_logs_btn.pack(padx=5,pady=(5,0),expand=True,side="left",fill="x")
        self.change_to_logs_btn.grid(row=0, column=0, padx=(5, 2), pady=5, sticky="ew")

        self.change_to_imp_btn = ctk.CTkButton(
            self.change_logs_frame,
            text="Important",
            fg_color="#EFEFEF",
            hover_color="#efefef",
            text_color="#838383"
        )
        self.change_to_imp_btn.grid(row=0, column=1, padx=(2, 5), pady=5, sticky="ew")

        self.log_list_frame = ctk.CTkScrollableFrame(self.change_logs_frame,
                                                      fg_color="#F7F7F7",
                                                    #   fg_color="green"
                                                      )
        self.log_list_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=(0, 5))

        # self.add_log_entry2(
        #     timestamp="14:35:18",
        #     main_text="save.dat modified",
        #     sub_text="Size changed to 1.1MB",
        #     log_id="log_001" # A unique ID for this log
        # )

        # self.add_log_entry(
        #     timestamp="14:35:18",
        #     main_text="save.dat modified",
        #     sub_text="Size changed to 1.1MB",
        #     log_id="log_001" # A unique ID for this log
        # )

        # self.add_log_entry(
        #     timestamp="14:35:18",
        #     main_text="save.dat modified",
        #     sub_text="Size changed to 1.1MB",
        #     log_id="log_002" # A unique ID for this log
        # )

    def add_simple_msg_to_log_entry(self, msg):
        NORMAL_BG = "transparent"
        entry_frame = ctk.CTkFrame(self.log_list_frame, 
                                   fg_color=NORMAL_BG, 
                                   height=70) 
        entry_frame.pack(fill="x", pady=(5, 0), padx=5)

        label = ctk.CTkLabel(entry_frame,
            text=msg,
            text_color="#949494",
        )
        label.pack(padx=5, pady=5)

    def clear_log_entries(self):
        for widget in self.log_list_frame.winfo_children():
            widget.destroy()

    def add_log_entry(self, timestamp, main_text, sub_text, log_id):
        small_font = ctk.CTkFont(family="Helvetica", size=11, weight="normal")
        main_font = ctk.CTkFont(family="Helvetica", size=13, weight="bold")
        NORMAL_BG = "#EFEFEF"
        HOVER_BG = "#E5E5E5"

        entry_frame = ctk.CTkFrame(self.log_list_frame, 
                                   fg_color=NORMAL_BG, 
                                   cursor="hand2",
                                   height=70) 
        entry_frame.pack(fill="x", pady=(5, 0), padx=5)
        # Stop pack from shrinking the frame
        entry_frame.pack_propagate(False) 
        # vertical line
        v_line = ctk.CTkFrame(entry_frame, 
                              width=3, 
                              fg_color="#C8C8C8", 
                              corner_radius=2)
        v_line.pack(side="left", fill="y", padx=(5, 10), pady=10)

        # 3. Create an encompassing frame for the text
        text_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, pady=2, padx=(0, 5))

        timestamp_label = ctk.CTkLabel(text_frame, text=timestamp,
                                       font=small_font, text_color="gray",
                                       anchor="w")
        timestamp_label.place(x=0, y=0) 

        main_label = ctk.CTkLabel(text_frame, text=main_text,
                                  font=main_font, text_color="black",
                                  anchor="w")
        main_label.place(x=0, y=18) 

        sub_label = ctk.CTkLabel(text_frame, text=sub_text,
                                 font=small_font, text_color="gray",
                                 anchor="w")
        sub_label.place(x=0, y=40)

        def _on_click(event):
            self._on_log_entry_click(log_id) 

        def _on_enter(event):
            entry_frame.configure(fg_color=HOVER_BG) 
            text_frame.configure(fg_color=HOVER_BG) 
            
        def _on_leave(event):
            entry_frame.configure(fg_color=NORMAL_BG)
            text_frame.configure(fg_color=NORMAL_BG)

        # Bind functions
        widgets_to_bind = [entry_frame, v_line, text_frame, timestamp_label, main_label, sub_label]
        for widget in widgets_to_bind:
            widget.bind("<Button-1>", _on_click)
            widget.bind("<Enter>", _on_enter)
            widget.bind("<Leave>", _on_leave)

    # Add this placeholder function to handle the click event
    def _on_log_entry_click(self, log_id):
        print(f"Clicked log entry! ID: {log_id}")
        self.clear_log_entries()
        # You can add your logic here, e.g., show details for this log

    def _gui_createMain(self):
        self.main_frame = ctk.CTkFrame(self.root, fg_color="white")
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
                                       image=self.root.play_icon,
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
                                      image=self.root.pause_icon,
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

    def show_recent_files_menu(self, widget):
        if self.dropdown_frame:
            self.close_dropdown()
            return 
            
        recent_files = self.root.M_fileHandler.get_recent_files()
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
        recent_files = self.root.M_fileHandler.get_recent_files()
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

    def main_log(self, message: str, tag: str = None):
        """Helper function to add a message to the main output textbox."""
        self.output_textbox.configure(state="normal")
        
        timestamp = f"{datetime.datetime.now():%H:%M:%S} "
        self.output_textbox.insert("end", timestamp, "timestamp")
        
        if tag:
            self.output_textbox.insert("end", f"{tag:8} ", tag) # 8 chars padding
        
        self.output_textbox.insert("end", f"{message}\n")
        self.output_textbox.see("end")
        self.output_textbox.configure(state="disabled")

    def enable_monitor_btn(self, state: bool):
        if state:
            self.monitor_toggle_button.configure(
                state="normal",
                fg_color="#dedede",      
                hover_color="#d1d1d1"    
            )
        else:
            self.monitor_toggle_button.configure(
                state="disabled",
                fg_color="#bdbdbd",      
                hover_color="#bdbdbd"    
            )

    def enable_stop_btn(self, state: bool):
        if state:
            self.stop_button.configure(
                state="normal",
                fg_color="#EF4444",      
            )
        else:
            self.stop_button.configure(
                state="disabled",
                fg_color="#DC2626",      
            )
