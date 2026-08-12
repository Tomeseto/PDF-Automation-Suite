import threading
import customtkinter as ctk
from typing import Any

from app.gui.components.file_picker import FilePicker
from app.gui.components.status_bar import StatusBar

from app.modules.batch_process.registry import BATCH_OPERATIONS
from app.modules.batch_process import batch_process

class BatchView(ctk.CTkFrame):
    def __init__(self, master: Any, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        
        # Operation Selector
        self.op_var = ctk.StringVar(value=list(BATCH_OPERATIONS.keys())[0])
        op_label = ctk.CTkLabel(frame, text="Select Batch Operation:", anchor="w")
        op_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        
        self.op_dropdown = ctk.CTkOptionMenu(
            frame, 
            values=list(BATCH_OPERATIONS.keys()), 
            variable=self.op_var
        )
        self.op_dropdown.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Input Files
        self.batch_input = FilePicker(frame, label_text="Select PDFs to Process:", select_multiple=True)
        self.batch_input.grid(row=2, column=0, sticky="ew", pady=(10, 5))
        
        # Output Directory
        self.batch_output = FilePicker(frame, label_text="Select Output Directory:", select_dir=True)
        self.batch_output.grid(row=3, column=0, sticky="ew", pady=5)
        
        # Options JSON (Optional advanced feature)
        self.options_entry = ctk.CTkEntry(frame, placeholder_text="Additional Options (e.g. watermark_text=CONFIDENTIAL)")
        self.options_entry.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        
        # Status
        self.batch_status = StatusBar(frame)
        self.batch_status.grid(row=5, column=0, sticky="ew", pady=5)
        
        btn = ctk.CTkButton(frame, text="Run Batch Process", command=self._do_batch)
        btn.grid(row=6, column=0, pady=10)

    def _do_batch(self):
        operation = self.op_var.get()
        in_files = self.batch_input.get_paths()
        out_dir = self.batch_output.get_path()
        options_str = self.options_entry.get().strip()
        
        if not in_files or not out_dir:
            self.batch_status.show_error("Please select input files and output directory.")
            return
            
        options = {}
        if options_str:
            try:
                for pair in options_str.split(","):
                    k, v = pair.split("=")
                    options[k.strip()] = v.strip()
            except ValueError:
                self.batch_status.show_error("Invalid options format. Use k=v, k2=v2")
                return

        def worker():
            try:
                self.batch_status.show_info("Processing batch...")
                results = batch_process(operation, in_files, options, out_dir)
                
                successes = sum(1 for r in results if r["status"] == "success")
                failures = len(results) - successes
                msg = f"Batch complete: {successes} success, {failures} failed."
                
                if failures == 0:
                    self.batch_status.show_success(msg)
                else:
                    self.batch_status.show_error(msg)
            except Exception as e:
                self.batch_status.show_error(f"Error: {e}")
                
        threading.Thread(target=worker, daemon=True).start()
