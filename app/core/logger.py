"""
Shared processing logger for the PDF Automation Suite.

This module provides a thread-safe, structured logging utility that every
feature module calls to record processing events. Log entries are stored
as JSON-lines in ``logs/processing.log``.

PUBLIC API (frozen after Phase 1 — do not modify signatures):
    log_event(module, action, status, details)
    get_recent_events(limit)
    clear_log()

Status constants:
    STATUS_SUCCESS, STATUS_FAILURE, STATUS_WARNING, STATUS_INFO
"""

import json
import os
from datetime import datetime
from threading import Lock

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LOG_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "logs", "processing.log"
)

# Status constants — use these instead of raw strings.
STATUS_SUCCESS = "SUCCESS"
STATUS_FAILURE = "FAILURE"
STATUS_WARNING = "WARNING"
STATUS_INFO = "INFO"

_lock = Lock()

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def log_event(module: str, action: str, status: str, details: str = "") -> None:
    """Append a structured log entry.

    Args:
        module:  Name of the calling module (e.g. ``"merge_pdf"``).
        action:  Specific action performed (e.g. ``"merge_files"``).
        status:  One of :data:`STATUS_SUCCESS`, :data:`STATUS_FAILURE`,
                 :data:`STATUS_WARNING`, :data:`STATUS_INFO`.
        details: Free-form detail string.
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "action": action,
        "status": status,
        "details": details,
    }
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with _lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


def get_recent_events(limit: int = 100) -> list[dict]:
    """Return the most recent *limit* log entries as dicts (newest first).

    Args:
        limit: Maximum number of entries to return. Defaults to ``100``.

    Returns:
        A list of log-entry dicts, ordered newest-first.
    """
    if not os.path.exists(LOG_FILE):
        return []
    with _lock:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    entries: list[dict] = []
    for line in reversed(lines):
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        if len(entries) >= limit:
            break
    return entries


def clear_log() -> None:
    """Clear all log entries.

    Primarily intended for use in tests and during development.
    """
    with _lock:
        if os.path.exists(LOG_FILE):
            open(LOG_FILE, "w").close()
