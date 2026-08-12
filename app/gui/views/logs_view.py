import customtkinter as ctk
from typing import Any
import json

from app.core.logger import get_recent_events, clear_log

class LogsView(ctk.CTkFrame):
    def __init__(self, master: Any, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header.grid_columnconfigure(0, weight=1)
        
        lbl = ctk.CTkLabel(header, text="Processing Logs", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.grid(row=0, column=0, sticky="w")
        
        refresh_btn = ctk.CTkButton(header, text="Refresh", width=80, command=self.refresh_logs)
        refresh_btn.grid(row=0, column=1, padx=5)
        
        clear_btn = ctk.CTkButton(header, text="Clear Logs", width=80, fg_color="#ff4c4c", hover_color="#cc0000", command=self._clear_logs)
        clear_btn.grid(row=0, column=2)
        
        # Text Area
        self.textbox = ctk.CTkTextbox(frame, wrap="word", font=ctk.CTkFont(family="Consolas", size=12))
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        self.refresh_logs()
        
    def refresh_logs(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        
        events = get_recent_events(limit=50)
        if not events:
            self.textbox.insert("1.0", "No logs found.")
        else:
            for event in reversed(events):
                try:
                    # Clean up the output if it's stored as JSON
                    log_entry = json.dumps(event, indent=2)
                except Exception:
                    log_entry = str(event)
                
                self.textbox.insert("end", log_entry + "\n\n")
                
        self.textbox.configure(state="disabled")

    def _clear_logs(self):
        clear_log()
        self.refresh_logs()
