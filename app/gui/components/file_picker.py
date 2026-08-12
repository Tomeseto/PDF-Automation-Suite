import customtkinter as ctk
from tkinter import filedialog
from typing import Optional, Any


class FilePicker(ctk.CTkFrame):
    """
    A reusable widget for selecting files or directories.
    """
    def __init__(
        self,
        master: Any,
        label_text: str = "Select File:",
        select_dir: bool = False,
        select_multiple: bool = False,
        save_as: bool = False,
        filetypes: tuple = (("PDF Files", "*.pdf"), ("All Files", "*.*")),
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.select_dir = select_dir
        self.select_multiple = select_multiple
        self.save_as = save_as
        self.filetypes = filetypes
        self._current_paths: list[str] = []

        # Layout: Label on top, Entry + Button in a row below
        self.label = ctk.CTkLabel(self, text=label_text, anchor="w")
        self.label.pack(fill="x", padx=0, pady=(0, 5))

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", expand=True)

        self.entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="No file selected...", 
            state="readonly"
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_btn = ctk.CTkButton(
            self.input_frame,
            text="Browse",
            width=80,
            command=self._browse
        )
        self.browse_btn.pack(side="right")

    def _browse(self):
        if self.select_dir:
            path = filedialog.askdirectory()
            if path:
                self.set_paths([path])
        elif self.select_multiple:
            paths = filedialog.askopenfilenames(filetypes=self.filetypes)
            if paths:
                self.set_paths(list(paths))
        elif self.save_as:
            path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=self.filetypes)
            if path:
                self.set_paths([path])
        else:
            path = filedialog.askopenfilename(filetypes=self.filetypes)
            if path:
                self.set_paths([path])

    def set_paths(self, paths: list[str]):
        """Programmatically set the selected paths."""
        self._current_paths = paths
        
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        if not paths:
            self.entry.insert(0, "")
        elif len(paths) == 1:
            self.entry.insert(0, paths[0])
        else:
            self.entry.insert(0, f"{len(paths)} files selected")
        self.entry.configure(state="readonly")

    def get_paths(self) -> list[str]:
        """Return a list of selected absolute paths."""
        return self._current_paths

    def get_path(self) -> Optional[str]:
        """Return a single selected path, or None."""
        if self._current_paths:
            return self._current_paths[0]
        return None

    def clear(self):
        """Clear the selection."""
        self.set_paths([])
