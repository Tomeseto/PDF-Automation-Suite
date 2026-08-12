import os
from io import BytesIO
import pypdf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from app.core.logger import log_event, STATUS_SUCCESS, STATUS_FAILURE, STATUS_WARNING

def add_watermark(
    input_file: str,
    output_file: str,
    text: str,
    opacity: float = 0.3,
    position: str = "center"
) -> str:
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
            
        if not text:
            raise ValueError("Watermark text cannot be empty")
            
        if not (0.0 <= opacity <= 1.0):
            raise ValueError("Opacity must be between 0.0 and 1.0")
            
        valid_positions = {"center", "top-left", "top-right", "bottom-left", "bottom-right"}
        if position not in valid_positions:
            raise ValueError(f"Invalid position: {position}")
            
        reader = pypdf.PdfReader(input_file)
        writer = pypdf.PdfWriter()
        
        for page in reader.pages:
            # Get actual page dimensions
            mediabox = page.mediabox
            page_width = float(mediabox.width)
            page_height = float(mediabox.height)
            
            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=(page_width, page_height))
            c.setFillAlpha(opacity)
            c.setFont("Helvetica", 40)
            
            text_width = c.stringWidth(text, "Helvetica", 40)
            
            # Calculate coordinates
            if position == "center":
                x = (page_width - text_width) / 2
                y = page_height / 2
            elif position == "top-left":
                x = 36
                y = page_height - 36 - 40
            elif position == "top-right":
                x = page_width - text_width - 36
                y = page_height - 36 - 40
            elif position == "bottom-left":
                x = 36
                y = 36
            elif position == "bottom-right":
                x = page_width - text_width - 36
                y = 36
                
            c.drawString(x, y, text)
            c.save()
            packet.seek(0)
            
            watermark_page = pypdf.PdfReader(packet).pages[0]
            page.merge_page(watermark_page)
            writer.add_page(page)
            
        with open(output_file, "wb") as f:
            writer.write(f)
            
        log_event("watermark_add", "add", STATUS_SUCCESS, f"Added watermark to {input_file} -> {output_file}")
        return output_file
        
    except (ValueError, FileNotFoundError):
        raise
    except Exception as e:
        log_event("watermark_add", "add", STATUS_FAILURE, str(e))
        raise RuntimeError(f"Failed to add watermark: {e}") from e
