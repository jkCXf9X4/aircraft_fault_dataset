#!/usr/bin/env python3

import csv
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FAULTS_DIR = ROOT / "data" / "faults"
SECONDARY_EFFECTS_FILE = ROOT / "data" / "fault_secondary_effects.csv"
EXPECTED_HEADERS = [
    "fault_id",
    "subsystem",
    "severity",
    "short_description",
    "long_description",
    "pilot_actions",
]
VALID_SEVERITIES = {"medium", "high", "critical"}
EXPECTED_AVIONICS = {"MMC", "SMC", "RPC", "NAVC", "DPC", "CCC"}
FLIGHT_SAFETY_SUBSYSTEMS = {"Propulsion", "Flight Control", "Hydraulic", "ECS"}
MAJOR_SUBSYSTEM_MIN_COUNTS = {
    "Propulsion": 10,
    "Fuel System": 10,
    "Electrical": 10,
    "Hydraulic": 10,
}
FILE_ID_PREFIXES = {
    "ccc.csv": "CCC",
    "dpc.csv": "DPC",
    "ecs.csv": "ECS",
    "electrical.csv": "ELEC",
    "flight_control.csv": "FCTL",
    "fuel_system.csv": "FUEL",
    "hydraulic.csv": "HYD",
    "landing_gear.csv": "LG",
    "mmc.csv": "MMC",
    "navc.csv": "NAVC",
    "propulsion.csv": "PROP",
    "rpc.csv": "RPC",
    "smc.csv": "SMC",
}


def load_fault_rows():
    rows = []
    files = sorted(FAULTS_DIR.glob("*.csv"))
    if not files:
        raise ValueError(f"No fault files found in {FAULTS_DIR}")

    for path in files:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != EXPECTED_HEADERS:
                raise ValueError(f"{path.name}: invalid header {reader.fieldnames}")
            file_rows = list(reader)
            if not file_rows:
                raise ValueError(f"{path.name}: file is empty")
            if len(file_rows) < 5:
                raise ValueError(f"{path.name}: file should contain at least 5 faults")
            rows.extend(file_rows)

    return rows, files


def validate_file_local_ids(path, file_rows):
    expected_prefix = FILE_ID_PREFIXES.get(path.name)
    if expected_prefix is None:
        raise ValueError(f"{path.name}: no expected fault_id prefix configured")

    for index, row in enumerate(file_rows, start=1):
        fault_id = row["fault_id"]
        match = re.fullmatch(r"([A-Z]+)-(\d{3})", fault_id)
        if not match:
            raise ValueError(f"{path.name}: invalid fault_id format {fault_id}")

        prefix, number = match.groups()
        if prefix != expected_prefix:
            raise ValueError(
                f"{path.name}: expected prefix {expected_prefix}, found {prefix}"
            )
        if int(number) != index:
            raise ValueError(
                f"{path.name}: expected sequential id {expected_prefix}-{index:03d}, "
                f"found {fault_id}"
            )


def load_secondary_effects():
    with SECONDARY_EFFECTS_FILE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["fault", "derived_secondary_faults"]:
            raise ValueError("fault_secondary_effects.csv: invalid header")
        return list(reader)


def validate():
    faults, fault_files = load_fault_rows()
    secondary_effects = load_secondary_effects()

    fault_ids = set()
    short_descriptions = set()
    severity_counts = Counter()
    subsystem_counts = Counter()

    for path in fault_files:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            validate_file_local_ids(path, list(reader))

    for row in faults:
        fault_id = row["fault_id"]
        short_description = row["short_description"]
        subsystem = row["subsystem"]
        severity = row["severity"]

        if fault_id in fault_ids:
            raise ValueError(f"Duplicate fault_id: {fault_id}")
        fault_ids.add(fault_id)

        if short_description in short_descriptions:
            raise ValueError(f"Duplicate short_description: {short_description}")
        short_descriptions.add(short_description)

        if len(short_description) > 20:
            raise ValueError(f"{fault_id}: short_description exceeds 20 characters")
        if severity not in VALID_SEVERITIES:
            raise ValueError(f"{fault_id}: invalid severity {severity}")
        if not row["long_description"].strip():
            raise ValueError(f"{fault_id}: missing long_description")
        if not row["pilot_actions"].strip():
            raise ValueError(f"{fault_id}: missing pilot_actions")

        severity_counts[severity] += 1
        subsystem_counts[subsystem] += 1

    effect_names = {row["fault"] for row in secondary_effects}
    missing_effects = short_descriptions - effect_names
    if missing_effects:
        raise ValueError(
            "Missing secondary effects for faults: " + ", ".join(sorted(missing_effects))
        )

    unknown_primary = effect_names - short_descriptions
    if unknown_primary:
        raise ValueError(
            "Secondary effects reference unknown primary faults: "
            + ", ".join(sorted(unknown_primary))
        )

    for row in secondary_effects:
        fault = row["fault"]
        derived_faults = [
            item.strip()
            for item in row["derived_secondary_faults"].split(";")
            if item.strip()
        ]
        if not derived_faults:
            raise ValueError(f"{fault}: missing derived_secondary_faults mapping")
        unknown_derived = [item for item in derived_faults if item not in short_descriptions]
        if unknown_derived:
            raise ValueError(
                f"{fault}: unknown derived faults: {', '.join(sorted(unknown_derived))}"
            )
        if fault in derived_faults:
            raise ValueError(f"{fault}: self-reference is not allowed")

    missing_avionics = EXPECTED_AVIONICS - set(subsystem_counts)
    if missing_avionics:
        raise ValueError(
            "Missing dedicated avionics fault files for: "
            + ", ".join(sorted(missing_avionics))
        )

    missing_critical = [
        subsystem
        for subsystem in FLIGHT_SAFETY_SUBSYSTEMS
        if not any(
            row["subsystem"] == subsystem and row["severity"] == "critical"
            for row in faults
        )
    ]
    if missing_critical:
        raise ValueError(
            "Missing critical fault coverage for: " + ", ".join(sorted(missing_critical))
        )

    if set(severity_counts) != VALID_SEVERITIES:
        raise ValueError(
            "Severity coverage incomplete; found: "
            + ", ".join(sorted(severity_counts))
        )

    undercovered_major = [
        f"{subsystem}<{minimum}"
        for subsystem, minimum in MAJOR_SUBSYSTEM_MIN_COUNTS.items()
        if subsystem_counts.get(subsystem, 0) < minimum
    ]
    if undercovered_major:
        raise ValueError(
            "Major subsystem coverage too low: " + ", ".join(undercovered_major)
        )

    return {
        "fault_file_count": len(fault_files),
        "fault_count": len(faults),
        "secondary_effect_count": len(secondary_effects),
        "severity_counts": dict(severity_counts),
        "subsystem_counts": dict(subsystem_counts),
    }


def main():
    try:
        summary = validate()
    except ValueError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1

    print("Fault data validation passed.")
    print(f"Fault files: {summary['fault_file_count']}")
    print(f"Fault rows: {summary['fault_count']}")
    print(f"Secondary effect rows: {summary['secondary_effect_count']}")
    print(f"Severity counts: {summary['severity_counts']}")
    print(f"Subsystem counts: {summary['subsystem_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
