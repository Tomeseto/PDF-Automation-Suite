import os
import pytest
import pypdf
from app.modules.compress_pdf import compress_pdf

@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)

@pytest.fixture
def corrupt_pdf(tmp_path):
    pdf_path = tmp_path / "corrupt.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"not a valid pdf")
    return str(pdf_path)

def test_compress_succeeds(sample_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    compress_pdf(sample_pdf, output_path)
    assert os.path.exists(output_path)

def test_compress_returns_sizes(sample_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    result = compress_pdf(sample_pdf, output_path)
    assert "original_size" in result
    assert "compressed_size" in result
    assert result["output_path"] == output_path
    assert result["original_size"] > 0
    assert result["compressed_size"] > 0

def test_compress_original_unchanged(sample_pdf, tmp_path):
    original_size = os.path.getsize(sample_pdf)
    with open(sample_pdf, "rb") as f:
        original_content = f.read()
        
    output_path = str(tmp_path / "output.pdf")
    compress_pdf(sample_pdf, output_path)
    
    assert os.path.getsize(sample_pdf) == original_size
    with open(sample_pdf, "rb") as f:
        assert f.read() == original_content

def test_compress_invalid_pdf(corrupt_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(RuntimeError, match="Failed to compress PDF"):
        compress_pdf(corrupt_pdf, output_path)

def test_compress_missing_file(tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(FileNotFoundError):
        compress_pdf("nonexistent.pdf", output_path)
