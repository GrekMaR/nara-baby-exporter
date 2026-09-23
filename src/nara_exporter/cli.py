"""Command-line interface for nara_exporter.

Usage:
    python -m nara_exporter.cli export INPUT.csv [--out-dir DIR] [--json-only] [--csv-only]
    python -m nara_exporter.cli summary INPUT.csv
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from .normalize import normalize_rows
from .parser import read_raw_rows
from .schema import KNOWN_TYPES
from .writer import write_csv, write_json


def _load_events(input_path: Path):
    rows = read_raw_rows(input_path)
    return list(normalize_rows(rows))


def cmd_summary(args: argparse.Namespace) -> int:
    events = _load_events(args.input)
    counts = Counter(e.event_type for e in events)

    print(f"Parsed {len(events)} events from {args.input}")
    print()
    print("By type:")
    for event_type, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {event_type:20s} {count}")

    unknown_raw_types = sorted({e.raw_type for e in events if e.event_type == "unknown"})
    if unknown_raw_types:
        print()
        print("WARNING: encountered activity types not yet mapped in schema.py:")
        for raw_type in unknown_raw_types:
            print(f"  - {raw_type!r}")
        print(
            "These rows were preserved (see 'raw_fields' in JSON output) but not"
            " broken out into typed columns. Please open an issue/PR with a"
            " sample so they can be added to KNOWN_TYPES."
        )
    else:
        known = set(KNOWN_TYPES.values())
        missing = known - set(counts)
        if missing:
            print()
            print(f"(No rows found for known types: {', '.join(sorted(missing))} -- fine if unused.)")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    events = _load_events(args.input)
    out_dir = args.out_dir or args.input.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = args.input.stem
    wrote_any = False

    if not args.json_only:
        csv_path = out_dir / f"{stem}.normalized.csv"
        n = write_csv(events, csv_path)
        print(f"Wrote {n} rows -> {csv_path}")
        wrote_any = True

    if not args.csv_only:
        json_path = out_dir / f"{stem}.normalized.json"
        n = write_json(events, json_path)
        print(f"Wrote {n} records -> {json_path}")
        wrote_any = True

    if not wrote_any:
        print("Nothing to do: both --json-only and --csv-only were set.", file=sys.stderr)
        return 1

    unknown_count = sum(1 for e in events if e.event_type == "unknown")
    if unknown_count:
        print(
            f"\nNote: {unknown_count} row(s) had an activity type not yet mapped"
            " in the schema. Run the 'summary' command for details."
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nara-export",
        description="Parse and normalize a Nara Baby CSV export into a portable schema.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export", help="Convert a Nara CSV export to normalized CSV/JSON.")
    export_parser.add_argument("input", type=Path, help="Path to Nara's exported CSV file.")
    export_parser.add_argument(
        "--out-dir", type=Path, default=None, help="Output directory (default: same folder as input)."
    )
    export_parser.add_argument("--csv-only", action="store_true", help="Only write the normalized CSV.")
    export_parser.add_argument("--json-only", action="store_true", help="Only write the normalized JSON.")
    export_parser.set_defaults(func=cmd_export)

    summary_parser = subparsers.add_parser("summary", help="Print a count of activity types found in the export.")
    summary_parser.add_argument("input", type=Path, help="Path to Nara's exported CSV file.")
    summary_parser.set_defaults(func=cmd_summary)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
