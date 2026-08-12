"""Tests for app.modules.split_pdf"""

import os

import pypdf
import pytest

from app.modules.split_pdf import split_pdf


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


class TestSplitSingleRange:
    def test_output_file_created(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out_dir = str(tmp_path / "out")
        result = split_pdf(src, out_dir, [(1, 3)])
        assert len(result) == 1
        assert os.path.isfile(result[0])

    def test_correct_page_count(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out_dir = str(tmp_path / "out")
        result = split_pdf(src, out_dir, [(1, 3)])
        assert _page_count(result[0]) == 3

    def test_returns_absolute_paths(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out_dir = str(tmp_path / "out")
        result = split_pdf(src, out_dir, [(2, 4)])
        assert os.path.isabs(result[0])


class TestSplitMultipleRanges:
    def test_two_output_files(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out_dir = str(tmp_path / "out")
        result = split_pdf(src, out_dir, [(1, 2), (4, 5)])
        assert len(result) == 2

    def test_correct_page_counts(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=6)
        out_dir = str(tmp_path / "out")
        result = split_pdf(src, out_dir, [(1, 2), (4, 6)])
        assert _page_count(result[0]) == 2
        assert _page_count(result[1]) == 3

    def test_output_filenames(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out_dir = str(tmp_path / "out")
        result = split_pdf(src, out_dir, [(1, 2), (4, 5)])
        basenames = [os.path.basename(p) for p in result]
        assert "split_1-2.pdf" in basenames
        assert "split_4-5.pdf" in basenames


class TestSplitOutOfBoundsRange:
    def test_end_exceeds_pages(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out_dir = str(tmp_path / "out")
        with pytest.raises(ValueError, match="out of bounds"):
            split_pdf(src, out_dir, [(1, 99)])

    def test_start_zero(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out_dir = str(tmp_path / "out")
        with pytest.raises(ValueError):
            split_pdf(src, out_dir, [(0, 2)])

    def test_start_greater_than_end(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out_dir = str(tmp_path / "out")
        with pytest.raises(ValueError, match="start must be"):
            split_pdf(src, out_dir, [(4, 2)])


class TestSplitOverlappingRanges:
    def test_overlapping_raises_value_error(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out_dir = str(tmp_path / "out")
        with pytest.raises(ValueError, match="[Oo]verlapping"):
            split_pdf(src, out_dir, [(1, 3), (3, 5)])


class TestSplitInvalidPDF:
    def test_corrupt_pdf_raises_runtime_error(self, tmp_path):
        bad = tmp_path / "bad.pdf"
        bad.write_bytes(b"this is not a pdf")
        out_dir = str(tmp_path / "out")
        with pytest.raises(RuntimeError):
            split_pdf(str(bad), out_dir, [(1, 1)])


class TestSplitMissingFile:
    def test_missing_file_raises_file_not_found(self, tmp_path):
        out_dir = str(tmp_path / "out")
        with pytest.raises(FileNotFoundError):
            split_pdf("/no/such/file.pdf", out_dir, [(1, 1)])


class TestSplitEmptyRanges:
    def test_empty_ranges_raises_value_error(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out_dir = str(tmp_path / "out")
        with pytest.raises(ValueError):
            split_pdf(src, out_dir, [])
