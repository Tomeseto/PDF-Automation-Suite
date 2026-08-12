"""
batch_process.batch
~~~~~~~~~~~~~~~~~~~

Applies a chosen PDF operation in batch to multiple files, mapping
arguments dynamically and returning a success/failure report for each.
"""

import inspect
import os
from typing import Any

from app.core.logger import (
    STATUS_FAILURE,
    STATUS_SUCCESS,
    log_event,
)
from .registry import BATCH_OPERATIONS

_MODULE = "batch_process"
_ACTION = "batch_process"


def batch_process(
    operation_name: str,
    input_files: list[str],
    options: dict[str, Any],
    output_directory: str,
) -> list[dict]:
    """Apply an operation to a batch of files.

    Args:
        operation_name:   Name of the operation (must exist in registry).
        input_files:      List of input file paths.
        options:          Feature-specific options to pass to the function.
        output_directory: Where to save output files (if applicable).

    Returns:
        List of dicts describing the outcome per file:
        [{"file": "name.pdf", "status": "success", "result": ...}, ...]
        
    Raises:
        ValueError: If the operation is unknown or input_files is empty.
    """
    if operation_name not in BATCH_OPERATIONS:
        raise ValueError(
            f"Unknown operation {operation_name!r}. "
            f"Supported: {sorted(BATCH_OPERATIONS.keys())}"
        )
    if not input_files:
        raise ValueError("input_files list must not be empty.")

    os.makedirs(output_directory, exist_ok=True)
    
    func, _ = BATCH_OPERATIONS[operation_name]
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())

    results = []
    success_count = 0
    failure_count = 0

    for filepath in input_files:
        basename = os.path.basename(filepath)
        out_name = f"{operation_name}_{basename}"
        # For pdf_to_image, output_directory is expected, for others it's output_file
        out_path = os.path.join(output_directory, out_name)

        # Build arguments dynamically based on the function's signature
        call_kwargs = {}
        for name in param_names:
            if name in options:
                call_kwargs[name] = options[name]
            elif name in ["input_file", "pdf_path"]:
                call_kwargs[name] = filepath
            elif name in ["input_files", "image_files"]:
                # Some functions take a list of files. In a batch context where
                # we iterate per file, we pass the single file as a 1-element list.
                call_kwargs[name] = [filepath]
            elif name == "output_file":
                call_kwargs[name] = out_path
            elif name == "output_directory":
                # Give it a unique sub-directory per file to avoid collisions
                sub_dir = os.path.join(output_directory, f"{operation_name}_{basename}_out")
                os.makedirs(sub_dir, exist_ok=True)
                call_kwargs[name] = sub_dir
            elif name == "output_prefix":
                call_kwargs[name] = out_path

        try:
            res = func(**call_kwargs)
            results.append({"file": basename, "status": "success", "result": res})
            success_count += 1
            log_event(
                _MODULE,
                operation_name,
                STATUS_SUCCESS,
                f"Batch processed {basename}",
            )
        except Exception as e:
            results.append({"file": basename, "status": "failure", "error": str(e)})
            failure_count += 1
            log_event(
                _MODULE,
                operation_name,
                STATUS_FAILURE,
                f"Batch failed for {basename}: {e}",
            )

    log_event(
        _MODULE,
        _ACTION,
        STATUS_SUCCESS,
        f"Batch {operation_name} complete: {success_count} success, {failure_count} failed",
    )

    return results
