import pytest
import fitz
from app.modules.search_pdf import search_pdf

@pytest.fixture
def test_pdf(tmp_path):
    pdf = tmp_path / "test.pdf"
    doc = fitz.open()
    
    p1 = doc.new_page()
    p1.insert_text((50, 50), "Hello World! This is a test for searching PDF documents.")
    
    p2 = doc.new_page()
    p2.insert_text((50, 50), "hello world again!")
    
    doc.save(str(pdf))
    doc.close()
    return str(pdf)

def test_search_exact_match(test_pdf):
    res = search_pdf(test_pdf, "searching PDF")
    assert len(res) == 1
    assert res[0]["page"] == 1
    assert "searching PDF" in res[0]["snippet"]

def test_search_case_insensitive(test_pdf):
    res = search_pdf(test_pdf, "hello", case_sensitive=False)
    assert len(res) == 2
    assert res[0]["page"] == 1
    assert res[1]["page"] == 2

def test_search_case_sensitive(test_pdf):
    res = search_pdf(test_pdf, "hello", case_sensitive=True)
    assert len(res) == 1
    assert res[0]["page"] == 2

def test_search_multiple_matches(test_pdf):
    res = search_pdf(test_pdf, "World")
    assert len(res) == 2

def test_search_no_matches(test_pdf):
    res = search_pdf(test_pdf, "Not found")
    assert len(res) == 0

def test_search_empty_query(test_pdf):
    with pytest.raises(ValueError):
        search_pdf(test_pdf, "")

def test_search_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        search_pdf(str(tmp_path / "missing.pdf"), "hello")
