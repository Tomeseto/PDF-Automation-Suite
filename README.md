# PDF Automation Suite

A fully offline, modular Python application for automating common PDF operations.

## Features (18 core + 2 app-level)

| # | Feature | Owner | Status |
|---|---------|-------|--------|
| 1 | Merge PDFs | Tanmay | 🔲 Planned |
| 2 | Split PDF | Tanmay | 🔲 Planned |
| 3 | Extract Pages | Tanmay | 🔲 Planned |
| 4 | Rotate Pages | Tanmay | 🔲 Planned |
| 5 | Reorder Pages | Tanmay | 🔲 Planned |
| 6 | Organize PDFs | Tanmay | 🔲 Planned |
| 7 | Compress PDF | Nishit | 🔲 Planned |
| 8 | Add Watermark | Nishit | 🔲 Planned |
| 9 | Remove Watermark | Nishit | 🔲 Planned |
| 10 | Add Password | Nishit | 🔲 Planned |
| 11 | Remove Password | Nishit | 🔲 Planned |
| 12 | Add Signature | Nishit | 🔲 Planned |
| 13 | Scan Images to PDF | Tanish | 🔲 Planned |
| 14 | Extract Text | Tanish | 🔲 Planned |
| 15 | Search PDF | Tanish | 🔲 Planned |
| 16 | PDF to Images | Tanish | 🔲 Planned |
| 17 | Images to PDF | Tanish | 🔲 Planned |
| 18 | Batch Processing | Tanish | 🔲 Planned |
| — | View Processing Logs | Shared | ✅ Logger ready |
| — | Exit | GUI-only | — |

## Architecture

```
Pdf_project/
├── run.py                      # Top-level runner
├── requirements.txt            # Pinned dependencies
├── .gitignore
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── logger.py           # Shared logger (FROZEN after Phase 1)
│   │
│   ├── gui/                    # GUI package (Phase 7-8)
│   │   └── __init__.py
│   │
│   └── modules/                # Feature modules (one folder per feature)
│       ├── __init__.py
│       ├── merge_pdf/          # Tanmay
│       ├── split_pdf/          # Tanmay
│       ├── extract_pages/      # Tanmay
│       ├── rotate_pages/       # Tanmay
│       ├── reorder_pages/      # Tanmay
│       ├── organize_pdf/       # Tanmay
│       ├── compress_pdf/       # Nishit
│       ├── watermark_add/      # Nishit
│       ├── watermark_remove/   # Nishit
│       ├── password_add/       # Nishit
│       ├── password_remove/    # Nishit
│       ├── signature_add/      # Nishit
│       ├── scan_to_pdf/        # Tanish
│       ├── extract_text/       # Tanish
│       ├── search_pdf/         # Tanish
│       ├── pdf_to_image/       # Tanish
│       ├── image_to_pdf/       # Tanish
│       └── batch_process/      # Tanish (built last)
│
├── tests/                      # One test file per feature module
│
└── logs/                       # Runtime logs (git-ignored)
    └── processing.log
```

## Setup

```bash
# Clone the repository
git clone https://github.com/Tomeseto/Pdf_project.git
cd Pdf_project

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

## Running Tests

```bash
# Run all tests
pytest -v

# Run tests for a specific module
pytest tests/test_merge.py -v
```

## Shared Logger API

All feature modules log their actions via `app.core.logger`:

```python
from app.core.logger import log_event, STATUS_SUCCESS, STATUS_FAILURE

# Log a successful operation
log_event("merge_pdf", "merge_files", STATUS_SUCCESS, "Merged 3 files -> output.pdf")

# Log a failure
log_event("compress_pdf", "compress", STATUS_FAILURE, "File not found: input.pdf")
```

The logger is **frozen after Phase 1** — its public API (`log_event`, `get_recent_events`, `clear_log`) must not be modified.

## Development Rules

1. **Python only** — no APIs, no cloud services, fully offline.
2. **Modular architecture** — one folder per feature, feature logic never in GUI code.
3. **No cross-editing** — developers must never modify another developer's module or test files.
4. **Structured errors** — every public function catches exceptions and returns structured results.
5. **Feature branches** — never commit directly to `main`.

## Dependencies

| Library | Purpose |
|---|---|
| pypdf | PDF manipulation (merge, split, rotate, encrypt, etc.) |
| PyMuPDF | Text extraction, search, page rendering |
| pdfplumber | Fallback text/layout extraction |
| Pillow | Image handling (scan, convert) |
| reportlab | Watermark and signature overlay generation |
| pytest | Testing framework |

## License

This project is for educational purposes.
