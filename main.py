import customtkinter as ctk
from AppManager import AppManager

def main():
    ctk.set_appearance_mode("light")
    app = AppManager()
    app.mainloop()

if __name__=="__main__":
    main()