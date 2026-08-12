import pytest
import fitz
from app.modules.extract_text import extract_text

@pytest.fixture
def test_pdf(tmp_path):
    pdf = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello World")
    doc.save(str(pdf))
    doc.close()
    return str(pdf)

@pytest.fixture
def empty_pdf(tmp_path):
    pdf = tmp_path / "empty.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(pdf))
    doc.close()
    return str(pdf)

def test_extract_normal(test_pdf):
    res = extract_text(test_pdf)
    assert 1 in res
    assert "Hello World" in res[1]

def test_extract_multipage(tmp_path):
    pdf = tmp_path / "multi.pdf"
    doc = fitz.open()
    for i in range(3):
        p = doc.new_page()
        p.insert_text((50,50), f"Page {i+1}")
    doc.save(str(pdf))
    doc.close()
    
    res = extract_text(str(pdf))
    assert list(res.keys()) == [1, 2, 3]
    assert "Page 1" in res[1]

def test_extract_empty_text(empty_pdf):
    res = extract_text(empty_pdf)
    assert res[1] == ""

def test_extract_invalid_pdf(tmp_path):
    invalid = tmp_path / "invalid.pdf"
    invalid.write_text("not a pdf")
    with pytest.raises(RuntimeError):
        extract_text(str(invalid))

def test_extract_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_text(str(tmp_path / "missing.pdf"))
