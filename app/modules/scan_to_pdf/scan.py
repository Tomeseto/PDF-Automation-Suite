import os
from PIL import Image, ImageOps
from app.core.logger import log_event, STATUS_SUCCESS, STATUS_FAILURE

def scan_images_to_pdf(
    image_files: list[str],
    output_file: str,
    enhance: bool = True
) -> str:
    try:
        if not image_files:
            raise ValueError("image_files list cannot be empty")
        
        images = []
        for file in image_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"File not found: {file}")
            
            img = Image.open(file)
            img.verify() # Verify valid image
            img = Image.open(file) # Re-open after verify
            
            if enhance:
                img = img.convert("L")
                img = ImageOps.autocontrast(img, cutoff=1)
                # Deskew: best-effort. Skipping complex deskew logic to avoid numpy/OpenCV dependency issues,
                # as instruction allows skipping gracefully.
                try:
                    # Simple thresholding to mimic scan
                    img = img.point(lambda x: 0 if x < 128 else 255, '1')
                except Exception:
                    pass # Skip on failure
                
            img = img.convert("RGB")
            images.append(img)
            
        images[0].save(output_file, "PDF", save_all=True, append_images=images[1:])
        
        details = f"Scanned {len(image_files)} images to {output_file}"
        log_event("scan_to_pdf", "scan_images", STATUS_SUCCESS, details)
        return output_file
        
    except (ValueError, FileNotFoundError):
        raise
    except Exception as e:
        log_event("scan_to_pdf", "scan_images", STATUS_FAILURE, str(e))
        raise RuntimeError(f"Failed to scan images to PDF: {e}") from e
