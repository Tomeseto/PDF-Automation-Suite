import os
import pypdf
from app.core.logger import log_event, STATUS_SUCCESS, STATUS_FAILURE, STATUS_WARNING

def compress_pdf(input_file: str, output_file: str) -> dict:
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
            
        original_size = os.path.getsize(input_file)
        
        reader = pypdf.PdfReader(input_file)
        writer = pypdf.PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            page.compress_content_streams()
            
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
        
        with open(output_file, "wb") as f:
            writer.write(f)
            
        compressed_size = os.path.getsize(output_file)
        
        result = {
            "original_size": original_size,
            "compressed_size": compressed_size,
            "output_path": output_file
        }
        
        if compressed_size >= original_size:
            log_event("compress_pdf", "compress", STATUS_WARNING, "File could not be compressed further")
        else:
            log_event("compress_pdf", "compress", STATUS_SUCCESS, f"Compressed {input_file} to {output_file} ({original_size} -> {compressed_size} bytes)")
            
        return result
        
    except (ValueError, FileNotFoundError):
        raise
    except Exception as e:
        log_event("compress_pdf", "compress", STATUS_FAILURE, str(e))
        raise RuntimeError(f"Failed to compress PDF: {e}") from e
