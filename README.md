# Luba 3 AWD Gothic Garage

DIY project for building a compact protective garage for the Mammotion Luba 3 AWD robot mower, styled as a small Gothic church.

The design is intentionally split into stages:

1. **Stage 1: functional protection** — plywood box, roof, weather protection, safe robot entry, charging station access.
2. **Stage 2: facade and windows** — printed outdoor vinyl film, optional window cut-outs, acrylic inserts, warm LED lighting.
3. **Stage 3: Gothic decor** — false floors, tower, spires, rose window, arches, columns, erkers/bay-window modules, 3D-printed elements.

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
| Baseline lower box external size | 1050 mm | 760 mm | 470 mm |
| Baseline lower box approximate clear size | ~1026 mm | ~736 mm | ~470 mm |

Older reference data retained for context:

| Item | Length | Width | Height |
|---|---:|---:|---:|
| LUBA 2 AWD robot | 690 mm | 513 mm | 273 mm |
| Charging base / station MTL23CHS0001 | 610 mm | 570 mm | 350 mm |

## Baseline dimensions

Recommended external footprint for the lower functional box:

- **Length:** 1050 mm
- **Width:** 760 mm
- **Robot bay working height:** 470 mm

Recommended visual upper module:

- **Gable rise above lower box:** 280–320 mm
- **Roof footprint:** approx. 1090 × 820 mm with small overhangs
- **Optional square tower:** 220–280 mm wide

Recommended robot bay:

- **Internal length:** approx. 1026 mm
- **Internal width:** approx. 736 mm
- **Robot bay working height:** approx. 470 mm
- **Gate opening:** functional low mower entry, not cathedral-height

The front lower box ratio is approximately 760 / 470 = 1.617, close to the golden ratio. This creates a stable visual base for the hinged gable roof and optional tower.

## Cut sheets

- [Baseline lower box cut sheet — 1250 × 2500 mm](cut-sheets/baseline-lower-box-1250x2500.md)

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

Concept and first documentation draft. The measured minimum clear envelope is now 850 × 650 × 450 mm. Baseline lower box cut sheet added for a 1250 × 2500 mm plywood sheet. Final cut files still require verification against the real Luba 3 AWD charging station and installation site before production.
