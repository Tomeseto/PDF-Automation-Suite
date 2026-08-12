"""
reorder_pages.reorder
~~~~~~~~~~~~~~~~~~~~~

Reorders pages of a PDF according to a caller-supplied permutation.
The new_order list must be an exact permutation of [1 .. n] (1-indexed),
covering every page exactly once.

Public function:
    reorder_pages(input_file, output_file, new_order) -> str
"""

import os

import pypdf

from app.core.logger import (
    STATUS_FAILURE,
    STATUS_SUCCESS,
    log_event,
)

_MODULE = "reorder_pages"
_ACTION = "reorder_pages"


def reorder_pages(
    input_file: str,
    output_file: str,
    new_order: list[int],
) -> str:
    """Reorder all pages of a PDF according to a new page order.

    Args:
        input_file:  Path to the source PDF.
        output_file: Path for the reordered output PDF.
        new_order:   A permutation of ``[1, 2, ..., n]`` (1-indexed) where
                     ``n`` is the total page count. Every page index must
                     appear exactly once.

    Returns:
        The absolute path to the output file.

    Raises:
        FileNotFoundError: *input_file* does not exist.
        ValueError:        *new_order* is not a valid permutation of the page
                           indices (wrong length, duplicates, or out-of-range
                           values).
        RuntimeError:      The PDF cannot be read or writing fails.
    """
    try:
        # --- Validate file ---
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file!r}")

        try:
            reader = pypdf.PdfReader(input_file)
            total = len(reader.pages)
        except pypdf.errors.PdfReadError as exc:
            raise RuntimeError(
                f"Cannot read PDF (corrupt or unsupported): {input_file!r}"
            ) from exc

        # --- Validate new_order is a permutation of range(1, total+1) ---
        if len(new_order) != total:
            raise ValueError(
                f"new_order has {len(new_order)} element(s) but the PDF has "
                f"{total} page(s). Must cover every page exactly once."
            )

        expected = set(range(1, total + 1))
        provided = set(new_order)

        if provided != expected:
            missing = expected - provided
            extra = provided - expected
            msg_parts = []
            if missing:
                msg_parts.append(f"missing pages: {sorted(missing)}")
            if extra:
                msg_parts.append(f"out-of-range or extra pages: {sorted(extra)}")
            raise ValueError(
                f"new_order is not a valid permutation of [1..{total}]. "
                + "; ".join(msg_parts)
            )

        # Check for duplicates (set equality above does not catch them
        # if len matches by coincidence — e.g. [1,1,3] for 3 pages)
        if len(new_order) != len(set(new_order)):
            raise ValueError(
                "new_order contains duplicate page indices."
            )

        # --- Build reordered output ---
        writer = pypdf.PdfWriter()
        for page_num in new_order:
            writer.add_page(reader.pages[page_num - 1])  # 1-indexed → 0-indexed

        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "wb") as fh:
            writer.write(fh)

        abs_out = os.path.abspath(output_file)
        log_event(
            _MODULE,
            _ACTION,
            STATUS_SUCCESS,
            f"Reordered {total} pages in {input_file!r} -> {abs_out}",
        )
        return abs_out

    except (FileNotFoundError, ValueError):
        log_event(_MODULE, _ACTION, STATUS_FAILURE, "Validation error — see exception")
        raise
    except RuntimeError:
        raise
    except Exception as exc:
        log_event(_MODULE, _ACTION, STATUS_FAILURE, str(exc))
        raise RuntimeError(f"Failed to reorder pages: {exc}") from exc
