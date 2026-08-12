"""
split_pdf.split
~~~~~~~~~~~~~~~

Splits a PDF file into multiple output PDFs according to a list of
(start, end) page ranges (1-indexed, inclusive).

Public function:
    split_pdf(input_file, output_directory, page_ranges) -> list[str]
"""

import os

import pypdf

from app.core.logger import (
    STATUS_FAILURE,
    STATUS_SUCCESS,
    STATUS_WARNING,
    log_event,
)

_MODULE = "split_pdf"
_ACTION = "split_file"


def split_pdf(
    input_file: str,
    output_directory: str,
    page_ranges: list[tuple[int, int]],
) -> list[str]:
    """Split a PDF into multiple files, one per page range.

    Args:
        input_file:       Path to the source PDF.
        output_directory: Directory where split files will be written.
        page_ranges:      List of ``(start, end)`` tuples (1-indexed, inclusive).
                          E.g. ``[(1, 3), (5, 7)]`` produces two output files.

    Returns:
        List of absolute paths to the produced output files, in the same
        order as *page_ranges*.

    Raises:
        FileNotFoundError: *input_file* does not exist.
        ValueError:        *page_ranges* is empty, a range is out-of-bounds,
                           ranges overlap, or start > end.
        RuntimeError:      The PDF cannot be read (corrupt) or writing fails.
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

        # --- Validate ranges ---
        if not page_ranges:
            raise ValueError("page_ranges must not be empty.")

        for start, end in page_ranges:
            if start > end:
                raise ValueError(
                    f"Invalid range ({start}, {end}): start must be <= end."
                )
            if start < 1 or end > total:
                raise ValueError(
                    f"Range ({start}, {end}) is out of bounds for a "
                    f"{total}-page PDF (pages are 1-indexed)."
                )

        # Check for overlapping ranges
        sorted_ranges = sorted(page_ranges, key=lambda r: r[0])
        for i in range(len(sorted_ranges) - 1):
            _, prev_end = sorted_ranges[i]
            next_start, _ = sorted_ranges[i + 1]
            if next_start <= prev_end:
                raise ValueError(
                    f"Overlapping page ranges: {sorted_ranges[i]} and "
                    f"{sorted_ranges[i + 1]}."
                )

        # --- Create output directory ---
        os.makedirs(output_directory, exist_ok=True)

        # --- Split ---
        output_files: list[str] = []
        for start, end in page_ranges:
            writer = pypdf.PdfWriter()
            # pypdf pages are 0-indexed internally
            for page_idx in range(start - 1, end):
                writer.add_page(reader.pages[page_idx])

            filename = f"split_{start}-{end}.pdf"
            out_path = os.path.abspath(os.path.join(output_directory, filename))
            with open(out_path, "wb") as fh:
                writer.write(fh)
            output_files.append(out_path)

        log_event(
            _MODULE,
            _ACTION,
            STATUS_SUCCESS,
            f"Split {input_file!r} into {len(output_files)} file(s) "
            f"using ranges {page_ranges}",
        )

        if not output_files:
            log_event(_MODULE, _ACTION, STATUS_WARNING, "No output files produced.")

        return output_files

    except (FileNotFoundError, ValueError):
        log_event(_MODULE, _ACTION, STATUS_FAILURE, "Validation error — see exception")
        raise
    except RuntimeError:
        raise
    except Exception as exc:
        log_event(_MODULE, _ACTION, STATUS_FAILURE, str(exc))
        raise RuntimeError(f"Failed to split PDF: {exc}") from exc
