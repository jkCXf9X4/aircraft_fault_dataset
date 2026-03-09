# Aircraft Fault Dataset

This repository stores a starter dataset for in-flight aircraft fault analysis based on a notional single-engine multi-role fighter aircraft.

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
- `data/faults/`
  - one CSV per subsystem or avionics computer
  - each file uses the same in-flight fault schema
- `data/fault_secondary_effects.csv`
  - mapping between primary faults and likely downstream or secondary effects
- `scripts/validate_fault_data.py`
  - schema and coverage validation for the split fault dataset
- `tests/test_fault_data.py`
  - automated checks for dataset consistency and coverage

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

- secondary effects map each fault to one or more existing fault names from `data/faults/`
- mappings are written as plausible fault-propagation links rather than free-text consequence phrases
- these relationships are analytical assumptions, not guaranteed deterministic outcomes

## Current Status

The repository currently contains:

- a baseline aircraft design assumptions document
- an initial split in-flight fault catalog covering propulsion, fuel, electrical, flight control, hydraulic, avionics, ECS, and landing gear
- computer-specific avionics fault cases for `MMC`, `SMC`, `RPC`, `NAVC`, `DPC`, and `CCC`
- an initial secondary-effects dataset for those faults

## Validation And Tests

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

## Suggested Next Steps

- add phase-of-flight and pilot workload fields to the fault dataset
- add machine-readable links between subsystem assumptions and fault entries
- generate derived analysis views such as severity-by-subsystem and propagation summaries

### Focused Fault Evaluation Implications

- Fault datasets can now distinguish computer-local failures from shared bus or sensor failures.
- Secondary-effect analysis can trace propagation paths, for example `NAVC fault -> MMC degraded fusion -> DPC display inconsistency`.
- Rectification actions can target the affected computer, its interfaces, or shared dependencies such as cooling, power, and mission buses.

### Dataset Modeling Assumptions

- Fault entries are written as in-flight operational fault cases, not as ground maintenance discrepancies or detailed part-number failures.
- Short descriptions are capped to 20 characters to match the README requirement.
- Secondary effects capture plausible airborne propagation paths and mission impacts, not guaranteed deterministic outcomes.
- Pilot action fields describe immediate cockpit response, aircraft handling, and reco very intent.
