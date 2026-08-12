import os
import pypdf
from pypdf.generic import ContentStream
from app.core.logger import log_event, STATUS_SUCCESS, STATUS_FAILURE, STATUS_WARNING

def remove_watermark(
    input_file: str,
    output_file: str,
    watermark_text: str | None = None
) -> str:
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
            
        reader = pypdf.PdfReader(input_file)
        writer = pypdf.PdfWriter()
        
        watermark_found = False
        
        for page in reader.pages:
            content_object = page.get_contents()
            if content_object:
                content = ContentStream(content_object, reader)
                
                new_operations = []
                for operands, operator in content.operations:
                    # Very basic text removal for exact matches
                    is_watermark = False
                    if watermark_text and operator == b"Tj":
                        text = operands[0]
                        if isinstance(text, str) and watermark_text in text:
                            is_watermark = True
                        elif isinstance(text, bytes) and watermark_text.encode('utf-8') in text:
                            is_watermark = True
                            
                    # Note: for advanced cases or missing watermark_text, it's best-effort.
                    # We might search for XObjects that are common to overlays, but we'll stick to basic for now
                    
                    if is_watermark:
                        watermark_found = True
                        continue
                        
                    new_operations.append((operands, operator))
                    
                content.operations = new_operations
                page.replace_contents(content)
                
            writer.add_page(page)
            
        with open(output_file, "wb") as f:
            writer.write(f)
            
        if not watermark_found:
            log_event("watermark_remove", "remove", STATUS_WARNING, "No watermark detected")
        else:
            log_event("watermark_remove", "remove", STATUS_SUCCESS, f"Removed watermark from {input_file} -> {output_file}")
            
        return output_file
        
    except (ValueError, FileNotFoundError):
        raise
    except Exception as e:
        log_event("watermark_remove", "remove", STATUS_FAILURE, str(e))
        raise RuntimeError(f"Failed to remove watermark: {e}") from e
