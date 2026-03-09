# Aircraft Design Assumptions

## Scope

This repository models a notional single-engine multi-role fighter aircraft for fault analysis dataset generation. The aircraft is a generic reference platform inspired by modern lightweight fighters and is not intended to reproduce any specific real-world aircraft exactly.

## Top-Level Aircraft Characteristics

| Attribute | Assumption |
| --- | --- |
| Aircraft role | Multi-role fighter |
| Engine count | 1 turbofan engine |
| Crew | 1 pilot |
| Flight control concept | Digital fly-by-wire |
| Landing gear | Retractable tricycle gear |
| Electrical architecture | Primary AC/DC generation with battery-backed emergency buses |
| Hydraulic architecture | Dual hydraulic circuits with emergency backup provisions |
| Fuel architecture | Internal fuselage and wing tanks with boost pumps |
| Avionics concept | Federated mission computers with redundant data buses |
| Environmental control | Engine bleed-air based ECS with cockpit pressurization |

## Sub-System Baseline Data

### Propulsion

| Item | Assumption |
| --- | --- |
| Type | Afterburning low-bypass turbofan |
| Primary function | Generate thrust and pneumatic power |
| Key components | Fan, compressor, combustor, turbine, FADEC, fuel control, nozzle |
| Typical dependencies | Fuel system, electrical power, engine sensors, ECS bleed interfaces |

### Fuel System

| Item | Assumption |
| --- | --- |
| Primary function | Store and deliver fuel to the engine |
| Key components | Internal tanks, boost pumps, transfer pumps, valves, filters, quantity sensors |
| Failure sensitivities | Contamination, leaks, pump failures, valve faults |

### Electrical Power System

| Item | Assumption |
| --- | --- |
| Primary function | Supply electrical power to mission, flight, and support systems |
| Key components | Engine-driven generator, battery, converters/rectifiers, buses, circuit protection |
| Failure sensitivities | Generator faults, bus shorts, battery degradation, wiring faults |

### Flight Control System

| Item | Assumption |
| --- | --- |
| Primary function | Command aerodynamic control surfaces |
| Key components | Flight control computers, actuators, sensors, control laws, data buses |
| Failure sensitivities | Sensor disagreement, actuator jams, software faults, power loss |

### Hydraulic System

| Item | Assumption |
| --- | --- |
| Primary function | Power actuators, landing gear, and braking subsystems |
| Key components | Pumps, accumulators, reservoirs, lines, valves, actuators |
| Failure sensitivities | Fluid leaks, pressure loss, contamination, pump degradation |

### Avionics and Mission Systems

| Item | Assumption |
| --- | --- |
| Primary function | Support navigation, mission execution, and pilot situational awareness |
| Architecture concept | Federated avionics with multiple function-specific computers connected through redundant mission data buses |
| Key components | Mission management computer, stores management computer, radar processor, navigation computer, display processor, communication control computer, data bus interfaces |
| Failure sensitivities | Cooling faults, software faults, bus failures, processor resets, power conditioning faults, antenna damage |

#### Avionics Computer Allocation

| Computer | Primary role | Main inputs | Main outputs | Typical fault sensitivities |
| --- | --- | --- | --- | --- |
| Mission Management Computer (MMC) | Coordinates mission logic, mode management, sensor fusion, and pilot tactical workflow | Radar tracks, navigation data, pilot HOTAS inputs, weapon status, data link messages | Mission mode commands, display symbology requests, weapon employment logic, fault reporting | Software faults, bus saturation, processor overload, memory corruption |
| Stores Management Computer (SMC) | Monitors and commands pylons, release circuits, and weapon inventory status | Pilot armament selections, station status, interlock sensors, MMC commands | Weapon release enable/deny, station health data, inventory state | Interface faults, discrete I/O failures, release circuit faults, configuration mismatches |
| Radar Processor Computer (RPC) | Controls radar operating modes and signal processing | Radar array returns, timing references, cooling status, MMC mode requests | Target tracks, detection reports, radar status, built-in test results | Overheating, RF chain faults, timing errors, signal processor failures |
| Navigation Computer (NAVC) | Maintains position, velocity, attitude, and time reference for the aircraft | INS sensors, GPS receiver data, air data inputs, barometric data | Navigation solution, time synchronization, steering cues, reference data to MMC and displays | Sensor disagreement, alignment faults, drift accumulation, interface loss |
| Display Processor Computer (DPC) | Renders pilot display pages and consolidates alerting information | MMC symbology requests, NAVC data, engine and aircraft status, caution/advisory inputs | Head-down display pages, HUD formatting data, caution/warning presentation | Graphics processor faults, display bus faults, refresh lag, partial page corruption |
| Communication Control Computer (CCC) | Manages radio tuning, crypto/status interfaces, and data link routing | Pilot comm selections, radio status, antenna paths, mission network messages | Radio control commands, data link traffic, communication status to MMC and displays | Tuning logic faults, interface bus faults, crypto handshake faults, antenna switching failures |

### Environmental Control System

| Item | Assumption |
| --- | --- |
| Primary function | Provide cooling, ventilation, and cockpit pressurization |
| Key components | Heat exchangers, ducts, valves, controllers, sensors |
| Failure sensitivities | Bleed-air loss, valve faults, overheating, cabin pressure anomalies |

### Landing Gear and Braking

| Item | Assumption |
| --- | --- |
| Primary function | Ground handling, takeoff support, and landing deceleration |
| Key components | Gear struts, extension/retraction actuators, uplocks, wheels, brakes, anti-skid |
| Failure sensitivities | Hydraulic faults, sensor faults, actuator jams, tire damage |

