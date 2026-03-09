import csv
import unittest
from pathlib import Path

from scripts.validate_fault_data import (
    EXPECTED_AVIONICS,
    FILE_ID_PREFIXES,
    MAJOR_SUBSYSTEM_MIN_COUNTS,
    VALID_SEVERITIES,
    validate,
)


ROOT = Path(__file__).resolve().parent.parent
FAULTS_DIR = ROOT / "data" / "faults"


class FaultDataTests(unittest.TestCase):
    def test_validation_passes(self):
        summary = validate()
        self.assertGreaterEqual(summary["fault_count"], 65)
        self.assertEqual(summary["secondary_effect_count"], summary["fault_count"])

    def test_each_fault_file_contains_single_subsystem(self):
        for path in sorted(FAULTS_DIR.glob("*.csv")):
            with path.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
                subsystems = {row["subsystem"] for row in rows}
            self.assertEqual(
                len(subsystems),
                1,
                msg=f"{path.name} should only contain one subsystem/computer",
            )
            self.assertGreaterEqual(
                len(rows),
                5,
                msg=f"{path.name} should contain at least five fault cases",
            )

    def test_short_descriptions_remain_compact(self):
        for path in sorted(FAULTS_DIR.glob("*.csv")):
            with path.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    self.assertLessEqual(
                        len(row["short_description"]),
                        20,
                        msg=f"{row['fault_id']} short_description is too long",
                    )

    def test_all_severity_levels_are_used(self):
        summary = validate()
        self.assertEqual(set(summary["severity_counts"]), VALID_SEVERITIES)

    def test_all_dedicated_avionics_computers_have_fault_coverage(self):
        summary = validate()
        self.assertTrue(EXPECTED_AVIONICS.issubset(summary["subsystem_counts"]))

    def test_major_subsystems_have_deeper_coverage(self):
        summary = validate()
        for subsystem, minimum in MAJOR_SUBSYSTEM_MIN_COUNTS.items():
            self.assertGreaterEqual(
                summary["subsystem_counts"].get(subsystem, 0),
                minimum,
                msg=f"{subsystem} should contain at least {minimum} fault cases",
            )

    def test_fault_ids_restart_from_one_in_each_file(self):
        for path in sorted(FAULTS_DIR.glob("*.csv")):
            expected_prefix = FILE_ID_PREFIXES[path.name]
            with path.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                fault_ids = [row["fault_id"] for row in reader]
            expected_ids = [
                f"{expected_prefix}-{index:03d}"
                for index in range(1, len(fault_ids) + 1)
            ]
            self.assertEqual(
                fault_ids,
                expected_ids,
                msg=f"{path.name} should restart numbering at 001",
            )

    def test_secondary_effects_reference_existing_faults(self):
        summary = validate()
        self.assertEqual(
            summary["secondary_effect_count"],
            summary["fault_count"],
            msg="secondary effects should map one-to-one with existing faults",
        )


if __name__ == "__main__":
    unittest.main()
