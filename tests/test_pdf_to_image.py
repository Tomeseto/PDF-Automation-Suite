import os
import pytest
import fitz
from app.modules.pdf_to_image import pdf_to_images

@pytest.fixture
def test_pdf(tmp_path):
    pdf = tmp_path / "test.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(pdf))
    doc.close()
    return str(pdf)

@pytest.fixture
def multi_pdf(tmp_path):
    pdf = tmp_path / "multi.pdf"
    doc = fitz.open()
    for _ in range(3):
        doc.new_page()
    doc.save(str(pdf))
    doc.close()
    return str(pdf)

def test_convert_single_page(test_pdf, tmp_path):
    out_dir = tmp_path / "out"
    res = pdf_to_images(test_pdf, str(out_dir))
    assert len(res) == 1
    assert os.path.exists(res[0])

def test_convert_multipage(multi_pdf, tmp_path):
    out_dir = tmp_path / "out"
    res = pdf_to_images(multi_pdf, str(out_dir))
    assert len(res) == 3
    for path in res:
        assert os.path.exists(path)

def test_convert_png(test_pdf, tmp_path):
    out_dir = tmp_path / "out"
    res = pdf_to_images(test_pdf, str(out_dir), image_format="png")
    assert res[0].endswith(".png")

def test_convert_jpeg(test_pdf, tmp_path):
    out_dir = tmp_path / "out"
    res = pdf_to_images(test_pdf, str(out_dir), image_format="jpeg")
    assert res[0].endswith(".jpeg")

def test_convert_filenames(multi_pdf, tmp_path):
    out_dir = tmp_path / "out"
    res = pdf_to_images(multi_pdf, str(out_dir))
    basenames = [os.path.basename(p) for p in res]
    assert basenames == ["page_001.png", "page_002.png", "page_003.png"]

def test_convert_invalid_format(test_pdf, tmp_path):
    out_dir = tmp_path / "out"
    with pytest.raises(ValueError):
        pdf_to_images(test_pdf, str(out_dir), image_format="bmp")

def test_convert_invalid_pdf(tmp_path):
    invalid = tmp_path / "invalid.pdf"
    invalid.write_text("not a pdf")
    out_dir = tmp_path / "out"
    with pytest.raises(RuntimeError):
        pdf_to_images(str(invalid), str(out_dir))

def test_convert_missing_file(tmp_path):
    out_dir = tmp_path / "out"
    with pytest.raises(FileNotFoundError):
        pdf_to_images(str(tmp_path / "missing.pdf"), str(out_dir))
