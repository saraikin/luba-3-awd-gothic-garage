# Luba 3 AWD Gothic Garage

DIY project for building a compact protective garage for the Mammotion Luba 3 AWD robot mower, styled as a small Gothic church.

The design is intentionally split into stages:

1. **Stage 1: functional protection** — plywood box, roof, weather protection, safe robot entry, charging station access.
2. **Stage 2: facade and windows** — printed outdoor vinyl film, optional window cut-outs, acrylic inserts, warm LED lighting.
3. **Stage 3: Gothic decor** — false floors, wide tower, spires, rose window, arches, columns, erkers/bay-window modules, 3D-printed elements.

## Design goals

- Minimal footprint close to the standard charging station area.
- No internal maneuvering area: the robot docks and undocks along one fixed trajectory.
- About 1500 mm of straight, level, obstacle-free path must remain in front of the charging station.
- Separate robot bay from storage/service compartment.
- Removable or hinged roof for access to documentation, power supplies, spare parts, and maintenance items.
- Buildable with basic tools, without CNC.
- Main structure assembled on timber battens rather than precision plywood slots.
- Printable facade graphics for stone, slate roof, stained glass, and decorative shadows.

## Technical reference dimensions

Reference dimensions to verify against the actual Luba 3 AWD installation:

| Item | Length | Width | Height |
|---|---:|---:|---:|
| Measured minimum clear envelope | 850 mm | 650 mm | 450 mm |
| **Current lower box external size** | **1000 mm** | **900 mm** | **560 mm** |
| Approximate clear size with 12 mm plywood | ~976 mm | ~876 mm | ~560 mm |

Older reference data retained for context:

| Item | Length | Width | Height |
|---|---:|---:|---:|
| LUBA 2 AWD robot | 690 mm | 513 mm | 273 mm |
| Charging base / station MTL23CHS0001 | 610 mm | 570 mm | 350 mm |

## Current approved dimensions

### Lower functional box

- **Length:** 1000 mm
- **Width:** 900 mm
- **Robot bay / wall height:** 560 mm

The visible front face ratio is:

- **900 / 560 = 1.607**
- Golden ratio: **1.618**

This is approximately 0.7% below the golden ratio and gives the lower module a balanced church-like facade while preserving practical internal clearance.

### Gable roof

- **Gable rise above the lower box:** 280–300 mm
- **Height from ground to roof ridge:** 840–860 mm
- **Approximate roof footprint:** 1040 × 940 mm with about 20 mm overhang on each side

The roof rise is measured above the 560 mm rectangular box height. It is not included in the lower-box height.

### Wide tower

The current concept uses a wide tower centered over both roof slopes rather than a narrow ridge tower.

- **Width:** 480–520 mm
- **Depth:** 450–500 mm
- **Visible height above the roof:** approximately 450–500 mm
- **Approximate total structure height:** 1290–1360 mm

The tower must be supported by the roof-module structure and internal framing, not by roof cladding alone.

### Recommended robot bay

- **Internal length:** approximately 976 mm
- **Internal width:** approximately 876 mm
- **Working height:** approximately 560 mm
- **Gate opening:** functional low mower entry, not cathedral-height

## Cut sheets

- [Current lower box cut sheet — 1250 × 2500 mm](cut-sheets/baseline-lower-box-1250x2500.md)

## Internal layout

The garage is divided into two zones:

### Lower robot bay

- Robot + charging station only.
- No high threshold at the entrance.
- Cable route behind or beside the station.
- Ventilation and drainage considered from the beginning.

### Upper/service compartment

Created by installing a removable ceiling above the robot bay.

Suggested storage:

- Charging power supply / adapter, if safely ventilated.
- Documentation and warranty papers.
- Spare blades and screws.
- Cleaning brush.
- Small tools.
- Spare 3D-printed decorative parts.

## Repository structure

```text
docs/            Project documentation
cut-sheets/      Plywood cutting plans
facade-print/    Vinyl print templates and specs
3d-print/        Printable Gothic decorative modules
electrical/      LED, cable routing, power supply compartment
images/          Renders, construction photos, examples
```

## Current status

The current dimensional baseline is fixed at **1000 × 900 × 560 mm** for the lower box, with a **280–300 mm** gable rise and a wide tower approximately **480–520 mm wide**, **450–500 mm deep**, and **450–500 mm high above the roof**. Final production drawings still require verification against the real Luba 3 AWD charging station, construction material thickness, hinge design, and installation site before cutting.