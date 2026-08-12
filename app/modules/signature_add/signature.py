import os
import pypdf
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from app.core.logger import log_event, STATUS_SUCCESS, STATUS_FAILURE, STATUS_WARNING

def add_signature(
    input_file: str,
    output_file: str,
    signature_image: str,
    position: tuple[int, int],
    page_number: int
) -> str:
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
            
        if not os.path.exists(signature_image):
            raise FileNotFoundError(f"Signature image not found: {signature_image}")
            
        try:
            with Image.open(signature_image) as img:
                img.verify()
        except UnidentifiedImageError as e:
            raise ValueError(f"Invalid image file: {signature_image}") from e
            
        reader = pypdf.PdfReader(input_file)
        
        if page_number < 1 or page_number > len(reader.pages):
            raise ValueError(f"Page number {page_number} out of range (1-{len(reader.pages)})")
            
        writer = pypdf.PdfWriter()
        
        for i, page in enumerate(reader.pages):
            if i + 1 == page_number:
                mediabox = page.mediabox
                page_width = float(mediabox.width)
                page_height = float(mediabox.height)
                
                img_reader = ImageReader(signature_image)
                img_width, img_height = img_reader.getSize()
                
                packet = BytesIO()
                c = canvas.Canvas(packet, pagesize=(page_width, page_height))
                c.drawImage(img_reader, position[0], position[1], width=img_width, height=img_height, mask='auto')
                c.save()
                
                packet.seek(0)
                sig_page = pypdf.PdfReader(packet).pages[0]
                page.merge_page(sig_page)
                
            writer.add_page(page)
            
        with open(output_file, "wb") as f:
            writer.write(f)
            
        log_event("signature_add", "add", STATUS_SUCCESS, f"Added signature to {input_file} page {page_number} -> {output_file}")
        return output_file
        
    except (ValueError, FileNotFoundError):
        raise
    except Exception as e:
        log_event("signature_add", "add", STATUS_FAILURE, str(e))
        raise RuntimeError(f"Failed to add signature: {e}") from e
