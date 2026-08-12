import sys
import customtkinter as ctk

from app.gui.views.organization_view import OrganizationView
from app.gui.views.batch_view import BatchView
from app.gui.views.logs_view import LogsView

from app.gui.views.security_view import SecurityView
from app.gui.views.conversion_view import ConversionView


class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF Automation Suite")
        self.geometry("900x600")
        
        # Configure grid layout (1x2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1) # Spacer

        self.logo_label = ctk.CTkLabel(self.sidebar, text="PDF Suite", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Buttons
        self.btn_org = ctk.CTkButton(self.sidebar, text="Organization", command=lambda: self.select_view("org"))
        self.btn_org.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_sec = ctk.CTkButton(self.sidebar, text="Security", command=lambda: self.select_view("sec"))
        self.btn_sec.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_conv = ctk.CTkButton(self.sidebar, text="Conversion", command=lambda: self.select_view("conv"))
        self.btn_conv.grid(row=3, column=0, padx=20, pady=10)
        
        self.btn_batch = ctk.CTkButton(self.sidebar, text="Batch Process", command=lambda: self.select_view("batch"))
        self.btn_batch.grid(row=4, column=0, padx=20, pady=10)
        
        self.btn_logs = ctk.CTkButton(self.sidebar, text="View Logs", command=lambda: self.select_view("logs"))
        self.btn_logs.grid(row=5, column=0, padx=20, pady=10)
        
        self.btn_exit = ctk.CTkButton(self.sidebar, text="Exit", command=self._exit_app, fg_color="#ff4c4c", hover_color="#cc0000")
        self.btn_exit.grid(row=8, column=0, padx=20, pady=20)

        # --- Main Frame ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Init views
        self.views = {
            "org": OrganizationView(self.main_frame),
            "sec": SecurityView(self.main_frame),
            "conv": ConversionView(self.main_frame),
            "batch": BatchView(self.main_frame),
            "logs": LogsView(self.main_frame),
        }

        # Default view
        self.select_view("org")

    def select_view(self, view_name: str):
        # Hide all
        for v in self.views.values():
            v.grid_forget()
            
        # Show selected
        self.views[view_name].grid(row=0, column=0, sticky="nsew")
        
        # If logs view is selected, refresh it
        if view_name == "logs":
            self.views["logs"].refresh_logs()
            
    def _exit_app(self):
        # Optionally show confirmation dialog
        self.destroy()
        sys.exit(0)
