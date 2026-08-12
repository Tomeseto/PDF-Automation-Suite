import os
from PIL import Image
from app.core.logger import log_event, STATUS_SUCCESS, STATUS_FAILURE

def images_to_pdf(image_files: list[str], output_file: str) -> str:
    try:
        if not image_files:
            raise ValueError("image_files list cannot be empty")
            
        images = []
        for file in image_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"File not found: {file}")
            
            img = Image.open(file)
            img.verify()
            
            img = Image.open(file)
            img = img.convert("RGB")
            images.append(img)
            
        images[0].save(
            output_file, "PDF",
            save_all=True,
            append_images=images[1:],
            resolution=100.0
        )
        
        details = f"Converted {len(image_files)} images to {output_file}"
        log_event("image_to_pdf", "images_to_pdf", STATUS_SUCCESS, details)
        return output_file
        
    except (ValueError, FileNotFoundError):
        raise
    except Exception as e:
        log_event("image_to_pdf", "images_to_pdf", STATUS_FAILURE, str(e))
        raise RuntimeError(f"Failed to convert images to PDF: {e}") from e
