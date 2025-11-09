import customtkinter as ctk
from PIL import Image
from AppWindows.NotificationWindow import NotificationWindow

class TestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Simulate the app_icon from AppManager
        self.app_icon = ctk.CTkImage(
            light_image=Image.open("assets/icons/app_icon.png"),
            dark_image=Image.open("assets/icons/app_icon.png"),
            size=(48, 48)
        )
        
        # Sample change data
        self.test_data = {
            "filepath": "C:/Users/test/AppData/LocalLow/Team Cherry/Hollow Knight Silksong/user4.dat",
            "timestamp": "2025-11-08 21:51:49",
            "diff": [
                ('change', 'playerData.playTime', (4950.0293, 4961.6543)),
                ('change', 'playerData.pilgrimRestCrowd', (2, 1)),
                ('change', 'playerData.pilgrimGroupBonegrave', (3, 2)),
                ('change', 'playerData.pilgrimGroupShellgrave', (1, 3)),
                ('change', 'playerData.halfwayCrowd', (2, 3)),
                ('change', 'playerData.FisherWalkerIdleTimeLeft', (12.8525553, 2.18597)),
                ('change', 'playerData.mapperAway', (False, True)),
                ('change', 'playerData.FisherWalkerTimer', (68.5083542, 64.25766)),
                ('change', 'playerData.FisherWalkerDirection', (False, True))
            ]
        }
        
        # Create and show notification window
        self.notification = NotificationWindow(self, change_data=self.test_data)
        
        # Center the notification window
        self.notification.update_idletasks()
        # width = self.notification.winfo_width()
        # height = self.notification.winfo_height()
        # x = (self.notification.winfo_screenwidth() // 2) - (width // 2)
        # y = (self.notification.winfo_screenheight() // 2) - (height // 2)
        # self.notification.geometry(f"{width}x{height}+{x}+{y}")
        
        # Hide main window
        self.withdraw()
        
        # Close app when notification is closed
        self.notification.protocol("WM_DELETE_WINDOW", self.quit)

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = TestApp()
    app.mainloop()
