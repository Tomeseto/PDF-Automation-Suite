"""
Batch operation registry.

Maps operation names to their corresponding module functions.
This file is the ONLY place in batch_process/ that imports
from other developers' modules. It imports only their public
API functions — never their internal files.
"""

from app.modules.merge_pdf import merge_pdfs
from app.modules.split_pdf import split_pdf
from app.modules.extract_pages import extract_pages
from app.modules.rotate_pages import rotate_pages
from app.modules.reorder_pages import reorder_pages
from app.modules.organize_pdf import organize_pdf
from app.modules.compress_pdf import compress_pdf
from app.modules.watermark_add import add_watermark
from app.modules.watermark_remove import remove_watermark
from app.modules.password_add import add_password
from app.modules.password_remove import remove_password
from app.modules.signature_add import add_signature
from app.modules.scan_to_pdf import scan_images_to_pdf
from app.modules.extract_text import extract_text
from app.modules.search_pdf import search_pdf
from app.modules.pdf_to_image import pdf_to_images
from app.modules.image_to_pdf import images_to_pdf

# Registry: operation_name -> (callable, description)
BATCH_OPERATIONS: dict[str, tuple] = {
    "merge":            (merge_pdfs, "Merge multiple PDFs"),
    "split":            (split_pdf, "Split PDF into ranges"),
    "extract_pages":    (extract_pages, "Extract specific pages"),
    "rotate":           (rotate_pages, "Rotate PDF pages"),
    "reorder":          (reorder_pages, "Reorder PDF pages"),
    "organize":         (organize_pdf, "Organize PDF pipeline"),
    "compress":         (compress_pdf, "Compress PDF"),
    "watermark_add":    (add_watermark, "Add watermark"),
    "watermark_remove": (remove_watermark, "Remove watermark"),
    "password_add":     (add_password, "Add password"),
    "password_remove":  (remove_password, "Remove password"),
    "signature":        (add_signature, "Add signature"),
    "scan_to_pdf":      (scan_images_to_pdf, "Scan images to PDF"),
    "extract_text":     (extract_text, "Extract text"),
    "search":           (search_pdf, "Search PDF"),
    "pdf_to_image":     (pdf_to_images, "Convert PDF to images"),
    "image_to_pdf":     (images_to_pdf, "Convert images to PDF"),
}
