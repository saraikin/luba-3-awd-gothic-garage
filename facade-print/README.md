# Facade print package

This directory contains the reproducible source for the lower-box vinyl graphics: measured geometry, realistic wall artwork, deterministic wall cleanup, exact cut paths, editable vector stained glass, floor texture generation and GitHub Actions automation.

## Current design

### Main wall film

- Finished file size: **3875 × 610 mm**.
- Wall sequence: **498.5 + 925 + 998 + 925 + 498.5 + 30 mm**.
- The upper **40 mm** folds over the top surface.
- Entrance: **604 mm** lower width, **600 mm** upper width, **365 mm** height and **87.5 mm** corner radius.

### Buttresses and their shadows removed

The realistic source image originally contained seven projecting buttresses and broad cast shadows. The generator rebuilds four wider cleanup zones from selected shadow-free masonry strips, preserves the entrance and window surrounds, and normalizes residual low-frequency darkness. Bottom moss and ground weathering are retained.

No rear-centre buttress is retained. The rear installation seam is plain masonry.

The build exports `BUTTRESS_AND_SHADOW_REMOVAL_DIAGNOSTICS.jpg` and `WALL_SHADOW_FREE_PROMINENT_QUOINS_PREVIEW.jpg`.

### Corner treatment: seamless dressed-limestone quoins

The four physical box corners use flat reinforced corner masonry: **quoins**, also described as **corner rustication** or **quoin stones**.

The nominal fold coordinates are:

- **498.5 mm** — rear-left corner;
- **1423.5 mm** — front-left corner;
- **2421.5 mm** — front-right corner;
- **3346.5 mm** — rear-right corner.

Each row is generated as **one uninterrupted stone block spanning both sides of the nominal fold**. There is no printed divider, colour transition, black outline or artificial fold shadow at the corner coordinate. If the physical fold shifts slightly during installation, it still falls inside the same continuous stone texture and the error is not exposed.

Long and short extents alternate by row, but they are only the outer limits of one continuous block:

- row height: **34 mm**;
- long extent from the fold: **150 mm**;
- short extent from the fold: **105 mm**;
- mortar gap: **3 mm**.

The blocks use a separate rough dressed-limestone texture with mineral variation, pores, chisel marks and occasional fine cracks. The former hard black frame has been removed. Relief is conveyed by:

- one soft blurred shadow around the complete stone;
- a slight downward/right shadow offset;
- the stone texture's natural light and dark variation;
- gently rounded printed corners.

The stone texture is generated oversized and cropped inward by **4 mm**, removing the source generator's baked perimeter bevel before the soft shadow is applied.

`CORNER_QUOIN_ALIGNMENT_DIAGNOSTICS.jpg` verifies nominal fold positions, while `FRONT_QUOIN_NEW_TEXTURE_DETAIL.jpg` shows the final material at print resolution.

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
│   ├── wall_preprocess_v2.py
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

The output is deterministic. `random_seed` controls masonry replacement choices, quoin material variation, wood grain, plank widths, board lengths and joints.

## Print materials

1. Wall: opaque white permanent polymeric or cast exterior PVC, matte UV laminate.
2. Stained glass: translucent/backlit film, without opaque white underprint behind colored areas.
3. Attic floor: exterior PVC with matte UV laminate rated for horizontal exposure.

Print all PDFs at **100%**, never `Fit to page`. The print shop should convert colors using its own printer/ink/film ICC profile and first test color, adhesion and actual LED backlighting.
