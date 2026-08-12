"""
organize_pdf.organize
~~~~~~~~~~~~~~~~~~~~~

Applies an ordered sequence of page-manipulation operations to a PDF in a
single pipeline pass. Supported operations:

    delete  — remove specified pages (1-indexed)
    rotate  — rotate specified pages by a given angle (90/180/270)
    reorder — reorder all remaining pages

The operations are applied sequentially; page indices in each operation
always reference the *current* page numbering at that step (after prior
deletions/reorderings).

Public function:
    organize_pdf(input_file, output_file, operations) -> str
"""

import os
from typing import Any

import pypdf

from app.core.logger import (
    STATUS_FAILURE,
    STATUS_SUCCESS,
    log_event,
)

_MODULE = "organize_pdf"
_ACTION = "organize_pdf"

_SUPPORTED_OPS = {"delete", "rotate", "reorder"}
_VALID_ANGLES = {90, 180, 270}


# ---------------------------------------------------------------------------
# Internal pipeline helpers (self-contained — no imports from other modules)
# ---------------------------------------------------------------------------


def _apply_delete(pages: list[pypdf.PageObject], op: dict[str, Any]) -> list[pypdf.PageObject]:
    """Remove pages at the given 1-indexed positions from the page list."""
    to_delete: list[int] = op.get("pages", [])
    if not to_delete:
        raise ValueError("delete operation requires a non-empty 'pages' list.")

    current_count = len(pages)
    for p in to_delete:
        if p < 1 or p > current_count:
            raise ValueError(
                f"delete: page {p} is out of range for current "
                f"{current_count}-page document."
            )

    # Convert to 0-indexed set and remove (iterate in reverse to avoid index shift)
    delete_set = {p - 1 for p in to_delete}
    return [page for idx, page in enumerate(pages) if idx not in delete_set]


def _apply_rotate(pages: list[pypdf.PageObject], op: dict[str, Any]) -> list[pypdf.PageObject]:
    """Rotate specified pages (or all) by the given angle."""
    angle: int = op.get("angle")
    if angle not in _VALID_ANGLES:
        raise ValueError(
            f"rotate: angle must be one of {sorted(_VALID_ANGLES)}, got {angle!r}."
        )

    target_pages: list[int] | None = op.get("pages")  # 1-indexed or None = all

    current_count = len(pages)
    if target_pages is not None:
        for p in target_pages:
            if p < 1 or p > current_count:
                raise ValueError(
                    f"rotate: page {p} is out of range for current "
                    f"{current_count}-page document."
                )
        target_set = {p - 1 for p in target_pages}
    else:
        target_set = set(range(current_count))

    for idx in target_set:
        pages[idx].rotate(angle)

    return pages


def _apply_reorder(pages: list[pypdf.PageObject], op: dict[str, Any]) -> list[pypdf.PageObject]:
    """Reorder pages according to new_order (1-indexed permutation)."""
    new_order: list[int] = op.get("order", [])
    current_count = len(pages)

    if len(new_order) != current_count:
        raise ValueError(
            f"reorder: order has {len(new_order)} element(s) but the "
            f"document currently has {current_count} page(s)."
        )

    expected = set(range(1, current_count + 1))
    provided = set(new_order)
    if provided != expected or len(new_order) != len(set(new_order)):
        raise ValueError(
            f"reorder: order is not a valid permutation of "
            f"[1..{current_count}]."
        )

    return [pages[p - 1] for p in new_order]


_OP_HANDLERS = {
    "delete": _apply_delete,
    "rotate": _apply_rotate,
    "reorder": _apply_reorder,
}


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------


def organize_pdf(
    input_file: str,
    output_file: str,
    operations: list[dict],
) -> str:
    """Apply an ordered pipeline of page operations to a PDF.

    Args:
        input_file:  Path to the source PDF.
        output_file: Path for the organized output PDF.
        operations:  Ordered list of operation dicts. Supported ops:

                     - ``{"op": "delete", "pages": [3, 5]}``
                     - ``{"op": "rotate", "pages": [1, 2], "angle": 90}``
                       (omit ``"pages"`` to rotate all current pages)
                     - ``{"op": "reorder", "order": [3, 1, 2]}``

    Returns:
        The absolute path to the output file.

    Raises:
        FileNotFoundError: *input_file* does not exist.
        ValueError:        *operations* is empty, an op type is unknown, or
                           an op's parameters are invalid given the current
                           page state.
        RuntimeError:      The PDF cannot be read or writing fails.
    """
    try:
        # --- Validate file ---
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file!r}")

        if not operations:
            raise ValueError("operations list must not be empty.")

        try:
            reader = pypdf.PdfReader(input_file)
        except pypdf.errors.PdfReadError as exc:
            raise RuntimeError(
                f"Cannot read PDF (corrupt or unsupported): {input_file!r}"
            ) from exc

        # Load all pages into a mutable list for in-place pipeline processing
        pages: list[pypdf.PageObject] = list(reader.pages)

        # --- Apply operations sequentially ---
        for step_idx, op in enumerate(operations):
            op_name = op.get("op")
            if op_name not in _SUPPORTED_OPS:
                raise ValueError(
                    f"Operation at index {step_idx} has unknown op type "
                    f"{op_name!r}. Supported: {sorted(_SUPPORTED_OPS)}."
                )
            handler = _OP_HANDLERS[op_name]
            pages = handler(pages, op)

            if not pages:
                raise ValueError(
                    f"All pages were deleted after operation {step_idx} "
                    f"({op_name!r}). Cannot produce a valid PDF."
                )

        # --- Write output ---
        writer = pypdf.PdfWriter()
        for page in pages:
            writer.add_page(page)

        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "wb") as fh:
            writer.write(fh)

        abs_out = os.path.abspath(output_file)
        op_summary = [op.get("op", "?") for op in operations]
        log_event(
            _MODULE,
            _ACTION,
            STATUS_SUCCESS,
            f"Applied {len(operations)} operation(s) {op_summary} to "
            f"{input_file!r} -> {abs_out}",
        )
        return abs_out

    except (FileNotFoundError, ValueError):
        log_event(_MODULE, _ACTION, STATUS_FAILURE, "Validation error — see exception")
        raise
    except RuntimeError:
        raise
    except Exception as exc:
        log_event(_MODULE, _ACTION, STATUS_FAILURE, str(exc))
        raise RuntimeError(f"Failed to organize PDF: {exc}") from exc
