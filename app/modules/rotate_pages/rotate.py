"""
rotate_pages.rotate
~~~~~~~~~~~~~~~~~~~

Rotates pages of a PDF by a specified angle (90 / 180 / 270 degrees).
Can target all pages or a specific subset.

Public function:
    rotate_pages(input_file, output_file, angle, pages) -> str
"""

import os
from typing import Optional

import pypdf

from app.core.logger import (
    STATUS_FAILURE,
    STATUS_SUCCESS,
    log_event,
)

_MODULE = "rotate_pages"
_ACTION = "rotate_pages"

_VALID_ANGLES = {90, 180, 270}


def rotate_pages(
    input_file: str,
    output_file: str,
    angle: int,
    pages: Optional[list[int]] = None,
) -> str:
    """Rotate pages of a PDF by a fixed angle.

    Args:
        input_file:  Path to the source PDF.
        output_file: Path for the rotated output PDF.
        angle:       Rotation angle in degrees. Must be 90, 180, or 270.
        pages:       1-indexed list of page numbers to rotate.  If ``None``
                     (default), all pages are rotated.

    Returns:
        The absolute path to the output file.

    Raises:
        FileNotFoundError: *input_file* does not exist.
        ValueError:        *angle* is not in {90, 180, 270}, or a page number
                           in *pages* is out of range.
        RuntimeError:      The PDF cannot be read or writing fails.
    """
    try:
        # --- Validate angle ---
        if angle not in _VALID_ANGLES:
            raise ValueError(
                f"angle must be one of {sorted(_VALID_ANGLES)}, got {angle!r}."
            )

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

        # --- Determine target page set (1-indexed → 0-indexed set) ---
        if pages is None:
            target_indices: set[int] = set(range(total))  # all pages
        else:
            if not pages:
                raise ValueError("pages list must not be empty when provided.")
            target_indices = set()
            for p in pages:
                if p < 1 or p > total:
                    raise ValueError(
                        f"Page {p} is out of range for a {total}-page PDF "
                        f"(pages are 1-indexed)."
                    )
                target_indices.add(p - 1)  # convert to 0-indexed

        # --- Build output ---
        writer = pypdf.PdfWriter()
        for idx, page in enumerate(reader.pages):
            if idx in target_indices:
                page.rotate(angle)
            writer.add_page(page)

        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "wb") as fh:
            writer.write(fh)

        abs_out = os.path.abspath(output_file)
        scope = "all pages" if pages is None else f"pages {pages}"
        log_event(
            _MODULE,
            _ACTION,
            STATUS_SUCCESS,
            f"Rotated {scope} by {angle}° in {input_file!r} -> {abs_out}",
        )
        return abs_out

    except (FileNotFoundError, ValueError):
        log_event(_MODULE, _ACTION, STATUS_FAILURE, "Validation error — see exception")
        raise
    except RuntimeError:
        raise
    except Exception as exc:
        log_event(_MODULE, _ACTION, STATUS_FAILURE, str(exc))
        raise RuntimeError(f"Failed to rotate pages: {exc}") from exc
