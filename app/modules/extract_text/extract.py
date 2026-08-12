import os
import fitz
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
from app.core.logger import log_event, STATUS_SUCCESS, STATUS_FAILURE

def extract_text(pdf_path: str) -> dict[int, str]:
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")
            
        result = {}
        # This will raise RuntimeError on corrupt PDF
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            
            if not text and pdfplumber:
                try:
                    with pdfplumber.open(pdf_path) as pdf:
                        if page_num < len(pdf.pages):
                            p_page = pdf.pages[page_num]
                            extracted = p_page.extract_text()
                            text = extracted.strip() if extracted else ""
                except Exception:
                    pass
                    
            result[page_num + 1] = text
        doc.close()
        
        log_event("extract_text", "extract", STATUS_SUCCESS, f"Extracted text from {pdf_path}")
        return result
        
    except FileNotFoundError:
        raise
    except Exception as e:
        log_event("extract_text", "extract", STATUS_FAILURE, str(e))
        raise RuntimeError(f"Failed to extract text: {e}") from e
