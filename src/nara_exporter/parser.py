"""Read a raw Nara Baby CSV export into plain dict rows.

Nara's export (confirmed against a real, user-provided sample on
2026-09-23) is a single flat CSV per child:

- One row per logged activity.
- A `Type` column discriminates the activity (e.g. "Sleep", "Diaper").
- Columns for activity-specific fields are prefixed like `[Sleep] ...`,
  `[Diaper] ...`, etc., and are left blank for rows of a different type.
- One `Profile` row per child holds static info (birth date, sex).
- Encoding is UTF-8 (verified byte-for-byte on a real export containing
  non-ASCII characters).

This module does no interpretation beyond reading rows as dicts; see
`normalize.py` for turning rows into `NormalizedEvent` objects.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator


def read_raw_rows(csv_path: str | Path) -> Iterator[dict]:
    """Yield each data row of a Nara export as a dict of {column: value}.

    Empty trailing rows (Nara's export sometimes ends with a blank line)
    are skipped. Uses utf-8-sig so a leading BOM (if present) is stripped
    automatically.
    """
    path = Path(csv_path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip fully-blank rows.
            if not any((value or "").strip() for value in row.values()):
                continue
            yield row


def read_header(csv_path: str | Path) -> list[str]:
    """Return the column header of a Nara export, in order."""
    path = Path(csv_path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        return next(reader)
