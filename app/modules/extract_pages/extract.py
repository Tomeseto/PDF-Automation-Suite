"""
extract_pages.extract
~~~~~~~~~~~~~~~~~~~~~

Extracts an arbitrary (possibly non-contiguous) list of pages from a PDF
and writes them into a new PDF, preserving the requested order.

Public function:
    extract_pages(input_file, output_file, pages) -> str
"""

import os

import pypdf

from app.core.logger import (
    STATUS_FAILURE,
    STATUS_SUCCESS,
    log_event,
)

_MODULE = "extract_pages"
_ACTION = "extract_pages"


def extract_pages(
    input_file: str,
    output_file: str,
    pages: list[int],
) -> str:
    """Extract specific pages from a PDF into a new file.

    Args:
        input_file:  Path to the source PDF.
        output_file: Path for the output PDF.
        pages:       1-indexed page numbers to extract, in desired output order.
                     Duplicates are deduplicated while preserving first-seen order.

    Returns:
        The absolute path to the output file.

    Raises:
        FileNotFoundError: *input_file* does not exist.
        ValueError:        *pages* is empty or contains an out-of-range number.
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

        # --- Validate pages list ---
        if not pages:
            raise ValueError("pages list must not be empty.")

        # Deduplicate while preserving order
        seen: set[int] = set()
        deduped: list[int] = []
        for p in pages:
            if p not in seen:
                seen.add(p)
                deduped.append(p)

        for p in deduped:
            if p < 1 or p > total:
                raise ValueError(
                    f"Page {p} is out of range for a {total}-page PDF "
                    f"(pages are 1-indexed)."
                )

        # --- Extract ---
        writer = pypdf.PdfWriter()
        for p in deduped:
            writer.add_page(reader.pages[p - 1])  # convert to 0-indexed

        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "wb") as fh:
            writer.write(fh)

        abs_out = os.path.abspath(output_file)
        log_event(
            _MODULE,
            _ACTION,
            STATUS_SUCCESS,
            f"Extracted pages {deduped} from {input_file!r} -> {abs_out}",
        )
        return abs_out

    except (FileNotFoundError, ValueError):
        log_event(_MODULE, _ACTION, STATUS_FAILURE, "Validation error — see exception")
        raise
    except RuntimeError:
        raise
    except Exception as exc:
        log_event(_MODULE, _ACTION, STATUS_FAILURE, str(exc))
        raise RuntimeError(f"Failed to extract pages: {exc}") from exc
