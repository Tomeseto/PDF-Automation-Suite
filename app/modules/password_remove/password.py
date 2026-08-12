import os
import pypdf
from app.core.logger import log_event, STATUS_SUCCESS, STATUS_FAILURE, STATUS_WARNING

def remove_password(input_file: str, output_file: str, password: str) -> str:
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
            
        reader = pypdf.PdfReader(input_file)
        
        if not reader.is_encrypted:
            # Not encrypted, copy to output
            writer = pypdf.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            with open(output_file, "wb") as f:
                writer.write(f)
            log_event("password_remove", "decrypt", STATUS_WARNING, "File was not encrypted")
            return output_file
            
        # Attempt decryption
        if reader.decrypt(password) == pypdf.PasswordType.NOT_DECRYPTED:
            raise ValueError("Incorrect password")
            
        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
            
        with open(output_file, "wb") as f:
            writer.write(f)
            
        log_event("password_remove", "decrypt", STATUS_SUCCESS, f"Decrypted {input_file} -> {output_file}")
        return output_file
        
    except (ValueError, FileNotFoundError):
        raise
    except Exception as e:
        log_event("password_remove", "decrypt", STATUS_FAILURE, "Failed to decrypt PDF")
        raise RuntimeError(f"Failed to remove password: {e}") from e
