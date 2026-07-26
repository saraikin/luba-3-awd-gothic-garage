# Facade print package

This directory contains the complete reproducible source for the lower-box vinyl graphics: measured geometry, deterministic stone and wood texture generators, exact cut paths, editable vector stained glass, print export code and GitHub Actions automation.

## Current design

### Main wall film

- Finished file size: **3875 × 610 mm**.
- Wall sequence: **498.5 + 925 + 998 + 925 + 498.5 + 30 mm**.
- The final **30 mm** is the rear-wall overlap.
- The upper **40 mm** folds over the top surface.
- Entrance: **604 mm** lower width, **600 mm** upper width, **365 mm** height and **87.5 mm** corner radius.

### Lit stained-glass windows

The white exterior wall film is opaque. The two openings are cut through the film and plywood; the colored inserts are printed separately on translucent/backlit film and attached from inside.

- Left: Tree of Life.
- Right: rose, stars and fleur-de-lis.
- Visible opening: **98 × 300 mm**.
- Pointed-arch height: **98 mm**.
- Mounting bleed: **8 mm**.

### Attic floor

- Print file: **1004 × 931 mm**.
- Trim size: **998 × 925 mm**.
- Model plank width: **14–22 mm**, approximately **220–350 mm** at 1:16 scale.

## Structure

```text
facade-print/
├── config.json                         Editable dimensions and generation settings
├── requirements.txt                    Python dependencies
├── Makefile                            Convenience command
├── scripts/
│   ├── textures.py                     Stone and aged-wood texture generators
│   ├── stained_glass.py                Editable vector stained-glass generator
│   ├── common.py                       Geometry and export helpers
│   └── generate_print_package.py       Complete package generator
└── generated/                          Small tracked reference files; large outputs are rebuilt

.github/workflows/facade-print.yml      Builds downloadable PDFs/SVGs as an Actions artifact
```

## Reproduce

Python 3.11 or newer:

```bash
cd facade-print
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_print_package.py --config config.json --output generated
```

Or:

```bash
make generate
```

The output is deterministic. `random_seed` controls stone variation, weathering, wood grain selection, plank widths and joints.

## Modify

Dimensions are in `config.json`:

- `wall.segments_mm` — panels and rear overlap;
- `entrance` — opening dimensions and radius;
- `windows` — positions, opening geometry and mounting bleed;
- `floor.plank_width_min_mm` / `plank_width_max_mm` — scale of floorboards;
- `dpi` — generated raster resolution.

Visual source code:

- `scripts/textures.py` — stone palette, stone size, mortar, corner blocks, buttresses, entrance/window surrounds, moss, wood grain and knots;
- `scripts/stained_glass.py` — colors, lead lines, Tree of Life, rose and fleur-de-lis;
- `scripts/generate_print_package.py` — panel composition, openings, floor joints, PDF/SVG exports and preview.

No stock photographs, external downloads or earlier chat assets are required.

## Print materials

1. Wall: opaque white permanent polymeric or cast exterior PVC, matte UV laminate.
2. Stained glass: translucent/backlit film, without opaque white underprint behind colored areas.
3. Attic floor: exterior PVC with matte UV laminate rated for horizontal exposure.

Print all PDFs at **100%**, never `Fit to page`. The print shop should convert colors using its own printer/ink/film ICC profile and first test color, adhesion and the actual LED backlighting.
