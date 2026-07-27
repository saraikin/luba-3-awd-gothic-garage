# Facade print package

This directory contains the reproducible source for the lower-box vinyl graphics: measured geometry, realistic wall artwork, deterministic corner treatment, exact cut paths, editable vector stained glass, floor texture generation and GitHub Actions automation.

## Current design

### Main wall film

- Finished file size: **3875 × 610 mm**.
- Wall sequence: **498.5 + 925 + 998 + 925 + 498.5 + 30 mm**.
- The upper **40 mm** folds over the top surface.
- Entrance: **604 mm** lower width, **600 mm** upper width, **365 mm** height and **87.5 mm** corner radius.

### Corner treatment: quoins / corner rustication

The four physical box corners no longer rely on projecting buttresses. They use flat reinforced corner masonry: **quoins**, also described as **corner rustication** or **quoin stones**.

The quoin centres are derived from the cumulative wall-segment dimensions and therefore coincide exactly with the four fold lines:

- **498.5 mm** — rear-left corner;
- **1423.5 mm** — front-left corner;
- **2421.5 mm** — front-right corner;
- **3346.5 mm** — rear-right corner.

Every masonry course crosses its fold line. Long and short legs alternate between the two adjacent wall faces, so the corner reads as one continuous reinforced element after the film is wrapped.

Default editable quoin geometry:

- row height: **55 mm**;
- long leg: **150 mm** from the fold;
- short leg: **105 mm** from the fold;
- mortar gap: **3 mm**;
- fold shadow: **1.5 mm**.

The generator also exports `CORNER_QUOIN_ALIGNMENT_DIAGNOSTICS.jpg`. Its red lines show the exact four folds through the centres of the generated corner masonry.

### Rear-wall seam

The artwork circuit ends at **3845 mm**. The following **30 mm** is an exact pixel-for-pixel copy of the beginning of the finished strip and serves as the installation overlap.

A separate realistic buttress remains centred on the rear-wall installation seam. It is not one of the four physical corner elements.

### Lit stained-glass windows

The white exterior wall film is opaque. The two openings are cut through the film and plywood; the colored inserts are printed separately on translucent/backlit film and attached from inside.

- Left window centre: **1047.5 mm**.
- Right window centre: **2733.5 mm**.
- Visible opening: **90 × 294 mm**.
- Opening top: **118 mm**.
- Pointed-arch height: **86 mm**.
- Mounting bleed: **8 mm**.

The raster opening masks and the SVG/PDF cut contours use the same geometry.

### Attic floor

- Print file: **1004 × 931 mm**.
- Trim size: **998 × 925 mm**.
- Render resolution: **150 dpi**.
- Plank width: **14–22 mm**.
- Plank-piece length: **180–360 mm**.
- Adjacent joints are kept at least **45 mm** apart where possible.

Every plank piece receives its own grain, knots, tonal variation and random seed at the final physical print scale.

## Structure

```text
facade-print/
├── config.json                         Editable dimensions and generation settings
├── requirements.txt                    Python dependencies
├── Makefile                            Convenience command
├── assets/                             Realistic wall source, stored directly or as Base64 chunks
├── scripts/
│   ├── textures.py                     Physically scaled wood generator
│   ├── stained_glass.py                Editable vector stained-glass generator
│   ├── common.py                       Geometry and export helpers
│   └── generate_print_package.py       Wall, quoins, cuts, floor and diagnostics
└── generated/                          Generated print and diagnostic files

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

The output is deterministic. `random_seed` controls quoin texture variation, wood grain, plank widths, board lengths and joints.

## Modify

Dimensions are in `config.json`:

- `wall.segments_mm` — panels and rear overlap;
- `wall.corner_quoins.boundary_indexes` — segment boundaries that receive quoins;
- `wall.corner_quoins.row_height_mm` — quoin course height;
- `wall.corner_quoins.long_leg_mm` / `short_leg_mm` — alternating distances from the fold;
- `wall.corner_quoins.mortar_mm` — gap between courses;
- `entrance` — opening dimensions and radius;
- `windows` — positions and opening geometry;
- `floor.dpi` — floor raster resolution;
- `floor.plank_width_min_mm` / `plank_width_max_mm` — scale of floorboards;
- `floor.plank_length_min_mm` / `plank_length_max_mm` — board-piece lengths;
- `floor.joint_clearance_mm` — preferred distance between adjacent joints;
- `dpi` — wall and stained-glass raster resolution.

## Print materials

1. Wall: opaque white permanent polymeric or cast exterior PVC, matte UV laminate.
2. Stained glass: translucent/backlit film, without opaque white underprint behind colored areas.
3. Attic floor: exterior PVC with matte UV laminate rated for horizontal exposure.

Print all PDFs at **100%**, never `Fit to page`. The print shop should convert colors using its own printer/ink/film ICC profile and first test color, adhesion and the actual LED backlighting.
