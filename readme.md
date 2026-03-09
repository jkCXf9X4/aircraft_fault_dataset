# Aircraft Fault Dataset

This repository stores a structured dataset for in-flight aircraft fault analysis based on a notional single-engine multi-role fighter aircraft.

It is intended for external analysts and tooling that need a compact, inspectable fault catalog with explicit downstream-effect mappings.

The current repository content focuses on:

- defining the aircraft and subsystem assumptions used for analysis
- listing representative faults that originate while flying
- mapping likely secondary effects derived from those in-flight faults
- documenting pilot actions associated with each fault case

## Repository Structure

- `docs/design_assumptions.md`
  - baseline aircraft specification
  - subsystem-level assumptions
  - federated avionics and mission systems breakdown with multiple dedicated avionics computers
- `docs/data_dictionary.md`
  - public data interface, field definitions, validation rules, and consumer notes
- `data/faults/`
  - one CSV per subsystem or avionics computer
  - each file uses the same in-flight fault schema
- `data/fault_secondary_effects.csv`
  - mapping between primary fault labels and likely downstream fault effects
- `scripts/validate_fault_data.py`
  - schema and coverage validation for the split fault dataset
- `scripts/export_fault_catalog.py`
  - flattens the split dataset into one CSV or JSON export for downstream analysis
- `tests/test_fault_data.py`
  - automated checks for dataset consistency and coverage

## Quick Start

Use this sequence if you are opening the repository for the first time:

1. Read `docs/data_dictionary.md` for the external data contract.
2. Read `docs/design_assumptions.md` for the aircraft and subsystem framing behind the fault cases.
3. Inspect `data/faults/*.csv` for the primary fault catalog and `data/fault_secondary_effects.csv` for propagation links.
4. Run the validator to confirm the local checkout is internally consistent.
5. Export a flattened CSV or JSON file if your workflow prefers one artifact instead of split source files.

Typical commands from the repository root:

```bash
python3 scripts/validate_fault_data.py
python3 scripts/export_fault_catalog.py --format csv --output exports/fault_catalog.csv
python3 scripts/export_fault_catalog.py --format json --output exports/fault_catalog.json
```

## Requirements

- run commands from the repository root
- Python 3 with the standard library is sufficient; there are no third-party runtime dependencies
- CSV files are UTF-8 encoded and use a header row

## Aircraft Model Scope

The dataset uses a generic fighter aircraft with the following high-level assumptions:

- single afterburning turbofan engine
- one pilot
- digital fly-by-wire flight controls
- dual hydraulic circuits
- battery-backed electrical buses
- bleed-air environmental control system
- federated avionics architecture

Operational framing for the current datasets:

- fault cases are modeled as faults that occur during flight rather than ground maintenance discrepancies
- action fields describe pilot response and aircraft handling decisions rather than post-flight repair actions
- secondary effects emphasize airborne operational consequences such as loss of capability, workload increase, diversion, or abnormal landing

The avionics model is intentionally split into multiple computers to support more focused fault analysis:

- Mission Management Computer (`MMC`)
- Stores Management Computer (`SMC`)
- Radar Processor Computer (`RPC`)
- Navigation Computer (`NAVC`)
- Display Processor Computer (`DPC`)
- Communication Control Computer (`CCC`)

## Dataset Files

### `data/faults/*.csv`

Columns:

- `fault_id`
- `subsystem`
- `severity`
- `short_description`
- `long_description`
- `pilot_actions`

Notes:

- `fault_id` is unique across the repo by combining a file-specific prefix with a local sequence that starts at `001` in each file
- `short_description` is limited to short labels suitable for compact displays and dataset indexing
- `severity` uses qualitative operational impact levels: `medium`, `high`, and `critical`
- entries are written as in-flight operational fault cases rather than depot or line-maintenance discrepancies
- `pilot_actions` captures immediate cockpit response and recovery intent
- each file should contain faults for exactly one subsystem or one avionics computer

### `data/fault_secondary_effects.csv`

Columns:

- `fault`
- `derived_secondary_faults`

Notes:

- `fault` stores a primary fault's `short_description`
- `derived_secondary_faults` stores one or more semicolon-delimited `short_description` values from `data/faults/`
- mappings are written as plausible fault-propagation links rather than free-text consequence phrases
- these relationships are analytical assumptions, not guaranteed deterministic outcomes

### Flattened Export

If you want one analysis-ready file instead of split subsystem files, use `scripts/export_fault_catalog.py`.

Export columns:

- `fault_id`
- `subsystem`
- `severity`
- `short_description`
- `long_description`
- `pilot_actions`
- `derived_secondary_faults`
- `source_file`

Example:

```bash
python3 scripts/export_fault_catalog.py --format csv
```

This writes a single CSV to standard output. Add `--output <path>` to write it to disk.

## Current Status

The repository currently contains:

- a baseline aircraft design assumptions document
- 13 split fault files covering propulsion, fuel system, electrical, flight control, hydraulic, ECS, landing gear, and six dedicated avionics computers
- 85 in-flight fault rows across those files
- 85 secondary-effects rows, one for each primary fault entry

## Validation and Tests

Run the dataset validator:

```bash
python3 scripts/validate_fault_data.py
```

Run the automated tests:

```bash
python3 -m unittest discover -s tests
```

Current test coverage checks:

- CSV schema consistency across all split fault files
- one-subsystem-per-file structure
- minimum of five fault cases per subsystem or avionics-computer file
- minimum of ten fault cases for the major subsystems: propulsion, fuel system, electrical, and hydraulic
- fault ID prefix and per-file `001` sequencing
- short description length constraints
- valid severity levels and severity coverage
- dedicated avionics computer coverage
- linkage between primary faults and secondary-effects rows

## Common Usage Patterns

### For Analysts

- use the flattened export when loading the dataset into spreadsheets, notebooks, or BI tools
- use `subsystem` and `severity` for high-level slicing
- use `derived_secondary_faults` to build propagation summaries or adjacency lists

### For Tooling

- treat `fault_id` as the primary row identifier
- use `source_file` from the flattened export if you need to preserve original file provenance
- validate before ingestion so schema or coverage regressions fail early

### Minimal Python Example

```python
import csv

with open("exports/fault_catalog.csv", newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

critical_propulsion = [
    row for row in rows
    if row["subsystem"] == "Propulsion" and row["severity"] == "critical"
]
```

## Suggested Next Steps

- add phase-of-flight and pilot workload fields to the fault dataset
- add machine-readable links between subsystem assumptions and fault entries
- generate derived analysis views such as severity-by-subsystem and propagation summaries

### Focused Fault Evaluation Implications

- fault datasets can distinguish computer-local failures from shared bus or sensor failures
- secondary-effect analysis can trace propagation paths, for example `NAVC fault -> MMC degraded fusion -> DPC display inconsistency`
- corrective actions can target the affected computer, its interfaces, or shared dependencies such as cooling, power, and mission buses

### Dataset Modeling Assumptions

- fault entries are written as in-flight operational fault cases, not as ground maintenance discrepancies or detailed part-number failures
- short descriptions are capped to 20 characters
- secondary effects capture plausible airborne propagation paths and mission impacts, not guaranteed deterministic outcomes
- pilot action fields describe immediate cockpit response, aircraft handling, and recovery intent
