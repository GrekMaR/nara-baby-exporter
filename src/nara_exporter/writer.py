"""Write normalized events out as CSV and/or JSON."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from .schema import CSV_COLUMNS, NormalizedEvent


def write_csv(events: Iterable[NormalizedEvent], out_path: str | Path) -> int:
    """Write events to a flat, normalized CSV. Returns the row count written."""
    path = Path(out_path)
    count = 0
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for event in events:
            writer.writerow(event.to_dict())
            count += 1
    return count


def write_json(events: Iterable[NormalizedEvent], out_path: str | Path, indent: int = 2) -> int:
    """Write events to a JSON array of objects. Returns the row count written."""
    path = Path(out_path)
    data = [event.to_dict() for event in events]
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    return len(data)
