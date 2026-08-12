import threading
import customtkinter as ctk
from typing import Any

from app.gui.components.file_picker import FilePicker
from app.gui.components.status_bar import StatusBar

from app.modules.password_add import add_password
from app.modules.password_remove import remove_password
from app.modules.watermark_add import add_watermark
from app.modules.watermark_remove import remove_watermark
from app.modules.signature_add import add_signature

class SecurityView(ctk.CTkFrame):
    def __init__(self, master: Any, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Tabs
        self.tabview.add("Passwords")
        self.tabview.add("Watermarks")
        self.tabview.add("Signatures")
        
        self._build_passwords_tab()
        self._build_watermarks_tab()
        self._build_signatures_tab()

    def _run_in_thread(self, func, status_bar, success_msg, *args, **kwargs):
        def worker():
            try:
                status_bar.show_info("Processing...")
                result = func(*args, **kwargs)
                status_bar.show_success(f"{success_msg}: {result}")
            except Exception as e:
                # IMPORTANT: Never log or print the raw arguments just in case they contain passwords.
                # The exception message should be safe, as backend modules don't embed passwords in errors.
                status_bar.show_error(f"Error: {e}")
        threading.Thread(target=worker, daemon=True).start()

    # --- Passwords ---
    def _build_passwords_tab(self):
        tab = self.tabview.tab("Passwords")
        tab.grid_columnconfigure(0, weight=1)
        
        self.pass_input = FilePicker(tab, label_text="Select PDF:")
        self.pass_input.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        
        self.pass_entry = ctk.CTkEntry(tab, placeholder_text="Password", show="*")
        self.pass_entry.grid(row=1, column=0, sticky="ew", pady=5, padx=10)
        
        self.pass_output = FilePicker(tab, label_text="Save Output As:", select_dir=False, filetypes=(("PDF", "*.pdf"),))
        self.pass_output.grid(row=2, column=0, sticky="ew", pady=5)
        
        self.pass_status = StatusBar(tab)
        self.pass_status.grid(row=3, column=0, sticky="ew", pady=5)
        
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=10)
        
        btn_add = ctk.CTkButton(btn_frame, text="Add Password", command=self._do_add_password)
        btn_add.pack(side="left", padx=5)
        
        btn_remove = ctk.CTkButton(btn_frame, text="Remove Password", command=self._do_remove_password)
        btn_remove.pack(side="left", padx=5)

    def _do_add_password(self):
        in_file = self.pass_input.get_path()
        out_file = self.pass_output.get_path()
        password = self.pass_entry.get()
        if not in_file or not out_file or not password:
            self.pass_status.show_error("Please fill all fields.")
            return
        self._run_in_thread(add_password, self.pass_status, "Password added", in_file, out_file, password)

    def _do_remove_password(self):
        in_file = self.pass_input.get_path()
        out_file = self.pass_output.get_path()
        password = self.pass_entry.get()
        if not in_file or not out_file or not password:
            self.pass_status.show_error("Please fill all fields.")
            return
        self._run_in_thread(remove_password, self.pass_status, "Password removed", in_file, out_file, password)

    # --- Watermarks ---
    def _build_watermarks_tab(self):
        tab = self.tabview.tab("Watermarks")
        tab.grid_columnconfigure(0, weight=1)
        
        self.wm_input = FilePicker(tab, label_text="Select PDF:")
        self.wm_input.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        
        self.wm_text_entry = ctk.CTkEntry(tab, placeholder_text="Watermark Text (e.g. DRAFT)")
        self.wm_text_entry.grid(row=1, column=0, sticky="ew", pady=5, padx=10)
        
        self.wm_output = FilePicker(tab, label_text="Save Output As:", select_dir=False, filetypes=(("PDF", "*.pdf"),))
        self.wm_output.grid(row=2, column=0, sticky="ew", pady=5)
        
        self.wm_status = StatusBar(tab)
        self.wm_status.grid(row=3, column=0, sticky="ew", pady=5)
        
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=10)
        
        btn_add = ctk.CTkButton(btn_frame, text="Add Watermark", command=self._do_add_wm)
        btn_add.pack(side="left", padx=5)
        
        btn_remove = ctk.CTkButton(btn_frame, text="Remove Watermark", command=self._do_remove_wm)
        btn_remove.pack(side="left", padx=5)

    def _do_add_wm(self):
        in_file = self.wm_input.get_path()
        out_file = self.wm_output.get_path()
        text = self.wm_text_entry.get()
        if not in_file or not out_file or not text:
            self.wm_status.show_error("Please fill all fields.")
            return
        self._run_in_thread(add_watermark, self.wm_status, "Watermark added", in_file, out_file, text)

    def _do_remove_wm(self):
        in_file = self.wm_input.get_path()
        out_file = self.wm_output.get_path()
        if not in_file or not out_file:
            self.wm_status.show_error("Please select input and output files.")
            return
        self._run_in_thread(remove_watermark, self.wm_status, "Watermark removed", in_file, out_file)

    # --- Signatures ---
    def _build_signatures_tab(self):
        tab = self.tabview.tab("Signatures")
        tab.grid_columnconfigure(0, weight=1)
        
        self.sig_pdf_input = FilePicker(tab, label_text="Select PDF:")
        self.sig_pdf_input.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        
        self.sig_img_input = FilePicker(tab, label_text="Select Signature Image:", filetypes=(("Images", "*.png;*.jpg;*.jpeg"),))
        self.sig_img_input.grid(row=1, column=0, sticky="ew", pady=5)
        
        # position
        pos_frame = ctk.CTkFrame(tab, fg_color="transparent")
        pos_frame.grid(row=2, column=0, sticky="ew", pady=5, padx=10)
        pos_frame.grid_columnconfigure((0,1,2), weight=1)
        
        self.sig_page = ctk.CTkEntry(pos_frame, placeholder_text="Page (e.g. 1)")
        self.sig_page.grid(row=0, column=0, padx=2)
        self.sig_x = ctk.CTkEntry(pos_frame, placeholder_text="X (e.g. 100)")
        self.sig_x.grid(row=0, column=1, padx=2)
        self.sig_y = ctk.CTkEntry(pos_frame, placeholder_text="Y (e.g. 100)")
        self.sig_y.grid(row=0, column=2, padx=2)
        
        self.sig_output = FilePicker(tab, label_text="Save Output As:", select_dir=False, filetypes=(("PDF", "*.pdf"),))
        self.sig_output.grid(row=3, column=0, sticky="ew", pady=5)
        
        self.sig_status = StatusBar(tab)
        self.sig_status.grid(row=4, column=0, sticky="ew", pady=5)
        
        btn = ctk.CTkButton(tab, text="Add Signature", command=self._do_add_sig)
        btn.grid(row=5, column=0, pady=10)

    def _do_add_sig(self):
        in_file = self.sig_pdf_input.get_path()
        img_file = self.sig_img_input.get_path()
        out_file = self.sig_output.get_path()
        
        try:
            page = int(self.sig_page.get())
            x = float(self.sig_x.get())
            y = float(self.sig_y.get())
        except ValueError:
            self.sig_status.show_error("Page, X, and Y must be numbers.")
            return
            
        if not in_file or not img_file or not out_file:
            self.sig_status.show_error("Please select all files.")
            return
            
        self._run_in_thread(add_signature, self.sig_status, "Signature added", in_file, out_file, img_file, page, x, y)
