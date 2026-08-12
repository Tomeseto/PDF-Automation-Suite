"""PDF Automation Suite — main entry point."""

import customtkinter as ctk
from app.gui.app_window import AppWindow

def main() -> None:
    """Launch the PDF Automation Suite."""
    
    # Set default appearance
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    app = AppWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
