import customtkinter as ctk
from tkinter import filedialog
from PIL import Image  # Add this import
import os
import json
import datetime
import time
import dictdiffer  # For comparing dictionaries
from SaveDecoder import decrypt_hollow_knight_save

class FileChangeWindow(ctk.CTkToplevel):
    def __init__(self, app_instance, filepath: str, change_data: dict, diff_data: list):
        super().__init__(app_instance)
        
        self.app = app_instance  # Reference to the main App
        self.filepath = filepath
        self.change_data = change_data
        self.diff_data = diff_data # The real diff
        
        self.title("File Change Detected")
        self.geometry("800x600")

        # --- Configure to be on top ---
        self.lift()  # Bring to front
        self.attributes("-topmost", True)  # Keep on top
        self.grab_set()  # Make window modal (user must interact with this first)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0, minsize=250) # Notes column
        self.grid_rowconfigure(2, weight=1) # Diff textbox expands

        # --- Header ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)

        filename = os.path.basename(filepath)
        timestamp = self.change_data.get('timestamp', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        title_label = ctk.CTkLabel(header_frame, 
                                   text=f"File Change: {filename}", 
                                   font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
                                   anchor="w")
        title_label.grid(row=0, column=0, sticky="w")
        
        timestamp_label = ctk.CTkLabel(header_frame, 
                                       text=f"Modified at {timestamp}", 
                                       font=ctk.CTkFont(family="Helvetica", size=12),
                                       text_color="gray",
                                       anchor="w")
        timestamp_label.grid(row=1, column=0, sticky="w")
        
        close_button = ctk.CTkButton(header_frame, 
                                     text="X", 
                                     width=30, 
                                     height=30,
                                     command=self.close_window,
                                     fg_color="transparent",
                                     text_color="gray",
                                     hover_color="#EEE")
        close_button.grid(row=0, column=1, rowspan=2, sticky="e")
        
        # --- File Path ---
        path_label = ctk.CTkLabel(self, 
                                  text=f"Changes in {filepath}", 
                                  font=ctk.CTkFont(family="Helvetica", size=12),
                                  text_color="gray",
                                  anchor="w")
        path_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=5)
        
        # --- Diff Textbox ---
        self.diff_textbox = ctk.CTkTextbox(self, 
                                           font=("Consolas", 13), 
                                           corner_radius=8,
                                           wrap="none")
        self.diff_textbox.grid(row=2, column=0, sticky="nsew", padx=(20, 10), pady=(5, 20))
        
        # Configure tags for colors
        self.diff_textbox._textbox.tag_configure("add", foreground="#16A34A", background="#D1FAE5")
        self.diff_textbox._textbox.tag_configure("remove", foreground="#DC2626", background="#FEE2E2")
        self.diff_textbox._textbox.tag_configure("line_num", foreground="gray")
        self.diff_textbox._textbox.tag_configure("path", foreground="#000000", font=("Consolas", 13, "bold"))
        
        self.populate_diff()
        self.diff_textbox.configure(state="disabled")

        # --- Notes & Actions (Right Column) ---
        notes_frame = ctk.CTkFrame(self, fg_color="transparent")
        notes_frame.grid(row=2, column=1, sticky="nsew", padx=(0, 20), pady=(5, 20))
        notes_frame.grid_rowconfigure(1, weight=1)
        
        notes_label = ctk.CTkLabel(notes_frame, 
                                   text="Notes", 
                                   font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                                   anchor="w")
        notes_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.notes_textbox = ctk.CTkTextbox(notes_frame, 
                                            font=ctk.CTkFont(family="Helvetica", size=13),
                                            corner_radius=8,
                                            height=150)
        self.notes_textbox.grid(row=1, column=0, sticky="new", pady=5)
        self.notes_textbox.insert("0.0", "Add a note about this change...")
        
        self.important_button = ctk.CTkButton(notes_frame, 
                                              text="Mark as Important", 
                                              font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                                              fg_color="#EF4444",
                                              hover_color="#DC2626",
                                              command=self.mark_as_important)
        self.important_button.grid(row=2, column=0, sticky="ew", pady=10)
        
        self.save_button = ctk.CTkButton(notes_frame, 
                                         text="Save Change", 
                                         font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                                         fg_color="transparent",
                                         border_width=1,
                                         border_color="gray",
                                         command=self.save_with_note)
        self.save_button.grid(row=3, column=0, sticky="ew", pady=5)

        self.discard_button = ctk.CTkButton(notes_frame, 
                                            text="Discard Change with Note", 
                                            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                                            fg_color="transparent",
                                            border_width=1,
                                            border_color="gray",
                                            command=self.save_with_note) # For now, same as save
        self.discard_button.grid(row=4, column=0, sticky="ew", pady=(5, 0))

    def populate_diff(self):
        """Inserts the real diff data into the textbox with color."""
        self.diff_textbox.configure(state="normal")
        self.diff_textbox.delete("0.0", "end") # Clear any old text
        
        if not self.diff_data:
            self.diff_textbox.insert("end", "No differences found or diff data is empty.")
            self.diff_textbox.configure(state="disabled")
            return
            
        line_num = 1
        for diff_type, path, changes in self.diff_data:
            path_str = ".".join(str(p) for p in path) if path else "root"
            
            if diff_type == 'change':
                old_val, new_val = changes
                self.diff_textbox.insert("end", f"{line_num:<3} ", "line_num")
                self.diff_textbox.insert("end", f"[CHANGE] at {path_str}\n", "path")
                self.diff_textbox.insert("end", f"{line_num+1:<3} ", "line_num")
                self.diff_textbox.insert("end", f"- {old_val}\n", "remove")
                self.diff_textbox.insert("end", f"{line_num+2:<3} ", "line_num")
                self.diff_textbox.insert("end", f"+ {new_val}\n", "add")
                line_num += 3
            elif diff_type == 'add':
                for key, value in changes:
                    self.diff_textbox.insert("end", f"{line_num:<3} ", "line_num")
                    self.diff_textbox.insert("end", f"[ADD] at {path_str}\n", "path")
                    self.diff_textbox.insert("end", f"{line_num+1:<3} ", "line_num")
                    self.diff_textbox.insert("end", f"+ {key}: {value}\n", "add")
                    line_num += 2
            elif diff_type == 'remove':
                for key, value in changes:
                    self.diff_textbox.insert("end", f"{line_num:<3} ", "line_num")
                    self.diff_textbox.insert("end", f"[REMOVE] at {path_str}\n", "path")
                    self.diff_textbox.insert("end", f"{line_num+1:<3} ", "line_num")
                    self.diff_textbox.insert("end", f"- {key}: {value}\n", "remove")
                    line_num += 2
            
            self.diff_textbox.insert("end", "\n")
            line_num += 1

        self.diff_textbox.configure(state="disabled")

    def get_note(self):
        note = self.notes_textbox.get("0.0", "end").strip()
        return note if note != "Add a note about this change..." else ""

    def mark_as_important(self):
        note = self.get_note()
        self.app.mark_as_important(self.filepath, self.change_data, note)
        self.close_window()

    def save_with_note(self):
        note = self.get_note()
        if not note:
             # You could add a small label here asking for a note
             print("Please add a note before saving.")
             return
        self.app.save_with_note(self.filepath, self.change_data, note)
        self.close_window()

    def close_window(self):
        self.grab_release()
        self.destroy()


