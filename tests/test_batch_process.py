"""Tests for app.modules.batch_process"""

import os
import pypdf
import pytest

from app.modules.batch_process import batch_process


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pdf(path: str, num_pages: int = 2) -> str:
    writer = pypdf.PdfWriter()
    for _ in range(num_pages):
        writer.add_page(pypdf.PageObject.create_blank_page(width=612, height=792))
    with open(path, "wb") as f:
        writer.write(f)
    return path


def _make_corrupt_pdf(path: str) -> str:
    with open(path, "wb") as f:
        f.write(b"Not a real PDF file at all.")
    return path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_batch_unknown_operation(tmp_path):
    with pytest.raises(ValueError, match="Unknown operation"):
        batch_process("nonexistent", ["doc.pdf"], {}, str(tmp_path))


def test_batch_empty_input(tmp_path):
    with pytest.raises(ValueError, match="empty"):
        batch_process("compress", [], {}, str(tmp_path))


def test_batch_compress_3_files(tmp_path):
    out_dir = str(tmp_path / "out")
    f1 = _make_pdf(str(tmp_path / "doc1.pdf"))
    f2 = _make_pdf(str(tmp_path / "doc2.pdf"))
    f3 = _make_pdf(str(tmp_path / "doc3.pdf"))
    
    results = batch_process("compress", [f1, f2, f3], {}, out_dir)
    assert len(results) == 3
    assert all(r["status"] == "success" for r in results)


def test_batch_watermark(tmp_path):
    out_dir = str(tmp_path / "out")
    f1 = _make_pdf(str(tmp_path / "doc1.pdf"))
    f2 = _make_pdf(str(tmp_path / "doc2.pdf"))
    
    # Needs watermark_text based on add_watermark signature
    results = batch_process(
        "watermark_add", 
        [f1, f2], 
        {"text": "CONFIDENTIAL"}, 
        out_dir
    )
    assert len(results) == 2
    assert all(r["status"] == "success" for r in results)
    
    # Check outputs actually exist
    for r in results:
        assert os.path.isfile(r["result"])


def test_batch_password(tmp_path):
    out_dir = str(tmp_path / "out")
    f1 = _make_pdf(str(tmp_path / "doc1.pdf"))
    
    results = batch_process(
        "password_add", 
        [f1], 
        {"user_password": "secret_password"}, 
        out_dir
    )
    assert len(results) == 1
    assert results[0]["status"] == "success"
    
    # Check if the generated file is actually encrypted
    reader = pypdf.PdfReader(results[0]["result"])
    assert reader.is_encrypted


def test_batch_one_fails(tmp_path):
    out_dir = str(tmp_path / "out")
    f1 = _make_pdf(str(tmp_path / "doc1.pdf"))
    f2 = _make_corrupt_pdf(str(tmp_path / "doc2.pdf"))  # will fail
    f3 = _make_pdf(str(tmp_path / "doc3.pdf"))
    
    results = batch_process("compress", [f1, f2, f3], {}, out_dir)
    assert len(results) == 3
    
    assert results[0]["status"] == "success"
    assert results[1]["status"] == "failure"
    assert "error" in results[1]
    assert results[2]["status"] == "success"


def test_batch_continues_on_error(tmp_path):
    # Same logic as above: ensures a failure on file 2 doesn't stop file 3
    out_dir = str(tmp_path / "out")
    f1 = _make_corrupt_pdf(str(tmp_path / "bad.pdf"))
    f2 = _make_pdf(str(tmp_path / "good.pdf"))
    
    results = batch_process("compress", [f1, f2], {}, out_dir)
    assert len(results) == 2
    assert results[0]["status"] == "failure"
    assert results[1]["status"] == "success"
