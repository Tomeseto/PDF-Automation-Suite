"""Tests for app.modules.extract_pages"""

import os

import pypdf
import pytest

from app.modules.extract_pages import extract_pages


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pdf(path: str, num_pages: int = 5) -> str:
    writer = pypdf.PdfWriter()
    for _ in range(num_pages):
        writer.add_page(pypdf.PageObject.create_blank_page(width=612, height=792))
    with open(path, "wb") as f:
        writer.write(f)
    return path


def _page_count(path: str) -> int:
    return len(pypdf.PdfReader(path).pages)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestExtractSinglePage:
    def test_output_exists(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        result = extract_pages(src, out, [2])
        assert os.path.isfile(result)

    def test_single_page_output(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        extract_pages(src, out, [2])
        assert _page_count(out) == 1

    def test_returns_absolute_path(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        result = extract_pages(src, out, [1])
        assert os.path.isabs(result)


class TestExtractMultipleNonContiguous:
    def test_three_non_contiguous_pages(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        extract_pages(src, out, [1, 3, 5])
        assert _page_count(out) == 3

    def test_order_preserved(self, tmp_path):
        # Extract pages in a specific order [5, 1, 3] — output should have 3 pages
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        extract_pages(src, out, [5, 1, 3])
        assert _page_count(out) == 3


class TestExtractDuplicatePages:
    def test_duplicates_deduplicated(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        # [1, 3, 1] should deduplicate to [1, 3] — 2 pages
        extract_pages(src, out, [1, 3, 1])
        assert _page_count(out) == 2

    def test_all_duplicates(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        extract_pages(src, out, [2, 2, 2])
        assert _page_count(out) == 1


class TestExtractInvalidPage:
    def test_page_too_large_raises_value_error(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError, match="out of range"):
            extract_pages(src, out, [99])

    def test_page_zero_raises_value_error(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError):
            extract_pages(src, out, [0])

    def test_empty_list_raises_value_error(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError):
            extract_pages(src, out, [])


class TestExtractMissingFile:
    def test_missing_file_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            extract_pages("/no/such/file.pdf", str(tmp_path / "out.pdf"), [1])
