import os
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    """Logs all events detected."""

    def on_any_event(self, event):
        """
        Catches all events and prints a formatted message.
        
        event.event_type (str): 'modified', 'created', 'deleted', 'moved'
        event.is_directory (bool): True if event was on a directory
        event.src_path (str): Path to the file/directory that triggered event
        """
        
        # Don't log directory modification events, as they are very noisy
        # (e.g., just accessing a folder can trigger it)
        if event.is_directory and event.event_type == 'modified':
            return

        # For 'moved' events, the event object has a 'dest_path' attribute
        if event.event_type == 'moved':
            print(f"📁 [MOVED]   From: {event.src_path}  ->  To: {event.dest_path}")
        else:
            # Format other events (created, modified, deleted)
            event_name = event.event_type.upper()
            print(f"📄 [{event_name}] at: {event.src_path}")


if __name__ == "__main__":
    # Check if the user provided a path to monitor
    # if len(sys.argv) < 2:
    #     print("Usage: python monitor.py /path/to/your/folder")
    #     sys.exit(1)
        
    path_to_watch = os.path.join(os.path.expanduser("~"), "AppData", "LocalLow", "Team Cherry","Hollow Knight Silksong","1156132065")
    
    print(f"Starting file monitor for: {path_to_watch}")
    print("Press Ctrl+C to stop.")

    # --- Setup and start the observer ---
    event_handler = ChangeHandler()
    observer = Observer()
    
    # Schedule the observer
    # recursive=True means it will watch subdirectories as well
    observer.schedule(event_handler, path_to_watch, recursive=True)
    
    # Start the observer thread
    observer.start()

    try:
        # Keep the main thread alive otherwise the script will exit
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C to stop the observer
        print("\nStopping monitor...")
        observer.stop()
    
    # Wait for the observer thread to finish
    observer.join()
    print("Monitor stopped.")