# Facade print package

This directory contains the reproducible source for the lower-box vinyl graphics: measured geometry, realistic wall artwork, deterministic corner treatment, exact cut paths, editable vector stained glass, floor texture generation and GitHub Actions automation.

## Current design

### Main wall film

- Finished file size: **3875 × 610 mm**.
- Wall sequence: **498.5 + 925 + 998 + 925 + 498.5 + 30 mm**.
- The upper **40 mm** folds over the top surface.
- Entrance: **604 mm** lower width, **600 mm** upper width, **365 mm** height and **87.5 mm** corner radius.

### Buttresses removed

The realistic source image originally contained seven projecting buttresses. The generator now removes all seven before any corner treatment is added. Each configured zone is replaced with a feathered clone of nearby plain realistic masonry; the entrance and window geometry remain unchanged.

The editable removal zones are stored under `wall.buttress_removal.zones` in `config.json`. The build exports `BUTTRESS_REMOVAL_DIAGNOSTICS.jpg` so every former buttress position can be checked.

No rear-centre buttress is retained. The rear installation seam is plain masonry.

### Corner treatment: prominent quoins / corner rustication

The four physical box corners use flat reinforced corner masonry: **quoins**, also described as **corner rustication** or **quoin stones**.

The quoin centres are derived from the cumulative wall-segment dimensions and therefore coincide exactly with the four fold lines:

- **498.5 mm** — rear-left corner;
- **1423.5 mm** — front-left corner;
- **2421.5 mm** — front-right corner;
- **3346.5 mm** — rear-right corner.

Every masonry course crosses its fold line. Long and short legs alternate between the two adjacent wall faces, so the corner reads as one continuous reinforced element after the film is wrapped.

Current editable quoin geometry:

- row height: **62 mm**;
- long leg: **185 mm** from the fold;
- short leg: **135 mm** from the fold;
- mortar gap: **4 mm**;
- fold shadow: **2.5 mm**.

The quoin stones are brighter and higher-contrast than the field masonry, with stronger outlines and highlights. The generator exports `CORNER_QUOIN_ALIGNMENT_DIAGNOSTICS.jpg`; its red lines pass through the exact four fold centres.

### Rear-wall seam

The artwork circuit ends at **3845 mm**. The following **30 mm** is an exact pixel-for-pixel copy of the beginning of the completed strip and serves as the installation overlap.

### Lit stained-glass windows

The white exterior wall film is opaque. The two openings are cut through the film and plywood; colored inserts are printed separately on translucent/backlit film and attached from inside.

- Left window centre: **1047.5 mm**.
- Right window centre: **2733.5 mm**.
- Visible opening: **90 × 294 mm**.
- Opening top: **118 mm**.
- Pointed-arch height: **86 mm**.
- Mounting bleed: **8 mm**.

The raster opening masks and SVG/PDF cut contours use the same geometry.

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
├── config.json
├── requirements.txt
├── Makefile
├── assets/
├── scripts/
│   ├── textures.py
│   ├── stained_glass.py
│   ├── common.py
│   ├── wall_preprocess.py
│   ├── generate_print_package.py
│   └── generate_print_package_v2.py
└── generated/

.github/workflows/facade-print.yml
```

## Reproduce

Python 3.11 or newer:

```bash
cd facade-print
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_print_package_v2.py --config config.json --output generated
```

Or:

```bash
make generate
```

The output is deterministic. `random_seed` controls masonry replacement choices, quoin texture variation, wood grain, plank widths, board lengths and joints.

## Modify

Dimensions are in `config.json`:

- `wall.segments_mm` — panels and rear overlap;
- `wall.buttress_removal.zones` — exact original-buttress areas and plain-masonry clone sources;
- `wall.buttress_removal.feather_mm` — blend width at replacement edges;
- `wall.corner_quoins.boundary_indexes` — segment boundaries that receive quoins;
- `wall.corner_quoins.row_height_mm` — quoin course height;
- `wall.corner_quoins.long_leg_mm` / `short_leg_mm` — alternating distances from the fold;
- `wall.corner_quoins.mortar_mm` — gap between courses;
- `wall.corner_quoins.fold_shadow_mm` — printed fold emphasis;
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

Print all PDFs at **100%**, never `Fit to page`. The print shop should convert colors using its own printer/ink/film ICC profile and first test color, adhesion and actual LED backlighting.
