#!/usr/bin/env python3

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_fault_data import FAULTS_DIR, SECONDARY_EFFECTS_FILE, validate


EXPORT_HEADERS = [
    "fault_id",
    "subsystem",
    "severity",
    "short_description",
    "long_description",
    "pilot_actions",
    "derived_secondary_faults",
    "source_file",
]


def load_secondary_effect_map():
    with SECONDARY_EFFECTS_FILE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return {
            row["fault"]: row["derived_secondary_faults"]
            for row in reader
        }


def build_export_rows():
    validate()
    secondary_effects = load_secondary_effect_map()
    rows = []

    for path in sorted(FAULTS_DIR.glob("*.csv")):
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows.append(
                    {
                        **row,
                        "derived_secondary_faults": secondary_effects[
                            row["short_description"]
                        ],
                        "source_file": path.name,
                    }
                )

    return rows


def write_csv(rows, output_path):
    if output_path is None:
        writer = csv.DictWriter(sys.stdout, fieldnames=EXPORT_HEADERS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPORT_HEADERS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(rows, output_path):
    payload = rows
    if output_path is None:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Export the split fault dataset as a single CSV or JSON file."
    )
    parser.add_argument(
        "--format",
        choices=("csv", "json"),
        default="csv",
        help="Output format. Defaults to csv.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path. Defaults to stdout if omitted.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    rows = build_export_rows()

    if args.format == "csv":
        write_csv(rows, args.output)
    else:
        write_json(rows, args.output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
