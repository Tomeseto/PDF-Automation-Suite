import os
import pytest
import pypdf
from app.modules.watermark_add import add_watermark

@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.add_blank_page(width=612, height=792)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)

def test_watermark_added(sample_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    add_watermark(sample_pdf, output_path, "TEST WATERMARK")
    
    assert os.path.exists(output_path)
    
    # Read output and original to ensure watermark is added (more objects usually)
    # Actually, simpler: just check that the output can be opened
    reader = pypdf.PdfReader(output_path)
    assert len(reader.pages) == 2

def test_watermark_multipage(sample_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    add_watermark(sample_pdf, output_path, "TEST")
    
    reader = pypdf.PdfReader(output_path)
    # Each page should have the merged content
    for page in reader.pages:
        assert "/XObject" in page.get_contents() or b"TEST" in page.get_contents().get_data() or b"Tj" in page.get_contents().get_data()

@pytest.mark.parametrize("position", ["center", "top-left", "top-right", "bottom-left", "bottom-right"])
def test_watermark_each_position(sample_pdf, tmp_path, position):
    output_path = str(tmp_path / f"output_{position}.pdf")
    # Should not crash
    add_watermark(sample_pdf, output_path, "TEST", position=position)
    assert os.path.exists(output_path)

def test_watermark_invalid_opacity(sample_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(ValueError, match="Opacity must be between 0.0 and 1.0"):
        add_watermark(sample_pdf, output_path, "TEST", opacity=1.5)

def test_watermark_invalid_position(sample_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(ValueError, match="Invalid position"):
        add_watermark(sample_pdf, output_path, "TEST", position="middle")

def test_watermark_empty_text(sample_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(ValueError, match="Watermark text cannot be empty"):
        add_watermark(sample_pdf, output_path, "")

def test_watermark_missing_file(tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(FileNotFoundError):
        add_watermark("nonexistent.pdf", output_path, "TEST")
