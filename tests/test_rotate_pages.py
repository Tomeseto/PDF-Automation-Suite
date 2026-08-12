"""Tests for app.modules.rotate_pages"""

import os

import pypdf
import pytest

from app.modules.rotate_pages import rotate_pages


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pdf(path: str, num_pages: int = 3) -> str:
    writer = pypdf.PdfWriter()
    for _ in range(num_pages):
        writer.add_page(pypdf.PageObject.create_blank_page(width=612, height=792))
    with open(path, "wb") as f:
        writer.write(f)
    return path


def _get_rotation(path: str, page_number: int = 0) -> int:
    """Return the rotation value (in degrees) of a page (0-indexed)."""
    reader = pypdf.PdfReader(path)
    page = reader.pages[page_number]
    return page.get("/Rotate", 0)


def _page_count(path: str) -> int:
    return len(pypdf.PdfReader(path).pages)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestRotateAllPages:
    def test_output_exists(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        result = rotate_pages(src, out, angle=90)
        assert os.path.isfile(result)

    def test_page_count_preserved(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        rotate_pages(src, out, angle=90)
        assert _page_count(out) == 3

    def test_all_pages_rotated_90(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        rotate_pages(src, out, angle=90)
        reader = pypdf.PdfReader(out)
        for page in reader.pages:
            assert page.get("/Rotate", 0) == 90

    def test_rotate_180(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=2)
        out = str(tmp_path / "out.pdf")
        rotate_pages(src, out, angle=180)
        reader = pypdf.PdfReader(out)
        for page in reader.pages:
            assert page.get("/Rotate", 0) == 180

    def test_rotate_270(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=2)
        out = str(tmp_path / "out.pdf")
        rotate_pages(src, out, angle=270)
        reader = pypdf.PdfReader(out)
        for page in reader.pages:
            assert page.get("/Rotate", 0) == 270


class TestRotateSubset:
    def test_only_selected_pages_rotated(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=4)
        out = str(tmp_path / "out.pdf")
        rotate_pages(src, out, angle=180, pages=[1, 3])
        reader = pypdf.PdfReader(out)
        assert reader.pages[0].get("/Rotate", 0) == 180  # page 1 rotated
        assert reader.pages[1].get("/Rotate", 0) == 0    # page 2 untouched
        assert reader.pages[2].get("/Rotate", 0) == 180  # page 3 rotated
        assert reader.pages[3].get("/Rotate", 0) == 0    # page 4 untouched

    def test_returns_absolute_path(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"))
        out = str(tmp_path / "out.pdf")
        result = rotate_pages(src, out, angle=90, pages=[1])
        assert os.path.isabs(result)


class TestRotateInvalidAngle:
    def test_angle_45_raises_value_error(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"))
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError, match="angle must be"):
            rotate_pages(src, out, angle=45)

    def test_angle_0_raises_value_error(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"))
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError):
            rotate_pages(src, out, angle=0)

    def test_angle_360_raises_value_error(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"))
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError):
            rotate_pages(src, out, angle=360)


class TestRotateOutOfRangePage:
    def test_page_99_raises_value_error(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError, match="out of range"):
            rotate_pages(src, out, angle=90, pages=[99])

    def test_page_0_raises_value_error(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError):
            rotate_pages(src, out, angle=90, pages=[0])


class TestRotateMissingFile:
    def test_missing_file_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            rotate_pages("/no/such/file.pdf", str(tmp_path / "out.pdf"), angle=90)
