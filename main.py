import customtkinter as ctk
from AppManager import AppManager

def main():
    ctk.set_appearance_mode("light")
    # ctk.deactivate_automatic_dpi_awareness()
    app = AppManager()
    # app.console_logging = True
    app.mainloop()

if __name__=="__main__":
    main()