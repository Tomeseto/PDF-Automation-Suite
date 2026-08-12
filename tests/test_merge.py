"""Tests for app.modules.merge_pdf"""

import os

import pypdf
import pytest

from app.modules.merge_pdf import merge_pdfs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pdf(path: str, num_pages: int = 1, text: str = "test") -> str:
    """Create a minimal valid PDF with *num_pages* pages and write to *path*."""
    writer = pypdf.PdfWriter()
    for _ in range(num_pages):
        page = pypdf.PageObject.create_blank_page(width=612, height=792)
        writer.add_page(page)
    with open(path, "wb") as f:
        writer.write(f)
    return path


def _page_count(path: str) -> int:
    return len(pypdf.PdfReader(path).pages)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMergeTwoPDFs:
    def test_output_exists(self, tmp_path):
        a = _make_pdf(str(tmp_path / "a.pdf"), num_pages=2)
        b = _make_pdf(str(tmp_path / "b.pdf"), num_pages=3)
        out = str(tmp_path / "merged.pdf")
        result = merge_pdfs([a, b], out)
        assert os.path.isfile(result)

    def test_page_count_combined(self, tmp_path):
        a = _make_pdf(str(tmp_path / "a.pdf"), num_pages=2)
        b = _make_pdf(str(tmp_path / "b.pdf"), num_pages=3)
        out = str(tmp_path / "merged.pdf")
        merge_pdfs([a, b], out)
        assert _page_count(out) == 5

    def test_returns_absolute_path(self, tmp_path):
        a = _make_pdf(str(tmp_path / "a.pdf"))
        b = _make_pdf(str(tmp_path / "b.pdf"))
        out = str(tmp_path / "merged.pdf")
        result = merge_pdfs([a, b], out)
        assert os.path.isabs(result)


class TestMergeManyPDFs:
    def test_order_preserved_page_count(self, tmp_path):
        paths = [_make_pdf(str(tmp_path / f"f{i}.pdf"), num_pages=i + 1) for i in range(5)]
        out = str(tmp_path / "merged.pdf")
        merge_pdfs(paths, out)
        # Total pages: 1+2+3+4+5 = 15
        assert _page_count(out) == 15


class TestMergeInvalidFile:
    def test_corrupt_pdf_raises_runtime_error(self, tmp_path):
        good = _make_pdf(str(tmp_path / "good.pdf"))
        bad = tmp_path / "bad.pdf"
        bad.write_bytes(b"not a pdf at all")
        with pytest.raises(RuntimeError, match="corrupt"):
            merge_pdfs([good, str(bad)], str(tmp_path / "out.pdf"))


class TestMergeMissingFile:
    def test_missing_file_raises_file_not_found(self, tmp_path):
        good = _make_pdf(str(tmp_path / "good.pdf"))
        with pytest.raises(FileNotFoundError):
            merge_pdfs([good, "/nonexistent/path/missing.pdf"], str(tmp_path / "out.pdf"))


class TestMergeEmptyList:
    def test_empty_list_raises_value_error(self, tmp_path):
        with pytest.raises(ValueError):
            merge_pdfs([], str(tmp_path / "out.pdf"))


class TestMergeOverwriteProtection:
    def test_existing_output_no_overwrite_raises(self, tmp_path):
        a = _make_pdf(str(tmp_path / "a.pdf"))
        out = str(tmp_path / "out.pdf")
        _make_pdf(out)  # pre-create the output
        with pytest.raises(FileExistsError):
            merge_pdfs([a], out, overwrite=False)

    def test_existing_output_with_overwrite_succeeds(self, tmp_path):
        a = _make_pdf(str(tmp_path / "a.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        _make_pdf(out, num_pages=1)  # pre-create with 1 page
        merge_pdfs([a], out, overwrite=True)
        assert _page_count(out) == 3
