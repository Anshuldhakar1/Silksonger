from datetime import datetime
import traceback
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from typing import TYPE_CHECKING, Optional
import os

from Modules.error import DashboardError

if TYPE_CHECKING:
    from Managers.AppManager import AppManager

class DashboardWindow(ctk.CTk):
    def __init__(self, app_manager: 'AppManager'):

        self.app_manager = app_manager

        self.app_manager.grid_columnconfigure(0, weight=0, minsize=300) # Sidebar
        self.app_manager.grid_columnconfigure(1, weight=1) # Main content
        self.app_manager.grid_rowconfigure(0, weight=1) 

        self.selected_file_path: Optional[str] = None

        self._gui_createSideBar()
        self._gui_createMain()
        
        self.main_log("Application started")
        self.add_simple_msg_to_log_entry("-------- Select a File to continue --------")
      
    # ------------------ GUI ------------------  
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
                                              fg_color="#FFFFFF",
                                            #   border_width=1,
                                            #   border_color="#e4e4e4"
                                              )
        self.change_logs_frame.grid(row=4,column=0,sticky="nwes",padx=5,pady=5)
        self.change_logs_frame.grid_columnconfigure(0, weight=1)
        self.change_logs_frame.grid_columnconfigure(1, weight=1)
        self.change_logs_frame.grid_rowconfigure(1, weight=1)

        self.change_to_logs_btn = ctk.CTkButton(
            self.change_logs_frame,
            text="Change Logs",
            fg_color="#fee2e2",
            hover_color="#f6dada",
            text_color="#801e1e",
            border_width=1,
            border_color="#612a2a",
            command=self.logs_btn_clicked
        )
        self.change_to_logs_btn.grid(row=0, column=0, padx=(5, 2), pady=5, sticky="ew")

        self.change_to_imp_btn = ctk.CTkButton(
            self.change_logs_frame,
            text="Important",
            fg_color="#EFEFEF",
            hover_color="#e3e3e3",
            text_color="#838383",
            border_width=1,
            border_color="#B1B1B1",
            command=self.imp_btn_clicked
        )
        self.change_to_imp_btn.grid(row=0, column=1, padx=(2, 5), pady=5, sticky="ew")

        self.log_list_frame = ctk.CTkScrollableFrame(self.change_logs_frame,
                                                      fg_color="#FFFFFF",
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

    # ------------------ main app ------------------  
    def main_log(self, message: str, tag: str = None):
        """Helper function to add a message to the main output textbox."""
        self.output_textbox.configure(state="normal")
        
        timestamp = f"{datetime.now():%H:%M:%S} "
        self.output_textbox.insert("end", timestamp, "timestamp")
        
        if tag:
            self.output_textbox.insert("end", f"{tag:8} ", tag) # 8 chars padding
        
        self.output_textbox.insert("end", f"{message}\n")
        self.output_textbox.see("end")
        self.output_textbox.configure(state="disabled")

    def on_file_selected(self, filepath: str):
        
        try:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, os.path.basename(filepath))

            self.selected_file_path = filepath
            self.app_manager.file_selected(filepath)
            self.app_manager.FileManager.file_selected(filepath)

            self.set_monitor_btn_state(True)
            self.set_stop_btn_state(True)
            
            self.main_log(f"Selected File {os.path.basename(filepath)}", "MODIFY")
            self.show_normal_changes()
        except Exception as e:
            traceback.print_exc()
            self.app_manager._error_popup(DashboardError(str(e)))

    def status_set_not_monitoring(self):
        self.status_indicator_label.configure(text="\u25cf Not Monitoring", text_color="#DC2626")
    
    def status_set_monitoring(self):
        self.status_indicator_label.configure(text="\u25cf Monitoring Active", text_color="#059669")

    def release_file(self):
        try:
            self.status_set_not_monitoring()
            if self.selected_file_path:
            
                if self.app_manager.Monitor.is_monitoring:
                    self.app_manager.Monitor.stop_monitoring()

                # after file release the logs tab button should be selected
                self.change_to_imp_btn.configure(
                    fg_color="#EFEFEF",
                    hover_color="#efefef",
                    text_color="#838383",
                )
                self.change_to_logs_btn.configure(
                    fg_color="#fee2e2",
                    hover_color="#fee2e2",
                    text_color="#801e1e",
                )

                self.set_monitor_btn_state(False)
                self.set_stop_btn_state(False)

                self.clear_log_entries()
                self.main_log(f"Released File {os.path.basename(self.selected_file_path)}", "MODIFY")
                
                self.selected_file_path = None
                self.app_manager.Monitor.release_target()

                self.file_entry.delete(0, "end")
                self.file_entry.configure(placeholder_text="C:\\...\\save.dat")
                self.add_simple_msg_to_log_entry("-------- Select a File to continue --------")
            else:
                self.main_log("No File Selected!!", "ERROR")
        except Exception as e:
            traceback.print_exc()
            self.app_manager._error_popup(DashboardError(f"Failed to release file: {e}"))
    
    # ------------------ Sidebar LOGS ------------------
    def add_log_entry(self, timestamp:str, main_text:str, sub_text:str, is_imp:bool=False):
        small_font = ctk.CTkFont(family="Helvetica", size=11, weight="normal")
        main_font = ctk.CTkFont(family="Helvetica", size=13, weight="bold")
        # NORMAL_BG = "#EFEFEF"
        # HOVER_BG = "#E5E5E5"
        NORMAL_BG = "#ffffff"
        HOVER_BG = "#EFEFEF"

        entry_frame = ctk.CTkFrame(self.log_list_frame, 
                                   fg_color=NORMAL_BG, 
                                   cursor="hand2",
                                   border_width=2,
                                   border_color="#BEBEBE",
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

        original_format = "%Y-%m-%d %H:%M:%S"
        new_format = "%d-%m-%y | %I:%M:%S %p"

        dt_object = datetime.strptime(timestamp, original_format)
        converted_timestamp = dt_object.strftime(new_format)

        timestamp_label = ctk.CTkLabel(text_frame, text=converted_timestamp,
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

        # --- THIS IS THE MODIFIED SECTION ---
    
        existing_entries = self.log_list_frame.pack_slaves()

        if existing_entries:
            # If the list is not empty, pack the new frame BEFORE the first (top) widget
            first_entry = existing_entries[0]
            entry_frame.pack(fill="x", pady=(5, 0), padx=5, before=first_entry)
        else:
            # If the list is empty, just pack it normally
            entry_frame.pack(fill="x", pady=(5, 0), padx=5)

        def _on_click(event):
            self._on_log_entry_click(main_text, is_imp=is_imp) 

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

    def _on_log_entry_click(self, note: str, is_imp:bool):
        self.app_manager.show_change(note=note, is_imp=is_imp)
        # self.app_manager.notifwindow_test()

    def clear_log_entries(self):
        for widget in self.log_list_frame.winfo_children():
            widget.destroy()

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

    def show_normal_changes(self):
        if not self.selected_file_path:
            return
        self.clear_log_entries()    

        if not self.app_manager.changes["normal"]:
            self.add_simple_msg_to_log_entry("-------- No Changes Saved --------")
            return

        for log_key in self.app_manager.changes["normal"].keys():
            log = self.app_manager.changes["normal"][log_key]
            timestamp = log['timestamp']
            num_diffs = len(log['diff'])
            self.add_log_entry(
                timestamp=timestamp,
                main_text=log_key, 
                sub_text=f"{num_diffs} changes detected",
                is_imp=False
            )   

    def show_imp_changes(self):
        if not self.selected_file_path:
            return
        self.clear_log_entries()  

        if not self.app_manager.changes["important"]:
            self.add_simple_msg_to_log_entry("-------- No Changes Saved --------")
            return

        for log_key in self.app_manager.changes["important"].keys():
            log = self.app_manager.changes["important"][log_key]
            timestamp = log['timestamp']
            num_diffs = len(log['diff'])
            self.add_log_entry(
                timestamp=timestamp,
                main_text=log_key, 
                sub_text=f"{num_diffs} changes detected",
                is_imp=True
            )                        

    # ------------------ File browsing  ------------------ 
    def show_recent_files_menu(self, widget):
        if self.dropdown_frame:
            self.close_dropdown()
            return 
            
        recent_files = self.app_manager.FileManager.get_recent_files()
        if not recent_files:
            return
        
        dropdown_width = widget.winfo_width() 
            
        self.dropdown_frame = ctk.CTkFrame(
            self.app_manager,
            fg_color="white",
            border_width=1,
            border_color="#D2D2D2",
            width=dropdown_width, 
            height=len(recent_files) * 32  
        )
        
        x = widget.winfo_rootx() - self.app_manager.winfo_rootx()
        y = widget.winfo_rooty() - self.app_manager.winfo_rooty() + widget.winfo_height() + 2 # Place *below*
        self.dropdown_frame.place(x=x, y=y)
        
        # Add recent files as buttons
        import os
        for i, filepath in enumerate(recent_files):
            btn = ctk.CTkButton(
                self.dropdown_frame,
                text=os.path.basename(filepath),
                fg_color="transparent",
                text_color="black",
                hover_color="#f0f0f0",
                anchor="w",
                height=30,
                width=dropdown_width - 2,  
                command=lambda f=filepath: self.on_file_selected(f)
            )
            btn.place(x=1, y=1 + (i * 31))

        self.dropdown_frame.bind("<FocusOut>", self.on_dropdown_focus_out)
        self.dropdown_frame.focus_set()
    
    def close_dropdown(self):
        if self.dropdown_frame:
            self.dropdown_frame.destroy()
            self.dropdown_frame = None

    def on_dropdown_focus_out(self, event):
        self.app_manager.after(50, self._check_focus)

    def _check_focus(self):
        if not self.dropdown_frame:
            return 

        new_focus_widget = self.app_manager.focus_get()
        master = new_focus_widget
        while master:
            if master == self.dropdown_frame:
                return 
            master = getattr(master, 'master', None)
        self.close_dropdown()

    def open_last_file(self):
        if self.selected_file_path:  # do not open recents if a file is selected
            return   # todo add code to stop monitoring and stopping it, then opening this new file
        
        try:
            recent_files = self.app_manager.FileManager.get_recent_files()

            menu = tk.Menu(self.app_manager, tearoff=0)

            for filepath in recent_files:
                filename = os.path.basename(filepath)
                menu.add_command(
                    label=filename,
                    command=lambda f=filepath: self.on_file_selected(f)
                )

            widget = self.history_button 
            x = widget.winfo_rootx() - 100
            y = widget.winfo_rooty() + widget.winfo_height() + 2 

            menu.tk_popup(x, y)
        except Exception as e:
            traceback.print_exc()
            self.app_manager._error_popup(DashboardError(f"Failed to open recent files menu: {e}"))
        finally:
            try:
                menu.grab_release()
            except: pass

    def browse(self):
        try:
            filepath = filedialog.askopenfilename(
                initialdir=self.app_manager.FileManager.target_directory,
                title="Select Save File",
                filetypes=[("DAT files", "*.dat"), ("All files", "*.*")]
            )
            if filepath:
                self.app_manager.FileManager.file_selected(filepath)
                self.on_file_selected(filepath)
        except Exception as e:
            traceback.print_exc()
            self.app_manager._error_popup(DashboardError(f"Browser error: {e}"))

    # ------------------ Buttons  ------------------ 
    def set_monitor_btn_state(self, state: bool):
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

    def set_stop_btn_state(self, state: bool):
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

    def logs_btn_clicked(self):
        if not self.selected_file_path:
            return

        self.change_to_imp_btn.configure(
            fg_color="#EFEFEF",
            hover_color="#efefef",
            text_color="#838383",
            border_color="#B1B1B1",
        )
        self.change_to_logs_btn.configure(
            fg_color="#fee2e2",
            hover_color="#fee2e2",
            text_color="#801e1e",
            border_color="#612a2a",
        )

        self.show_normal_changes()

    def imp_btn_clicked(self):
        if not self.selected_file_path:
            return

        self.change_to_logs_btn.configure(
            fg_color="#EFEFEF",
            hover_color="#efefef",
            text_color="#838383",
            border_color="#B1B1B1",
        )
        self.change_to_imp_btn.configure(
            fg_color="#fee2e2",
            hover_color="#fee2e2",
            text_color="#801e1e",
            border_color="#612a2a",   
        )

        self.show_imp_changes()

    def toggle_monitoring(self):
        try:
            if not self.selected_file_path:
                return

            if not self.app_manager.Monitor.is_monitoring:
                self.app_manager.Monitor.start_monitoring()
                self.status_set_monitoring()
                self.main_log(f"Started monitoring {os.path.basename(self.selected_file_path)}", "START")
                self.main_log("Waiting for changes ...", "INFO")
            else:
                self.app_manager.Monitor.stop_monitoring()
                self.status_set_not_monitoring()
        except Exception as e:
            traceback.print_exc()
            self.app_manager._error_popup(DashboardError(f"Monitoring toggle failed: {e}"))
