import threading
import customtkinter as ctk
from typing import Any

from app.gui.components.file_picker import FilePicker
from app.gui.components.status_bar import StatusBar

from app.modules.merge_pdf import merge_pdfs
from app.modules.split_pdf import split_pdf
from app.modules.extract_pages import extract_pages
from app.modules.rotate_pages import rotate_pages
from app.modules.reorder_pages import reorder_pages
from app.modules.organize_pdf import organize_pdf

class OrganizationView(ctk.CTkFrame):
    def __init__(self, master: Any, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Tabs
        self.tabview.add("Merge")
        self.tabview.add("Split")
        self.tabview.add("Extract")
        self.tabview.add("Rotate")
        self.tabview.add("Reorder")
        
        self._build_merge_tab()
        self._build_split_tab()
        self._build_extract_tab()
        self._build_rotate_tab()
        self._build_reorder_tab()

    def _run_in_thread(self, func, status_bar, success_msg, *args, **kwargs):
        def worker():
            try:
                status_bar.show_info("Processing...")
                result = func(*args, **kwargs)
                status_bar.show_success(f"{success_msg}: {result}")
            except Exception as e:
                status_bar.show_error(f"Error: {e}")
        threading.Thread(target=worker, daemon=True).start()

    # --- Merge ---
    def _build_merge_tab(self):
        tab = self.tabview.tab("Merge")
        tab.grid_columnconfigure(0, weight=1)
        
        self.merge_input = FilePicker(tab, label_text="Select PDFs to Merge:", select_multiple=True)
        self.merge_input.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        
        self.merge_output = FilePicker(tab, label_text="Save Output As:", select_dir=False, save_as=True, filetypes=(("PDF", "*.pdf"),))
        self.merge_output.grid(row=1, column=0, sticky="ew", pady=5)
        
        self.merge_status = StatusBar(tab)
        self.merge_status.grid(row=2, column=0, sticky="ew", pady=5)
        
        btn = ctk.CTkButton(tab, text="Merge PDFs", command=self._do_merge)
        btn.grid(row=3, column=0, pady=10)
        
    def _do_merge(self):
        in_files = self.merge_input.get_paths()
        out_file = self.merge_output.get_path()
        if not in_files or not out_file:
            self.merge_status.show_error("Please select input files and output destination.")
            return
        self._run_in_thread(merge_pdfs, self.merge_status, "Merged successfully", in_files, out_file)

    # --- Split ---
    def _build_split_tab(self):
        tab = self.tabview.tab("Split")
        tab.grid_columnconfigure(0, weight=1)
        
        self.split_input = FilePicker(tab, label_text="Select PDF to Split:")
        self.split_input.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        
        # ranges
        self.split_ranges_entry = ctk.CTkEntry(tab, placeholder_text="Ranges (e.g. 1-3, 4-5)")
        self.split_ranges_entry.grid(row=1, column=0, sticky="ew", pady=5, padx=10)
        
        self.split_output = FilePicker(tab, label_text="Output Prefix (Save As):", select_dir=False, save_as=True, filetypes=(("PDF", "*.pdf"),))
        self.split_output.grid(row=2, column=0, sticky="ew", pady=5)
        
        self.split_status = StatusBar(tab)
        self.split_status.grid(row=3, column=0, sticky="ew", pady=5)
        
        btn = ctk.CTkButton(tab, text="Split PDF", command=self._do_split)
        btn.grid(row=4, column=0, pady=10)

    def _do_split(self):
        in_file = self.split_input.get_path()
        out_prefix = self.split_output.get_path()
        ranges_str = self.split_ranges_entry.get()
        if not in_file or not out_prefix or not ranges_str:
            self.split_status.show_error("Please fill all fields.")
            return
            
        ranges = []
        try:
            for r in ranges_str.split(","):
                start, end = r.split("-")
                ranges.append((int(start.strip()), int(end.strip())))
        except ValueError:
            self.split_status.show_error("Invalid range format. Use e.g. 1-3, 4-5")
            return
            
        self._run_in_thread(split_pdf, self.split_status, "Split successfully", in_file, out_prefix, ranges)

    # --- Extract ---
    def _build_extract_tab(self):
        tab = self.tabview.tab("Extract")
        tab.grid_columnconfigure(0, weight=1)
        
        self.ext_input = FilePicker(tab, label_text="Select PDF:")
        self.ext_input.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        
        self.ext_pages_entry = ctk.CTkEntry(tab, placeholder_text="Pages (e.g. 1, 3, 5)")
        self.ext_pages_entry.grid(row=1, column=0, sticky="ew", pady=5, padx=10)
        
        self.ext_output = FilePicker(tab, label_text="Save Output As:", select_dir=False, save_as=True, filetypes=(("PDF", "*.pdf"),))
        self.ext_output.grid(row=2, column=0, sticky="ew", pady=5)
        
        self.ext_status = StatusBar(tab)
        self.ext_status.grid(row=3, column=0, sticky="ew", pady=5)
        
        btn = ctk.CTkButton(tab, text="Extract Pages", command=self._do_extract)
        btn.grid(row=4, column=0, pady=10)

    def _do_extract(self):
        in_file = self.ext_input.get_path()
        out_file = self.ext_output.get_path()
        pages_str = self.ext_pages_entry.get()
        if not in_file or not out_file or not pages_str:
            self.ext_status.show_error("Please fill all fields.")
            return
        
        try:
            pages = [int(p.strip()) for p in pages_str.split(",")]
        except ValueError:
            self.ext_status.show_error("Invalid page format. Use e.g. 1, 3, 5")
            return
            
        self._run_in_thread(extract_pages, self.ext_status, "Extracted successfully", in_file, out_file, pages)

    # --- Rotate ---
    def _build_rotate_tab(self):
        tab = self.tabview.tab("Rotate")
        tab.grid_columnconfigure(0, weight=1)
        
        self.rot_input = FilePicker(tab, label_text="Select PDF:")
        self.rot_input.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        
        self.rot_angle_var = ctk.StringVar(value="90")
        angle_dropdown = ctk.CTkOptionMenu(tab, values=["90", "180", "270"], variable=self.rot_angle_var)
        angle_dropdown.grid(row=1, column=0, sticky="w", pady=5, padx=10)
        
        self.rot_pages_entry = ctk.CTkEntry(tab, placeholder_text="Pages to rotate (e.g. 1, 3) or leave blank for all")
        self.rot_pages_entry.grid(row=2, column=0, sticky="ew", pady=5, padx=10)
        
        self.rot_output = FilePicker(tab, label_text="Save Output As:", select_dir=False, save_as=True, filetypes=(("PDF", "*.pdf"),))
        self.rot_output.grid(row=3, column=0, sticky="ew", pady=5)
        
        self.rot_status = StatusBar(tab)
        self.rot_status.grid(row=4, column=0, sticky="ew", pady=5)
        
        btn = ctk.CTkButton(tab, text="Rotate Pages", command=self._do_rotate)
        btn.grid(row=5, column=0, pady=10)

    def _do_rotate(self):
        in_file = self.rot_input.get_path()
        out_file = self.rot_output.get_path()
        angle = int(self.rot_angle_var.get())
        pages_str = self.rot_pages_entry.get().strip()
        
        if not in_file or not out_file:
            self.rot_status.show_error("Please select input and output files.")
            return
            
        pages = None
        if pages_str:
            try:
                pages = [int(p.strip()) for p in pages_str.split(",")]
            except ValueError:
                self.rot_status.show_error("Invalid page format. Use e.g. 1, 3")
                return
                
        self._run_in_thread(rotate_pages, self.rot_status, "Rotated successfully", in_file, out_file, angle, pages)

    # --- Reorder ---
    def _build_reorder_tab(self):
        tab = self.tabview.tab("Reorder")
        tab.grid_columnconfigure(0, weight=1)
        
        self.re_input = FilePicker(tab, label_text="Select PDF:")
        self.re_input.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        
        self.re_order_entry = ctk.CTkEntry(tab, placeholder_text="New Order (e.g. 3, 1, 2)")
        self.re_order_entry.grid(row=1, column=0, sticky="ew", pady=5, padx=10)
        
        self.re_output = FilePicker(tab, label_text="Save Output As:", select_dir=False, save_as=True, filetypes=(("PDF", "*.pdf"),))
        self.re_output.grid(row=2, column=0, sticky="ew", pady=5)
        
        self.re_status = StatusBar(tab)
        self.re_status.grid(row=3, column=0, sticky="ew", pady=5)
        
        btn = ctk.CTkButton(tab, text="Reorder Pages", command=self._do_reorder)
        btn.grid(row=4, column=0, pady=10)

    def _do_reorder(self):
        in_file = self.re_input.get_path()
        out_file = self.re_output.get_path()
        order_str = self.re_order_entry.get().strip()
        
        if not in_file or not out_file or not order_str:
            self.re_status.show_error("Please fill all fields.")
            return
            
        try:
            order = [int(p.strip()) for p in order_str.split(",")]
        except ValueError:
            self.re_status.show_error("Invalid order format. Use e.g. 3, 1, 2")
            return
            
        self._run_in_thread(reorder_pages, self.re_status, "Reordered successfully", in_file, out_file, order)

