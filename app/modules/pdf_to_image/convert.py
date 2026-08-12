import os
import fitz
from PIL import Image
from app.core.logger import log_event, STATUS_SUCCESS, STATUS_FAILURE

def pdf_to_images(
    input_file: str,
    output_directory: str,
    image_format: str = "png"
) -> list[str]:
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"File not found: {input_file}")
            
        if image_format not in {"png", "jpeg"}:
            raise ValueError(f"Invalid image format: {image_format}. Must be 'png' or 'jpeg'")
            
        os.makedirs(output_directory, exist_ok=True)
        
        output_files = []
        doc = fitz.open(input_file)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            
            filename = f"page_{page_num + 1:03d}.{image_format}"
            filepath = os.path.join(output_directory, filename)
            
            if image_format == "png":
                pix.save(filepath)
            elif image_format == "jpeg":
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.save(filepath, "JPEG", quality=95)
                
            output_files.append(filepath)
            
        doc.close()
        
        log_event("pdf_to_image", "convert", STATUS_SUCCESS, f"Converted {input_file} to {len(output_files)} images")
        return output_files
        
    except (FileNotFoundError, ValueError):
        raise
    except Exception as e:
        log_event("pdf_to_image", "convert", STATUS_FAILURE, str(e))
        raise RuntimeError(f"Failed to convert PDF to images: {e}") from e
