import os
import pytest
import pypdf
from PIL import Image
from app.modules.signature_add import add_signature

@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)

@pytest.fixture
def sample_image(tmp_path):
    img_path = tmp_path / "sig.png"
    img = Image.new('RGB', (100, 50), color='red')
    img.save(img_path)
    return str(img_path)

@pytest.fixture
def invalid_image(tmp_path):
    img_path = tmp_path / "sig.txt"
    with open(img_path, "w") as f:
        f.write("not an image")
    return str(img_path)

def test_signature_placed(sample_pdf, sample_image, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    add_signature(sample_pdf, output_path, sample_image, position=(100, 100), page_number=1)
    
    assert os.path.exists(output_path)
    reader = pypdf.PdfReader(output_path)
    assert len(reader.pages) == 1
    # Check that there is an XObject (image) in the page resources
    page = reader.pages[0]
    assert "/XObject" in page.get_contents() or b"Do" in page.get_contents().get_data()

def test_signature_invalid_page(sample_pdf, sample_image, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(ValueError, match="out of range"):
        add_signature(sample_pdf, output_path, sample_image, position=(100, 100), page_number=2)
    with pytest.raises(ValueError, match="out of range"):
        add_signature(sample_pdf, output_path, sample_image, position=(100, 100), page_number=0)

def test_signature_invalid_image(sample_pdf, invalid_image, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(ValueError, match="Invalid image file"):
        add_signature(sample_pdf, output_path, invalid_image, position=(100, 100), page_number=1)

def test_signature_missing_pdf(sample_image, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(FileNotFoundError):
        add_signature("nonexistent.pdf", output_path, sample_image, position=(100, 100), page_number=1)

def test_signature_missing_image(sample_pdf, tmp_path):
    output_path = str(tmp_path / "output.pdf")
    with pytest.raises(FileNotFoundError):
        add_signature(sample_pdf, output_path, "nonexistent.png", position=(100, 100), page_number=1)
