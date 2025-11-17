import os
from typing import Callable, TYPE_CHECKING
import customtkinter as ctk

from Modules.types import ChangeDataType
if TYPE_CHECKING:
    from Managers.AppManager import AppManager
class ChangeWindow(ctk.CTkToplevel):
    def __init__(self, *args, 
                app_manager: 'AppManager',
                note: str, 
                change: ChangeDataType,
                **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.app_manager = app_manager
        self.note: str = note
        self.change: ChangeDataType = change

        self.title("Change")
        self.geometry("700x550") 
        self.resizable(False, False)
        self.withdraw()

        self.configure(fg_color="white")

        # CONFIGURE ROWS
        self.grid_rowconfigure(0, weight=0)  # Row 0 for header_frame
        self.grid_rowconfigure(1, weight=1)  # Row 1 for main_content_frame (the diff)
        self.grid_rowconfigure(2, weight=0)  # Row 2 for footer_frame

        self.grid_columnconfigure(0, weight=1)

        # print(self.change.get("diff"))

        self._gui_header()
        self._gui_main()
        self._gui_footer()

        self.deiconify()
        self.grab_set()  # Block interaction with other windows
        self.focus()
        
        self.protocol("WM_DELETE_WINDOW", self.closing)
    
    def _gui_header(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="#f0f0f0", corner_radius=0)
        self.header_frame.grid(row=0, column=0,  sticky="ew")

        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)

        self.header_frame.grid_rowconfigure(0, weight=0)  
        self.header_frame.grid_rowconfigure(1, weight=0)  
        self.header_frame.grid_rowconfigure(2, weight=0)

        divider = ctk.CTkFrame(self.header_frame,
                            height=1, # the height here means nothing, the border makes it visible   
                            fg_color="#B8B8B8",
                            border_width=1)   

        # Use sticky="ew" to make it stretch horizontally (East-West)
        divider.grid(row=0, column=0, sticky="ew", pady=0, columnspan=2)

        base_dir = os.path.join(os.path.expanduser("~"), 
            "AppData", 
            "LocalLow", 
            "Team Cherry")
        filepath = self.change.get("filepath")[len(base_dir):]

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=filepath,
            fg_color="transparent",
            font=ctk.CTkFont(family="Roboto Mono", size=14),
            text_color="#4E4E4E",
            anchor="w",
            justify="left"
        )
        self.title_label.grid(row=1,column=0,padx=(15,0), pady=8, sticky="w")

        self.timestamp_label = ctk.CTkLabel(
            self.header_frame,
            fg_color="transparent",
            text=self.change.get("timestamp"),
            font=ctk.CTkFont(family="Roboto Mono", size=14),
            text_color="#5f6675",
            anchor="w"
        )
        self.timestamp_label.grid(row=1,column=1,padx=(0,15), pady=8)

        divider = ctk.CTkFrame(self.header_frame,
                            height=1, # the height here means nothing, the border makes it visible   
                            fg_color="#5C5C5C",
                            border_width=1)   

        # Use sticky="ew" to make it stretch horizontally (East-West)
        divider.grid(row=2, column=0, sticky="ew", pady=0, columnspan=2)

    def _gui_main(self):
        self.diff_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        self.diff_frame.grid(row=1, column=0, sticky="nsew", padx=0)

        self.diff_frame.grid_rowconfigure(0, weight=1)
        self.diff_frame.grid_columnconfigure(0, weight=1)

        self.diff_scroll_frame = ctk.CTkScrollableFrame(
            self.diff_frame,
            fg_color="transparent",
            # border_width=1,
            # border_color="#cdcdcd"
        )
        self.diff_scroll_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=10)

        self.populate_diff()

    def _gui_footer(self):

        FOOTER_COLOR = "#f0f0f0"
        self.footer_frame = ctk.CTkFrame(
            self,
            fg_color=FOOTER_COLOR,
        )
        self.footer_frame.grid( padx=0, pady=0, sticky="ew")


        FOOTER_PADDING = 10

        self.footer_frame.grid_columnconfigure(0,weight=1)
        self.footer_frame.grid_columnconfigure(1,weight=0)

        divider = ctk.CTkFrame(self.footer_frame,
                            height=1, # the height here means nothing, the border makes it visible   
                            fg_color="#5C5C5C",
                            border_width=1)   

        # Use sticky="ew" to make it stretch horizontally (East-West)
        divider.grid(row=0, column=0, sticky="ew", pady=0, columnspan=2)

        self.note_frame = ctk.CTkFrame(
            self.footer_frame,
            # fg_color="red",
            fg_color="transparent"
        )
        self.note_frame.grid( row=1, column=0, sticky="ew", pady=FOOTER_PADDING, padx=(10,0))

        self.btn_frame = ctk.CTkFrame(
            self.footer_frame,
            fg_color="transparent"
        )
        self.btn_frame.grid( row=1, column=1, sticky="w", pady=FOOTER_PADDING, padx=(0,10))

        font_bold = ctk.CTkFont(family="Roboto Mono", size=14, weight="bold")
        font_normal = ctk.CTkFont(family="Roboto Mono", size=14, weight="normal")

        self.note_frame.grid_columnconfigure(0,weight=0)
        self.note_frame.grid_columnconfigure(1,weight=1)

        # footer note

        note_label1 = ctk.CTkLabel(
            self.note_frame,
            text="Note:",
            font=font_bold,
        )
        note_label1.grid( row=0, column=0, padx=0, pady=0)

        # self.note = "Defeated the high halls gauntlet and got silk spool from high halls high halls high halls high halls"

        limit = 80
        note_text = ""
        start = 0
        for _ in range(len(self.note) // limit + 1):
            if start >= len(self.note):
                break
            end = min((start+limit) , len(self.note))
            if end == len(self.note):
                note_text = note_text + self.note[start:end].strip() + "\n"
                start = end 
                continue
            while self.note[end] not in [" ","\n"]:
                end -= 1
            note_text = note_text + self.note[start:end].strip() + "\n"
            start = end
        note_text = note_text.rstrip("\n")

        note_label2 = ctk.CTkLabel(
            self.note_frame,
            text=note_text,
            font=font_normal,
            justify="left",
            text_color="#4E4E4E",
        )
        note_label2.grid( row=0, column=1, padx=(15,0), pady=0, sticky="w")

        self.btn_frame.grid_columnconfigure(0,weight=0)
        self.btn_frame.grid_columnconfigure(1,weight=0)
        self.btn_frame.grid_columnconfigure(2,weight=0)

        # btn1 = ctk.CTkButton(
        #     self.btn_frame,
        #     text="Edit",
        #     image=self.app_manager.AssetManager.get_icon("edit_note_icon"),
        #     font=font_normal,
        #     width=0, # tells the app to calc the width acc to content
        #     fg_color=FOOTER_COLOR,
        #     hover_color=FOOTER_COLOR,
        #     text_color="#000000",
        # )
        # btn1.grid( row=0, column=0, padx=(10,5), pady=0)
        
        # btn2 = ctk.CTkButton(
        #     self.btn_frame,
        #     text="Important",
        #     image=self.app_manager.AssetManager.get_icon("star_red"),
        #     font=font_normal,
        #     width=0, # tells the app to calc the width acc to content
        #     fg_color=FOOTER_COLOR,
        #     hover_color=FOOTER_COLOR,
        #     text_color="#D92626",
        # )
        # btn2.grid( row=0, column=1, padx=10, pady=0)

        btn3 = ctk.CTkButton(
            self.btn_frame,
            text=" Close ",
            font=font_normal,
            width=0, # tells the app to calc the width acc to content
            fg_color="#D92626",
            hover_color="#CC2525",
            command=self.closing,
        )
        btn3.grid( row=0, column=2, padx=(10,15), pady=0)

    def closing(self):
        self.destroy()
        # self.app_manager._on_closing()   # remember to remove after testing

    def populate_diff(self):
        for i, item in enumerate(self.change['diff']):

            operation, path, values = item
            del_content, add_content = values

            change_frame = ctk.CTkFrame(
                self.diff_scroll_frame,
                fg_color="#f7f7f7" if i%2 == 0 else "#fcfcfc",
            )
            change_frame.pack( padx=15, pady=5, fill="x", expand=True)
            change_frame.grid_columnconfigure(0, weight=1)

            diff_font = ctk.CTkFont(family="Roboto Mono", size=13, weight="normal")
            diff_font_bold = ctk.CTkFont(family="Roboto Mono", size=13, weight="bold")

            title_frame = ctk.CTkFrame(
                change_frame,
                fg_color="transparent",
            )
            title_frame.grid( row=0, column=0, padx=5, pady=2, sticky="ew")

            arrow_label = ctk.CTkLabel(
                title_frame,
                text="",
                image=self.app_manager.AssetManager.get_icon("arrow_right")
            )
            arrow_label.grid(row=0, column=0, padx=0, pady=0)

            title_label = ctk.CTkLabel(
                title_frame,
                text=f"{path}",
                fg_color="transparent",
                font=diff_font_bold,
                text_color="#616161"
            )
            title_label.grid(row=0, column=1, padx=(3,0),sticky="w")

            values_frame = ctk.CTkFrame(
                change_frame,
                fg_color="transparent",
            )
            values_frame.grid( row=1, column=0, padx=5, pady=(0,5), sticky="ew")

            def del_widget(col: int = 0):
                values_frame.grid_columnconfigure(col, weight=0)
                del_frame = ctk.CTkFrame(
                    values_frame,
                    fg_color="#fdecec",
                    border_width=2,
                    border_color="#656565",
                )
                del_frame.grid( row=0, column=col, padx=5, pady=0, sticky="w")

                label_del = ctk.CTkLabel(
                    del_frame,
                    text=f" - {del_content} ",
                    text_color="#b81818",
                    font=diff_font,
                )
                label_del.pack(padx=5, pady=2)

            def add_widget(col: int = 1):
                values_frame.grid_columnconfigure(col, weight=0)
                add_frame = ctk.CTkFrame(
                    values_frame,
                    fg_color="#e8f9ef",
                    border_width=2,
                    border_color="#656565",
                )
                add_frame.grid( row=0, column=col, padx=5, pady=0, sticky="w")

                label_add = ctk.CTkLabel(
                    add_frame,
                    text=f" + {add_content} ",
                    text_color="#117e3a",
                    font=diff_font,
                )
                label_add.pack(padx=5, pady=2)

            if operation == "change":
                del_widget()
                add_widget()
            elif operation == "add":
                add_widget(col=0)
            elif operation == "del":
                del_widget()
