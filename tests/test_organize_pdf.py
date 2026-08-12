"""Tests for app.modules.organize_pdf"""

import os

import pypdf
import pytest

from app.modules.organize_pdf import organize_pdf


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


def _get_rotation(path: str, page_idx: int = 0) -> int:
    reader = pypdf.PdfReader(path)
    return reader.pages[page_idx].get("/Rotate", 0)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestOrganizeSingleDelete:
    def test_delete_one_page(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        result = organize_pdf(src, out, [{"op": "delete", "pages": [3]}])
        assert os.path.isfile(result)
        assert _page_count(result) == 4

    def test_delete_multiple_pages(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        organize_pdf(src, out, [{"op": "delete", "pages": [1, 5]}])
        assert _page_count(out) == 3


class TestOrganizeSingleRotate:
    def test_rotate_page_1_by_90(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        organize_pdf(src, out, [{"op": "rotate", "pages": [1], "angle": 90}])
        assert _get_rotation(out, 0) == 90
        assert _get_rotation(out, 1) == 0  # page 2 untouched

    def test_rotate_all_pages(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        organize_pdf(src, out, [{"op": "rotate", "angle": 180}])
        reader = pypdf.PdfReader(out)
        for page in reader.pages:
            assert page.get("/Rotate", 0) == 180


class TestOrganizeChainedOperations:
    def test_delete_then_reorder(self, tmp_path):
        # 5-page PDF: delete page 3 (leaves pages [1,2,4,5]),
        # then reorder to [4,3,2,1] (reverses the 4 remaining)
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        ops = [
            {"op": "delete", "pages": [3]},
            {"op": "reorder", "order": [4, 3, 2, 1]},
        ]
        result = organize_pdf(src, out, ops)
        assert _page_count(result) == 4

    def test_delete_rotate_reorder(self, tmp_path):
        # 5-page PDF: delete p5 → 4 pages; rotate p1 by 90 → 4 pages;
        # reorder [2,1,3,4] → 4 pages
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=5)
        out = str(tmp_path / "out.pdf")
        ops = [
            {"op": "delete", "pages": [5]},
            {"op": "rotate", "pages": [1], "angle": 90},
            {"op": "reorder", "order": [2, 1, 3, 4]},
        ]
        result = organize_pdf(src, out, ops)
        assert _page_count(result) == 4
        # After reorder [2,1,3,4], the original page-1 (rotated) is now at idx 1
        assert _get_rotation(result, 1) == 90

    def test_returns_absolute_path(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        result = organize_pdf(src, out, [{"op": "rotate", "angle": 90}])
        assert os.path.isabs(result)


class TestOrganizeInvalidOpType:
    def test_unknown_op_raises_value_error(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError, match="unknown op type"):
            organize_pdf(src, out, [{"op": "flip", "pages": [1]}])

    def test_missing_op_key_raises_value_error(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError):
            organize_pdf(src, out, [{"pages": [1]}])  # no "op" key


class TestOrganizeEmptyOperations:
    def test_empty_ops_raises_value_error(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError):
            organize_pdf(src, out, [])


class TestOrganizeMissingFile:
    def test_missing_file_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            organize_pdf(
                "/no/such/file.pdf",
                str(tmp_path / "out.pdf"),
                [{"op": "rotate", "angle": 90}],
            )


class TestOrganizeInvalidOpParams:
    def test_delete_out_of_range_page(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError, match="out of range"):
            organize_pdf(src, out, [{"op": "delete", "pages": [99]}])

    def test_rotate_invalid_angle(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError, match="angle"):
            organize_pdf(src, out, [{"op": "rotate", "angle": 45}])

    def test_reorder_wrong_permutation(self, tmp_path):
        src = _make_pdf(str(tmp_path / "src.pdf"), num_pages=3)
        out = str(tmp_path / "out.pdf")
        with pytest.raises(ValueError, match="permutation"):
            organize_pdf(src, out, [{"op": "reorder", "order": [1, 1, 3]}])
