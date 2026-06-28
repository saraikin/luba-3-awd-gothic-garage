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
| LUBA 2 AWD robot | 690 mm | 513 mm | 273 mm |
| Charging base / station MTL23CHS0001 | 610 mm | 570 mm | 350 mm |
| Minimum shelter internal size | 900 mm | 600 mm | 500 mm |

## Baseline dimensions

Recommended external footprint:

- **Length:** 1000–1200 mm
- **Width:** 800–1000 mm
- **Overall visual height:** 1300–1500 mm with false floors and tower

Recommended robot bay:

- **Internal length:** 900–1080 mm
- **Internal width:** 600–860 mm
- **Robot bay working height:** 500–650 mm
- **Gate opening:** approx. 700 mm wide × 420 mm high

The gate does not need to be cathedral-height. It only needs to allow safe Luba entry and exit.

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

Concept and first documentation draft. Exact charging pad dimensions should be verified on the real Luba 3 AWD installation before final cut files are treated as production-ready.
