import customtkinter as ctk
from typing import Any

class StatusBar(ctk.CTkFrame):
    """
    A reusable widget to show success or error messages.
    """
    def __init__(self, master: Any, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.label = ctk.CTkLabel(
            self, 
            text="Ready.", 
            text_color="gray", 
            anchor="w",
            wraplength=600  # Prevent long errors from expanding window too much
        )
        self.label.pack(fill="x", padx=10, pady=5)

    def show_success(self, message: str):
        self.label.configure(text=message, text_color="#00cc66")  # Green

    def show_error(self, message: str):
        self.label.configure(text=message, text_color="#ff4c4c")  # Red

    def show_info(self, message: str):
        self.label.configure(text=message, text_color="gray")
        
    def clear(self):
        self.show_info("Ready.")
