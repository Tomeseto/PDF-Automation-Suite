import os
import pypdf
from app.core.logger import log_event, STATUS_SUCCESS, STATUS_FAILURE, STATUS_WARNING

def add_password(
    input_file: str,
    output_file: str,
    user_password: str,
    owner_password: str | None = None
) -> str:
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
            
        if not user_password:
            raise ValueError("User password cannot be empty")
            
        if owner_password is None:
            owner_password = user_password
            
        reader = pypdf.PdfReader(input_file)
        
        # Check if already encrypted
        if reader.is_encrypted:
            log_event("password_add", "encrypt", STATUS_WARNING, f"File is already encrypted: {input_file}")
            # Depending on requirements, we might raise or handle it. Let's raise.
            raise ValueError("Input PDF is already encrypted")
            
        writer = pypdf.PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        writer.encrypt(user_password=user_password, owner_password=owner_password, algorithm="AES-256")
        
        with open(output_file, "wb") as f:
            writer.write(f)
            
        log_event("password_add", "encrypt", STATUS_SUCCESS, f"Encrypted {input_file} -> {output_file}")
        return output_file
        
    except (ValueError, FileNotFoundError):
        raise
    except Exception as e:
        # DO NOT log the exception message directly if it could contain the password,
        # but built-in exceptions for this process won't. Still, better safe than sorry.
        log_event("password_add", "encrypt", STATUS_FAILURE, "Failed to encrypt PDF")
        raise RuntimeError(f"Failed to encrypt PDF: {e}") from e
