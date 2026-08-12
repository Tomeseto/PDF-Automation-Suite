"""
merge_pdf.merge
~~~~~~~~~~~~~~~

Merges multiple PDF files into a single output PDF, preserving input order.

Public function:
    merge_pdfs(input_files, output_file, overwrite) -> str
"""

import os

import pypdf

from app.core.logger import (
    STATUS_FAILURE,
    STATUS_SUCCESS,
    log_event,
)

_MODULE = "merge_pdf"
_ACTION = "merge_files"


def merge_pdfs(
    input_files: list[str],
    output_file: str,
    overwrite: bool = False,
) -> str:
    """Merge multiple PDF files into one output file.

    Args:
        input_files: Ordered list of absolute or relative paths to input PDFs.
        output_file: Path for the merged output PDF.
        overwrite:   If ``False`` (default) and *output_file* already exists,
                     raises :class:`FileExistsError`.

    Returns:
        The absolute path to the merged output file.

    Raises:
        ValueError:       ``input_files`` is empty.
        FileNotFoundError: One or more input files do not exist on disk.
        FileExistsError:  ``output_file`` already exists and ``overwrite=False``.
        RuntimeError:     A PDF cannot be read (corrupt) or writing fails.
    """
    try:
        # --- Validate inputs ---
        if not input_files:
            raise ValueError("input_files must not be empty.")

        # Check existence and readability of every input PDF first,
        # so we fail fast before touching any output file.
        readers: list[pypdf.PdfReader] = []
        for path in input_files:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Input file not found: {path!r}")
            try:
                reader = pypdf.PdfReader(path)
                # Access pages to trigger any parse errors early.
                _ = len(reader.pages)
                readers.append(reader)
            except pypdf.errors.PdfReadError as exc:
                raise RuntimeError(
                    f"Cannot read PDF (corrupt or unsupported): {path!r}"
                ) from exc

        # --- Check output file collision ---
        if os.path.exists(output_file) and not overwrite:
            raise FileExistsError(
                f"Output file already exists: {output_file!r}. "
                "Pass overwrite=True to replace it."
            )

        # --- Merge ---
        writer = pypdf.PdfWriter()
        for reader in readers:
            writer.append(reader)

        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "wb") as out_fh:
            writer.write(out_fh)

        abs_out = os.path.abspath(output_file)
        log_event(
            _MODULE,
            _ACTION,
            STATUS_SUCCESS,
            f"Merged {len(input_files)} file(s) -> {abs_out}",
        )
        return abs_out

    except (ValueError, FileNotFoundError, FileExistsError):
        # Validation errors: log and re-raise as-is so the GUI can display them.
        log_event(_MODULE, _ACTION, STATUS_FAILURE, "Validation error — see exception")
        raise
    except RuntimeError:
        raise
    except Exception as exc:
        log_event(_MODULE, _ACTION, STATUS_FAILURE, str(exc))
        raise RuntimeError(f"Failed to merge PDFs: {exc}") from exc
