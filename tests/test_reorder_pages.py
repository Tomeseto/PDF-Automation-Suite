"""Tests for app.modules.reorder_pages"""

import os

import pypdf
import pytest

from app.modules.reorder_pages import reorder_pages


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pdf(path: str, num_pages: int = 4) -> str:
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


class TestReorderSimpleSwap:
    def test_output_exists(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        result = reorder_pages(src, out, [2, 1, 3])
        assert os.path.isfile(result)

    def test_page_count_preserved(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        reorder_pages(src, out, [2, 1, 3])
        assert _page_count(out) == 3

    def test_returns_absolute_path(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        result = reorder_pages(src, out, [3, 2, 1])
        assert os.path.isabs(result)


class TestReorderFullReverse:
    def test_reversed_page_count_preserved(self, tmp_path):
        n = 5
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=n)
        out = str(tmp_path / "out.pdf")
        reorder_pages(src, out, list(range(n, 0, -1)))
        assert _page_count(out) == n


class TestReorderInvalidPermutation:
    def test_missing_page_index(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=4)
        out = str(tmp_path / "out.pdf")
        # [1, 2, 3] is missing page 4
        with pytest.raises(ValueError):
            reorder_pages(src, out, [1, 2, 3])

    def test_duplicate_index(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        # [1, 1, 3] duplicates page 1 and omits page 2
        with pytest.raises(ValueError):
            reorder_pages(src, out, [1, 1, 3])

    def test_out_of_range_index(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        # [1, 2, 99] references a non-existent page
        with pytest.raises(ValueError):
            reorder_pages(src, out, [1, 2, 99])

    def test_wrong_length_too_short(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=4)
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError):
            reorder_pages(src, out, [1, 2])

    def test_wrong_length_too_long(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError):
            reorder_pages(src, out, [1, 2, 3, 4, 5])


class TestReorderMissingFile:
    def test_missing_file_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            reorder_pages("/no/such/file.pdf", str(tmp_path / "out.pdf"), [1, 2, 3])
