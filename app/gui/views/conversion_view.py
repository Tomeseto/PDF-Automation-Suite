import threading
import json
import customtkinter as ctk
from typing import Any

from app.gui.components.file_picker import FilePicker
from app.gui.components.status_bar import StatusBar

from app.modules.pdf_to_image import pdf_to_images
from app.modules.image_to_pdf import images_to_pdf
from app.modules.scan_to_pdf import scan_images_to_pdf
from app.modules.extract_text import extract_text
from app.modules.search_pdf import search_pdf

class ConversionView(ctk.CTkFrame):
    def __init__(self, master: Any, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Tabs
        self.tabview.add("PDF -> Image")
        self.tabview.add("Image -> PDF")
        self.tabview.add("Scan Images")
        self.tabview.add("Extract Text")
        self.tabview.add("Search PDF")
        
        self._build_p2i_tab()
        self._build_i2p_tab()
        self._build_scan_tab()
        self._build_text_tab()
        self._build_search_tab()

    def _run_in_thread(self, func, status_bar, success_msg, *args, **kwargs):
        def worker():
            try:
                status_bar.show_info("Processing...")
                result = func(*args, **kwargs)
                # Some functions return lists or dicts, limit output size
                if isinstance(result, (list, dict)):
                    res_str = str(result)[:100] + ("..." if len(str(result)) > 100 else "")
                else:
                    res_str = str(result)
                status_bar.show_success(f"{success_msg}: {res_str}")
            except Exception as e:
                status_bar.show_error(f"Error: {e}")
        threading.Thread(target=worker, daemon=True).start()

    # --- PDF to Image ---
    def _build_p2i_tab(self):
        tab = self.tabview.tab("PDF -> Image")
        tab.grid_columnconfigure(0, weight=1)
        
        self.p2i_input = FilePicker(tab, label_text="Select PDF:")
        self.p2i_input.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        
        self.p2i_format_var = ctk.StringVar(value="png")
        fmt_dropdown = ctk.CTkOptionMenu(tab, values=["png", "jpeg"], variable=self.p2i_format_var)
        fmt_dropdown.grid(row=1, column=0, sticky="w", pady=5, padx=10)
        
        self.p2i_output = FilePicker(tab, label_text="Save Images To (Directory):", select_dir=True)
        self.p2i_output.grid(row=2, column=0, sticky="ew", pady=5)
        
        self.p2i_status = StatusBar(tab)
        self.p2i_status.grid(row=3, column=0, sticky="ew", pady=5)
        
        btn = ctk.CTkButton(tab, text="Convert to Images", command=self._do_p2i)
        btn.grid(row=4, column=0, pady=10)

    def _do_p2i(self):
        in_file = self.p2i_input.get_path()
        out_dir = self.p2i_output.get_path()
        fmt = self.p2i_format_var.get()
        if not in_file or not out_dir:
            self.p2i_status.show_error("Please select input and output.")
            return
        self._run_in_thread(pdf_to_images, self.p2i_status, "Converted", in_file, out_dir, fmt)

    # --- Image to PDF ---
    def _build_i2p_tab(self):
        tab = self.tabview.tab("Image -> PDF")
        tab.grid_columnconfigure(0, weight=1)
        
        self.i2p_input = FilePicker(tab, label_text="Select Images:", select_multiple=True, filetypes=(("Images", "*.png;*.jpg;*.jpeg"),))
        self.i2p_input.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        
        self.i2p_output = FilePicker(tab, label_text="Save PDF As:", select_dir=False, save_as=True, filetypes=(("PDF", "*.pdf"),))
        self.i2p_output.grid(row=1, column=0, sticky="ew", pady=5)
        
        self.i2p_status = StatusBar(tab)
        self.i2p_status.grid(row=2, column=0, sticky="ew", pady=5)
        
        btn = ctk.CTkButton(tab, text="Convert to PDF", command=self._do_i2p)
        btn.grid(row=3, column=0, pady=10)

    def _do_i2p(self):
        in_files = self.i2p_input.get_paths()
        out_file = self.i2p_output.get_path()
        if not in_files or not out_file:
            self.i2p_status.show_error("Please select input images and output file.")
            return
        self._run_in_thread(images_to_pdf, self.i2p_status, "Converted to PDF", in_files, out_file)

    # --- Scan Images ---
    def _build_scan_tab(self):
        tab = self.tabview.tab("Scan Images")
        tab.grid_columnconfigure(0, weight=1)
        
        self.scan_input = FilePicker(tab, label_text="Select Images to Scan:", select_multiple=True, filetypes=(("Images", "*.png;*.jpg;*.jpeg"),))
        self.scan_input.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        
        self.scan_enhance_var = ctk.BooleanVar(value=True)
        cb = ctk.CTkCheckBox(tab, text="Enhance Scans (Deskew & Contrast)", variable=self.scan_enhance_var)
        cb.grid(row=1, column=0, sticky="w", pady=5, padx=10)
        
        self.scan_output = FilePicker(tab, label_text="Save Scanned PDF As:", select_dir=False, save_as=True, filetypes=(("PDF", "*.pdf"),))
        self.scan_output.grid(row=2, column=0, sticky="ew", pady=5)
        
        self.scan_status = StatusBar(tab)
        self.scan_status.grid(row=3, column=0, sticky="ew", pady=5)
        
        btn = ctk.CTkButton(tab, text="Process Scan", command=self._do_scan)
        btn.grid(row=4, column=0, pady=10)

    def _do_scan(self):
        in_files = self.scan_input.get_paths()
        out_file = self.scan_output.get_path()
        enhance = self.scan_enhance_var.get()
        if not in_files or not out_file:
            self.scan_status.show_error("Please select input images and output file.")
            return
        self._run_in_thread(scan_images_to_pdf, self.scan_status, "Scan complete", in_files, out_file, enhance)

    # --- Extract Text ---
    def _build_text_tab(self):
        tab = self.tabview.tab("Extract Text")
        tab.grid_columnconfigure(0, weight=1)
        
        self.txt_input = FilePicker(tab, label_text="Select PDF:")
        self.txt_input.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        
        self.txt_output = ctk.CTkTextbox(tab, height=150)
        self.txt_output.grid(row=1, column=0, sticky="nsew", pady=5, padx=10)
        tab.grid_rowconfigure(1, weight=1)
        
        self.txt_status = StatusBar(tab)
        self.txt_status.grid(row=2, column=0, sticky="ew", pady=5)
        
        btn = ctk.CTkButton(tab, text="Extract Text", command=self._do_extract_text)
        btn.grid(row=3, column=0, pady=10)

    def _do_extract_text(self):
        in_file = self.txt_input.get_path()
        if not in_file:
            self.txt_status.show_error("Please select a PDF.")
            return

        def worker():
            try:
                self.txt_status.show_info("Extracting...")
                result = extract_text(in_file)
                self.txt_output.delete("1.0", "end")
                for page, text in result.items():
                    self.txt_output.insert("end", f"--- Page {page} ---\n{text}\n\n")
                self.txt_status.show_success("Extraction complete.")
            except Exception as e:
                self.txt_status.show_error(f"Error: {e}")
        threading.Thread(target=worker, daemon=True).start()

    # --- Search PDF ---
    def _build_search_tab(self):
        tab = self.tabview.tab("Search PDF")
        tab.grid_columnconfigure(0, weight=1)
        
        self.search_input = FilePicker(tab, label_text="Select PDF:")
        self.search_input.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        
        self.search_query = ctk.CTkEntry(tab, placeholder_text="Search query...")
        self.search_query.grid(row=1, column=0, sticky="ew", pady=5, padx=10)
        
        self.search_case_var = ctk.BooleanVar(value=False)
        cb = ctk.CTkCheckBox(tab, text="Case Sensitive", variable=self.search_case_var)
        cb.grid(row=2, column=0, sticky="w", pady=5, padx=10)
        
        self.search_output = ctk.CTkTextbox(tab, height=150)
        self.search_output.grid(row=3, column=0, sticky="nsew", pady=5, padx=10)
        tab.grid_rowconfigure(3, weight=1)
        
        self.search_status = StatusBar(tab)
        self.search_status.grid(row=4, column=0, sticky="ew", pady=5)
        
        btn = ctk.CTkButton(tab, text="Search", command=self._do_search)
        btn.grid(row=5, column=0, pady=10)

    def _do_search(self):
        in_file = self.search_input.get_path()
        query = self.search_query.get()
        case_sens = self.search_case_var.get()
        if not in_file or not query:
            self.search_status.show_error("Please select a PDF and enter a query.")
            return

        def worker():
            try:
                self.search_status.show_info("Searching...")
                results = search_pdf(in_file, query, case_sens)
                self.search_output.delete("1.0", "end")
                if not results:
                    self.search_output.insert("end", "No matches found.")
                else:
                    self.search_output.insert("end", f"Found {len(results)} matches:\n\n")
                    for match in results:
                        page = match.get("page", "?")
                        snippet = match.get("snippet", "").replace("\n", " ")
                        self.search_output.insert("end", f"--- Page {page} ---\n...{snippet}...\n\n")
                self.search_status.show_success(f"Found {len(results)} matches.")
            except Exception as e:
                self.search_status.show_error(f"Error: {e}")
        threading.Thread(target=worker, daemon=True).start()
