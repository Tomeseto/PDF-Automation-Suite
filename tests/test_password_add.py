import os
import pytest
import pypdf
from app.modules.password_add import add_password
from app.core.logger import LOG_FILE

@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)

@pytest.fixture
def encrypted_pdf(sample_pdf, tmp_path):
    pdf_path = tmp_path / "encrypted.pdf"
    writer = pypdf.PdfWriter()
    reader = pypdf.PdfReader(sample_pdf)
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt("mypassword")
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)

def test_password_added(sample_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    add_password(sample_pdf, output_path, "secret_password")
    
    assert os.path.exists(output_path)
    
    # Verify it is actually encrypted
    reader = pypdf.PdfReader(output_path)
    assert reader.is_encrypted
    
    # Attempting to read without password should fail
    with pytest.raises(pypdf.errors.FileNotDecryptedError):
        reader.pages[0]
        
    # Attempting to read with password should succeed
    reader.decrypt("secret_password")
    assert reader.pages[0] is not None

def test_password_empty_rejected(sample_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(ValueError, match="User password cannot be empty"):
        add_password(sample_pdf, output_path, "")

def test_password_already_encrypted(encrypted_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(ValueError, match="already encrypted"):
        add_password(encrypted_pdf, output_path, "new_password")

def test_password_missing_file(tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(FileNotFoundError):
        add_password("nonexistent.pdf", output_path, "secret")

def test_password_not_logged(sample_pdf, tmp_path):
    # Ensure log file exists or clean it
    if os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
        
    output_path = str(tmp_path / "output.pdf")
    test_password = "SUPER_SECRET_TEST_PASSWORD_123!"
    
    add_password(sample_pdf, output_path, test_password)
    
    # Read log file and assert password is not there
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            log_contents = f.read()
            assert test_password not in log_contents
