import os
import pytest
import pypdf
from reportlab.pdfgen import canvas
from io import BytesIO
from app.modules.watermark_remove import remove_watermark


@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)

@pytest.fixture
def watermarked_pdf(sample_pdf, tmp_path):
    output_path = tmp_path / "watermarked.pdf"
    # Actually add watermark using pypdf directly with text "TEST" for simpler detection in tests
    writer = pypdf.PdfWriter()
    reader = pypdf.PdfReader(sample_pdf)
    page = reader.pages[0]
    
    packet = BytesIO()
    c = canvas.Canvas(packet)
    c.drawString(100, 100, "TEST")
    c.save()
    packet.seek(0)
    
    watermark = pypdf.PdfReader(packet).pages[0]
    page.merge_page(watermark)
    writer.add_page(page)
    
    with open(output_path, "wb") as f:
        writer.write(f)
    return str(output_path)

def test_remove_known_watermark(watermarked_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    # Our simple implementation looks for "TEST"
    remove_watermark(watermarked_pdf, output_path, "TEST")
    
    assert os.path.exists(output_path)
    # Check if "TEST" is removed
    reader = pypdf.PdfReader(output_path)
    page = reader.pages[0]
    content = page.get_contents()
    if content:
        data = content.get_data()
        assert b"TEST" not in data

def test_remove_no_watermark(sample_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    remove_watermark(sample_pdf, output_path, "NONEXISTENT")
    
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0

def test_remove_wrong_text(watermarked_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    remove_watermark(watermarked_pdf, output_path, "WRONG")
    
    assert os.path.exists(output_path)
    # Original text should still be there
    reader = pypdf.PdfReader(output_path)
    page = reader.pages[0]
    content = page.get_contents()
    if content:
        assert b"TEST" in content.get_data()

def test_remove_missing_file(tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(FileNotFoundError):
        remove_watermark("nonexistent.pdf", output_path, "TEST")
