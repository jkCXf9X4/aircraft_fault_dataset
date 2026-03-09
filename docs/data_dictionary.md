# Data Dictionary

This document defines the repository's public data interface for analysts and tooling.

## Dataset Layout

The repository exposes two logical datasets:

1. Split primary fault files under `data/faults/*.csv`
2. Secondary-effect mappings in `data/fault_secondary_effects.csv`

For consumers that prefer a single file, use `scripts/export_fault_catalog.py` to produce a flattened export.

## Primary Fault Schema

Each file under `data/faults/` uses the same schema.

| Column | Type | Description |
| --- | --- | --- |
| `fault_id` | string | Stable row identifier. Format is `<PREFIX>-<NNN>`, unique across the repository. |
| `subsystem` | string | Owning subsystem or dedicated avionics computer for the row. |
| `severity` | enum | Qualitative operational impact. Allowed values are `medium`, `high`, `critical`. |
| `short_description` | string | Compact fault label intended for indexing and display. Maximum 20 characters. |
| `long_description` | string | Operational description of the in-flight fault condition. |
| `pilot_actions` | string | Immediate pilot response, handling guidance, or recovery intent. |

## Fault ID Prefixes

| File | Prefix | Subsystem |
| --- | --- | --- |
| `ccc.csv` | `CCC` | Communication Control Computer |
| `dpc.csv` | `DPC` | Display Processor Computer |
| `ecs.csv` | `ECS` | Environmental Control System |
| `electrical.csv` | `ELEC` | Electrical |
| `flight_control.csv` | `FCTL` | Flight Control |
| `fuel_system.csv` | `FUEL` | Fuel System |
| `hydraulic.csv` | `HYD` | Hydraulic |
| `landing_gear.csv` | `LG` | Landing Gear |
| `mmc.csv` | `MMC` | Mission Management Computer |
| `navc.csv` | `NAVC` | Navigation Computer |
| `propulsion.csv` | `PROP` | Propulsion |
| `rpc.csv` | `RPC` | Radar Processor Computer |
| `smc.csv` | `SMC` | Stores Management Computer |

## Secondary Effects Schema

`data/fault_secondary_effects.csv` contains the following columns:

| Column | Type | Description |
| --- | --- | --- |
| `fault` | string | Primary fault label. This matches `short_description` in the split fault files. |
| `derived_secondary_faults` | string | Semicolon-delimited list of downstream fault labels, each matching a `short_description` value. |

## Consumer Notes

- Treat `fault_id` as the stable identifier for primary fault rows.
- Treat `short_description` as a compact label, not a guaranteed immutable business key.
- Secondary-effect mappings currently join on `short_description`; the export script copies those mappings onto each primary fault row for easier downstream use.
- Rows describe in-flight operational fault cases, not maintenance discrepancies or component-level teardown findings.
- Secondary-effect links represent plausible propagation assumptions, not deterministic causal guarantees.

## Flattened Export Schema

`scripts/export_fault_catalog.py` emits one row per primary fault with these columns:

| Column | Description |
| --- | --- |
| `fault_id` | Stable primary fault identifier |
| `subsystem` | Fault-owning subsystem or avionics computer |
| `severity` | Operational severity |
| `short_description` | Compact fault label |
| `long_description` | Detailed fault description |
| `pilot_actions` | Immediate pilot actions |
| `derived_secondary_faults` | Semicolon-delimited downstream fault labels |
| `source_file` | Original source CSV filename under `data/faults/` |

## Validation Rules

The repository validator enforces these baseline rules:

- every split fault file must use the shared schema
- every split fault file must contain at least five rows
- major subsystems `Propulsion`, `Fuel System`, `Electrical`, and `Hydraulic` must contain at least ten rows each
- all three severity levels must appear somewhere in the dataset
- `Propulsion`, `Flight Control`, `Hydraulic`, and `ECS` must each include at least one `critical` row
- every primary fault must have exactly one secondary-effects row
- every derived secondary fault must resolve to an existing primary fault label