class App(ctk.CTk):
    """
    Main application class, based on the 'dashboard.png' layout.
    """
    def __init__(self):
        super().__init__()
        
        # Update app icon size
        self.app_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/app_icon.png"),
            dark_image=Image.open("assets/icons/app_icon.png"),
            size=(48, 48)  # Slightly smaller to match the design
        )
        self.play_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/pause-play.png"),
            dark_image=Image.open("assets/icons/pause-play.png"),
            size=(16, 16)
        )
        self.pause_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/end.png"),
            dark_image=Image.open("assets/icons/end.png"),
            size=(16, 16)
        )
        self.browse_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/folder.png"),
            dark_image=Image.open("assets/icons/folder.png"),
            size=(16,16)
        )
        self.history_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/history.png"),
            dark_image=Image.open("assets/icons/history.png"),
            size=(16,16)
        )
        self.change_log_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/document.png"),
            dark_image=Image.open("assets/icons/document.png"),
            size=(16,16)
        )
        self.star_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/star.png"),
            dark_image=Image.open("assets/icons/star.png"),
            size=(16,16)
        )

        # --- Data Storage Setup ---
        self.data_dir = ".file_monitor_data"
        self.recent_files_path = os.path.join(self.data_dir, "recent_files.json")
        self.important_changes_path = os.path.join(self.data_dir, "important_changes.json")
        self.saved_notes_path = os.path.join(self.data_dir, "saved_notes.json")
        
        self.recent_files_list = []
        self.important_changes = {} # {"filepath": [data1, data2]}
        self.saved_notes = {}       # {"filepath": [data1, data2]}
        
        self.monitoring_active = False # Flag to control monitoring loop
        self.previous_data = {} # Stores the last known file state
        
        self.init_data_storage()
        
        # Remove current_change_events
        # self.current_change_events = [] # No longer needed
        
        # Add timestamp formatting helper
        self.format_timestamp = lambda ts: datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        
        self.initWindow()

    def init_data_storage(self):
        """Creates data directory and loads existing data from JSON files."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Load Recent Files
            if os.path.exists(self.recent_files_path):
                with open(self.recent_files_path, 'r') as f:
                    self.recent_files_list = json.load(f)
            
            # Load Important Changes
            if os.path.exists(self.important_changes_path):
                with open(self.important_changes_path, 'r') as f:
                    self.important_changes = json.load(f)

            # Load Saved Notes
            if os.path.exists(self.saved_notes_path):
                with open(self.saved_notes_path, 'r') as f:
                    self.saved_notes = json.load(f)
                    
        except Exception as e:
            print(f"Error initializing data storage: {e}")

    # --- Data Saving Methods ---

    def save_json_data(self, filepath, data):
        """Helper to save data to a JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving data to {filepath}: {e}")

    def save_recent_files(self, new_filepath):
        """Saves only the last used file."""
        self.recent_files_list = [new_filepath]  # Keep only the newest file
        self.save_json_data(self.recent_files_path, self.recent_files_list)

    def mark_as_important(self, filepath, change_data, note):
        """Saves a change record as 'important'."""
        if filepath not in self.important_changes:
            self.important_changes[filepath] = []
        
        entry = {"change_data": change_data, "note": note, "timestamp": time.time()}
        self.important_changes[filepath].append(entry)
        self.save_json_data(self.important_changes_path, self.important_changes)
        self.log_message(f"Marked change as important. Note: {note}", "INFO")
        self.add_recent_event(f"{os.path.basename(filepath)} marked important", "IMPORTANT", entry)
        self.show_change_log() # Refresh sidebar

    def save_with_note(self, filepath, change_data, note):
        """Saves a change record with a user note."""
        if filepath not in self.saved_notes:
            self.saved_notes[filepath] = []

        entry = {"change_data": change_data, "note": note, "timestamp": time.time()}
        self.saved_notes[filepath].append(entry)
        self.save_json_data(self.saved_notes_path, self.saved_notes)
        self.log_message(f"Saved change with note: {note}", "INFO")
        self.add_recent_event(f"Saved note for {os.path.basename(filepath)}", "INFO", entry)

    # --- UI Initialization ---

    def initWindow(self):
        """
        Set up the main window's properties and initialize widgets.
        """
        self.title("File Monitor")
        self.geometry("1100x700")

        self.grid_columnconfigure(0, weight=0, minsize=300) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Main content
        self.grid_rowconfigure(0, weight=1) 

        # --- Create Sidebar Frame ---
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="white")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Scrollable frame expands

        # Create a header frame with better spacing
        header_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="new", padx=20, pady=(10, 0))
        
        # App icon on the left
        app_icon_label = ctk.CTkLabel(header_frame,
                                    text="",
                                    image=self.app_icon,
                                    anchor="w")
        app_icon_label.grid(row=0, rowspan=2, column=0, padx=(0, 12), pady=(0,13))

        # Title container for text only
        text_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        text_container.grid(row=0, column=1, sticky="sw")

        # Title and subtitle in text container
        self.title_label = ctk.CTkLabel(text_container, 
                                      text="File Monitor", 
                                      font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
                                      anchor="w")
        self.title_label.grid(row=0, column=0, sticky="w")

        self.subtitle_label = ctk.CTkLabel(text_container, 
                                         text="Real-time file change tracker", 
                                         font=ctk.CTkFont(family="Helvetica", size=13),
                                         anchor="w",
                                         text_color="gray")
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        self.file_entry_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.file_entry_frame.grid(row=2, column=0, sticky="nwe", padx=20)
        self.file_entry_frame.grid_columnconfigure(0, weight=1)

        self.file_entry = ctk.CTkEntry(self.file_entry_frame, 
                                     placeholder_text="C:\\...\\save.dat", 
                                     border_width=1,
                                     border_color="#D2D2D2",
                                     font=ctk.CTkFont(family="Helvetica", size=14))
        self.file_entry.grid(row=0, column=0, sticky="we")

        self.history_button = ctk.CTkButton(self.file_entry_frame,
                                           text="",
                                         image=self.history_icon, 
                                         fg_color="#DEDEDE",
                                         hover_color="#DEDEDE",
                                         width=24,
                                         font=ctk.CTkFont(family="Helvetica", size=13),
                                         command=self.open_last_file)
        self.history_button.grid(row=0, column=1, sticky="w", padx=(5,0))

        self.browse_button = ctk.CTkButton(self.file_entry_frame,
                                           text="",
                                         image=self.browse_icon, 
                                         fg_color="#de0707",
                                         hover_color="#de0707",
                                         width=24,
                                         font=ctk.CTkFont(family="Helvetica", size=13),
                                         command=self.browse_file)
        self.browse_button.grid(row=0, column=2, sticky="w", padx=5)

        self.tab_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.tab_frame.grid(row=3, column=0, sticky="nwe", padx=20, pady=10)
        self.tab_frame.grid_columnconfigure(0, weight=1)
        self.tab_frame.grid_columnconfigure(1, weight=1)
        
        self.change_log_button = ctk.CTkButton(self.tab_frame, 
                                             text="Change Log", 
                                             font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                                             fg_color="#3B82F6", hover_color="#2563EB", command=self.show_change_log)
        self.change_log_button.grid(row=0, column=0, sticky="we", padx=(0, 5))
        
        self.important_button = ctk.CTkButton(self.tab_frame, 
                                           text="Important", 
                                           font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                                           fg_color="transparent", border_width=1, border_color="gray", command=self.show_important_log) 
        self.important_button.grid(row=0, column=1, sticky="we", padx=(5, 0))

        self.recent_changes_frame = ctk.CTkScrollableFrame(self.sidebar_frame, fg_color="white", border_width=1, border_color="#E5E7EB")
        self.recent_changes_frame.grid(row=4, column=0, sticky="nsew", padx=25, pady=(10, 20))
        
        # --- Create Main Content Frame ---
        self.main_frame = ctk.CTkFrame(self, fg_color="white")
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
        self.start_button = ctk.CTkButton(controls_frame, 
                                       text="",
                                       image=self.play_icon,
                                       width=32,
                                       height=32,
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       fg_color="#dedede", 
                                       hover_color="#dedede",
                                       command=self.toggle_monitoring)
        self.start_button.grid(row=0, column=0, sticky="e", padx=5)
        
        # Update stop button text and colors to indicate it's for releasing the file
        self.stop_button = ctk.CTkButton(controls_frame, 
                                      text="",
                                      image=self.pause_icon,
                                      width=32,
                                      height=32,
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      fg_color="#EF4444",
                                      hover_color="#DC2626",
                                      command=self.release_file,
                                      state="disabled")
        self.stop_button.grid(row=0, column=1, sticky="e", padx=5)

        self.search_entry = ctk.CTkEntry(controls_frame, 
                                     placeholder_text="Search log...",
                                     font=ctk.CTkFont(family="Helvetica", size=14))
        self.search_entry.grid(row=0, column=2, sticky="e", padx=(5, 0))

        # Main log area with slightly off-white background
        self.output_textbox = ctk.CTkTextbox(self.main_frame, 
                                          font=("Consolas", 13),
                                          corner_radius=8,
                                          fg_color="#F8FAFC",  # Slightly off-white
                                          text_color="black",
                                          state="disabled")
        self.output_textbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Configure tags for main log
        self.output_textbox._textbox.tag_configure("timestamp", foreground="gray")
        self.output_textbox._textbox.tag_configure("START", foreground="#059669", font=("Consolas", 13, "bold")) # Green
        self.output_textbox._textbox.tag_configure("STOP", foreground="#DC2626", font=("Consolas", 13, "bold")) # Red
        self.output_textbox._textbox.tag_configure("MODIFY", foreground="#D97706", font=("Consolas", 13, "bold")) # Amber
        self.output_textbox._textbox.tag_configure("INFO", foreground="gray")
        self.output_textbox._textbox.tag_configure("ERROR", foreground="red")
        
        # --- Set initial state ---
        self.log_message("Welcome! Select a file and click 'Start Monitoring'.", "INFO")
        self.add_recent_event("Application started", "INFO", None)
        self.show_change_log() # Populate sidebar

        # Add a monitoring state variable
        self.is_paused = True

    # --- UI Update Methods ---

    def clear_sidebar_list(self):
        """Destroys all widgets in the recent changes scrollable frame."""
        for widget in self.recent_changes_frame.winfo_children():
            widget.destroy()

    def show_change_log(self):
        """Populates sidebar with saved notes."""
        self.clear_sidebar_list()
        
        self.change_log_button.configure(fg_color="#3B82F6", hover_color="#2563EB")
        self.important_button.configure(fg_color="transparent", border_width=1)

        # Show saved notes from newest to oldest
        for filepath, notes in self.saved_notes.items():
            for note_entry in sorted(notes, key=lambda x: x['timestamp'], reverse=True):
                filename = os.path.basename(filepath)
                timestamp = self.format_timestamp(note_entry['timestamp'])
                
                self.create_sidebar_entry(
                    title=f"Note for {filename}",
                    subtitle=f"Added at {timestamp}",
                    note_text=note_entry['note'][:50] + "..." if len(note_entry['note']) > 50 else note_entry['note'],
                    tag="NOTE",
                    data=note_entry
                )

    def show_important_log(self):
        """Populates sidebar with IMPORTANT saved changes."""
        self.clear_sidebar_list()

        self.important_button.configure(fg_color="#3B82F6", hover_color="#2563EB")
        self.change_log_button.configure(fg_color="transparent", border_width=1)
        
        # Iterate through all files and all important changes
        for filepath, changes in self.important_changes.items():
            for change in changes:
                filename = os.path.basename(filepath)
                msg = f"Saved: {filename}\nNote: {change['note'][:30]}..."
                self.create_sidebar_entry(msg, "IMPORTANT", change)
    
    def create_sidebar_entry(self, title: str, subtitle: str, note_text: str, tag: str, data: dict = None):
        """Creates a single note entry in the sidebar."""
        event_frame = ctk.CTkFrame(self.recent_changes_frame, fg_color="white", corner_radius=6)
        event_frame.pack(fill="x", pady=(0, 10), padx=5)
        event_frame.grid_columnconfigure(1, weight=1)

        # Icon based on tag
        icon_label = ctk.CTkLabel(event_frame,
                                text="",
                                image=self.change_log_icon,  # Use note icon
                                anchor="w")
        icon_label.grid(row=0, rowspan=2, column=0, sticky="w", padx=(10, 8), pady=10)

        # Title
        title_label = ctk.CTkLabel(event_frame, 
                                text=title,
                                font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
                                anchor="w")
        title_label.grid(row=0, column=1, sticky="w", pady=(10, 0))

        # Subtitle (timestamp)
        time_label = ctk.CTkLabel(event_frame, 
                               text=subtitle,
                               font=ctk.CTkFont(family="Helvetica", size=12),
                               text_color="gray",
                               anchor="w")
        time_label.grid(row=1, column=1, sticky="w", pady=(0, 5))

        # Note preview
        note_label = ctk.CTkLabel(event_frame, 
                               text=note_text,
                               font=ctk.CTkFont(family="Helvetica", size=12),
                               text_color="gray",
                               anchor="w",
                               wraplength=200)
        note_label.grid(row=2, column=1, sticky="w", pady=(0, 10))

        if data:
            view_button = ctk.CTkButton(event_frame, 
                                    text="View",
                                    width=50,
                                    height=24,
                                    fg_color="transparent",
                                    border_width=1,
                                    border_color="#E5E7EB",
                                    text_color="black",
                                    font=ctk.CTkFont(family="Helvetica", size=12),
                                    command=lambda d=data: self.open_change_window(d['change_data'].get("filepath", "N/A"), d))
            view_button.grid(row=0, column=2, sticky="ne", padx=10, pady=10)

    def add_recent_event(self, message: str, tag: str, data: dict = None):
        """No longer needed - remove this method"""
        pass
        
    def log_message(self, message: str, tag: str = None):
        """Helper function to add a message to the main output textbox."""
        self.output_textbox.configure(state="normal")
        
        timestamp = f"{datetime.datetime.now():%H:%M:%S} "
        self.output_textbox.insert("end", timestamp, "timestamp")
        
        if tag:
            self.output_textbox.insert("end", f"{tag:8} ", tag) # 8 chars padding
        
        self.output_textbox.insert("end", f"{message}\n")
        self.output_textbox.see("end")
        self.output_textbox.configure(state="disabled")

    # --- File I/O and Decryption ---
    
    def read_file_content(self, filepath: str) -> dict:
        """Read and decrypt the current file content with retries."""
        for i in range(5):  # Retry up to 5 times
            try:
                with open(filepath, 'rb') as f:
                    encrypted_data = f.read()

                if not encrypted_data:
                    self.log_message(f"[RETRY] File is empty, retrying... ({i+1}/5)", "INFO")
                    time.sleep(0.2)
                    continue

                decrypted_json = decrypt_hollow_knight_save(encrypted_data)
                return json.loads(decrypted_json)

            except FileNotFoundError:
                self.log_message(f"File not found during read: {filepath}", "ERROR")
                return {}
            except Exception as e:
                self.log_message(f"Error reading/decrypting file (attempt {i+1}/5): {e}", "ERROR")
                time.sleep(0.2)
        
        self.log_message("Failed to read file after multiple retries.", "ERROR")
        return {}

    # --- Button Callbacks ---

    def browse_file(self):
        """
        Open a file dialog to select a file, starting in the Team Cherry folder.
        """
        base_path = os.path.join(os.path.expanduser("~"), "AppData", "LocalLow", "Team Cherry")
        silksong_path = os.path.join(base_path, "Hollow Knight Silksong")
        hk_path = os.path.join(base_path, "Hollow Knight")

        target_directory = os.path.expanduser("~")
        if os.path.exists(silksong_path):
            target_directory = silksong_path
        elif os.path.exists(hk_path):
            target_directory = hk_path
        elif os.path.exists(base_path):
            target_directory = base_path

        filename = filedialog.askopenfilename(
            initialdir=target_directory,
            title="Select Save File",
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")]
        )
        if filename:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filename)
            self.log_message(f"Selected file: {filename}", "INFO")
            self.save_recent_files(filename) # Save to recents
            
            # Load the file content on browse
            self.previous_data = self.read_file_content(filename)
            if self.previous_data:
                self.log_message(f"Successfully read and decrypted '{os.path.basename(filename)}'. Ready to monitor.", "INFO")
                self.stop_button.configure(state="normal")  # Enable stop button when file is loaded
            else:
                self.log_message(f"Could not read or decrypt '{os.path.basename(filename)}'. Check file and decryption logic.", "ERROR")

    def open_last_file(self):
        """Opens the last used file when history button is clicked."""
        try:
            if os.path.exists(self.recent_files_path):
                with open(self.recent_files_path, 'r') as f:
                    recent_files = json.load(f)
                    
                if recent_files and len(recent_files) > 0:
                    last_file = recent_files[0]  # Get the most recent file
                    if os.path.exists(last_file):
                        self.file_entry.delete(0, "end")
                        self.file_entry.insert(0, last_file)
                        self.log_message(f"Loaded last used file: {last_file}", "INFO")
                        
                        # Load the file content
                        self.previous_data = self.read_file_content(last_file)
                        if self.previous_data:
                            self.log_message(f"Successfully read and decrypted '{os.path.basename(last_file)}'. Ready to monitor.", "INFO")
                            self.stop_button.configure(state="normal")  # Enable stop button when file is loaded
                        else:
                            self.log_message(f"Could not read or decrypt '{os.path.basename(last_file)}'. Check file and decryption logic.", "ERROR")
                    else:
                        self.log_message("Last used file no longer exists.", "ERROR")
                else:
                    self.log_message("No recent files found.", "INFO")
        except Exception as e:
            self.log_message(f"Error loading last file: {e}", "ERROR")

    def toggle_monitoring(self):
        """Toggle between monitoring and paused states."""
        if self.is_paused:
            # Start monitoring
            file_path = self.file_entry.get()
            if not file_path:
                self.log_message("Please select a file first.", "ERROR")
                return
                
            if not self.previous_data:  # Only load file if not already loaded
                self.previous_data = self.read_file_content(file_path)
                if not self.previous_data:
                    self.log_message(f"Failed to read file: {file_path}. Cannot start monitoring.", "ERROR")
                    return

            self.monitoring_active = True
            self.is_paused = False
            self.log_message("Monitoring resumed.", "START")
            
            # Update UI
            self.status_indicator_label.configure(text="\u25cf Monitoring Active", text_color="#059669")
            # self.start_button.configure(fg_color="#EF4444", hover_color="#DC2626")  # Red when active
            self.stop_button.configure(state="normal")
            
            self.check_for_file_change()
        else:
            # Pause monitoring
            self.monitoring_active = False
            self.is_paused = True
            self.log_message("Monitoring paused.", "STOP")
            
            # Update UI
            self.status_indicator_label.configure(text="\u25cf Monitoring Paused", text_color="#D97706")  # Amber for paused
            # self.start_button.configure(fg_color="#22C55E", hover_color="#16A34A")  # Green when paused

    def release_file(self):
        """Completely stop monitoring and release the file."""
        self.monitoring_active = False
        self.is_paused = True
        self.previous_data = {}  # Clear the file data
        
        self.log_message("File released.", "STOP")
        self.add_recent_event("File released", "STOP", None)
        
        # Update UI
        self.status_indicator_label.configure(text="\u25cf Not Monitoring", text_color="#DC2626")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.file_entry.delete(0, "end")

    # --- Real Monitoring & Window Opener ---

    def check_for_file_change(self):
        """REAL monitoring loop. Checks for changes every 1 second."""
        if not self.monitoring_active:
            return # Stop the loop

        filepath = self.file_entry.get()
        if not filepath:
            self.log_message("No file path set. Stopping monitor.", "ERROR")
            self.stop_monitoring()
            return

        current_data = self.read_file_content(filepath)
        if not current_data:
            self.log_message("Failed to read current file data. Skipping check.", "ERROR")
            self.after(1000, self.check_for_file_change) # Try again in 1 sec
            return

        # --- This is the core logic ---
        # Compare old data vs new data
        diff = list(dictdiffer.diff(self.previous_data, current_data))
        
        if diff:
            # A change was found!
            self.log_message(f"File change detected! {len(diff)} changes.", "MODIFY")
            
            change_data = {
                "filepath": filepath,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "diff": diff, # Pass the real diff
            }
            
            # Add to sidebar
            self.add_recent_event(f"{os.path.basename(filepath)} modified", "MODIFY", change_data)
            
            # --- OPEN THE POP-UP WINDOW ---
            self.open_change_window(filepath, change_data, diff)
            
            # Update the "previous" state to the "current" state
            self.previous_data = current_data
        
        # Schedule the next check
        self.after(1000, self.check_for_file_change)


    def open_change_window(self, filepath: str, change_data: dict, diff_data: list):
        """Creates and shows the FileChangeWindow."""

        window = FileChangeWindow(self, filepath, change_data, diff_data)        

        window.grab_set()  # Make modal        
        window.transient(self)  # Keep it on top of the main window        
        # Check if a window is already open
        if hasattr(self, "change_window") and self.change_window.winfo_exists():
            self.change_window.lift() # Just bring to front
            self.change_window.grab_set() # Re-focus
        else:
            self.change_window = FileChangeWindow(self, filepath, change_data, diff_data)


def main():
    ctk.set_appearance_mode("light")
    # ctk.set_default_color_theme("blue")
    
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()