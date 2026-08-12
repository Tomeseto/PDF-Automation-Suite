import os
import pytest
import pypdf
from app.modules.password_remove import remove_password
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
    writer.encrypt("correct_password")
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)

def test_remove_correct_password(encrypted_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    remove_password(encrypted_pdf, output_path, "correct_password")
    
    assert os.path.exists(output_path)
    reader = pypdf.PdfReader(output_path)
    assert not reader.is_encrypted
    assert len(reader.pages) == 1

def test_remove_incorrect_password(encrypted_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(ValueError, match="Incorrect password"):
        remove_password(encrypted_pdf, output_path, "wrong_password")

def test_remove_non_encrypted(sample_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    remove_password(sample_pdf, output_path, "any_password")
    
    assert os.path.exists(output_path)
    reader = pypdf.PdfReader(output_path)
    assert not reader.is_encrypted

def test_remove_missing_file(tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(FileNotFoundError):
        remove_password("nonexistent.pdf", output_path, "secret")

def test_password_not_logged(encrypted_pdf, tmp_path):
    # Ensure log file exists or clean it
    if os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
        
    output_path = str(tmp_path / "output.pdf")
    test_password = "correct_password"
    
    remove_password(encrypted_pdf, output_path, test_password)
    
    # Read log file and assert password is not there
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            log_contents = f.read()
            assert test_password not in log_contents
