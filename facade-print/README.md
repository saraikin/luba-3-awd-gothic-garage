# Facade print package

This directory contains the reproducible source for the lower-box vinyl graphics: measured geometry, realistic wall artwork, deterministic wall cleanup, exact cut paths, editable vector stained glass, floor texture generation and GitHub Actions automation.

## Current design

### Main wall film

- Finished file size: **3875 × 610 mm**.
- Wall sequence: **498.5 + 925 + 998 + 925 + 498.5 + 30 mm**.
- The upper **40 mm** folds over the top surface.
- Entrance: **604 mm** lower width, **600 mm** upper width, **365 mm** height and **87.5 mm** corner radius.

### Buttresses and their shadows removed

The realistic source image originally contained seven projecting buttresses and broad cast shadows. Removing only the visible buttress pixels left dark silhouettes in the wall, so the generator now rebuilds four wider cleanup zones from explicitly selected shadow-free masonry strips.

The cleanup pipeline:

1. composites several clean masonry strips with cosine-feathered overlaps;
2. preserves the original entrance and window surrounds with geometry-derived masks;
3. performs low-frequency illumination normalization over the former shadow zones;
4. tapers the correction near the bottom so the original moss and ground weathering remain natural.

Editable settings are stored under `wall.buttress_removal`:

- `cleanup_zones` — broad areas containing each buttress and its shadow;
- `clean_source_intervals_mm` — verified plain-masonry source strips;
- `tile_min_width_mm` / `tile_max_width_mm` — source-piece variation;
- `tile_overlap_mm` and `feather_mm` — seamless blending;
- `window_frame_preserve_mm` and `entrance_frame_preserve_mm` — protected decorative surrounds.

No rear-centre buttress is retained. The rear installation seam is plain masonry.

The build exports `BUTTRESS_AND_SHADOW_REMOVAL_DIAGNOSTICS.jpg` and `WALL_SHADOW_FREE_PROMINENT_QUOINS_PREVIEW.jpg`.

### Corner treatment: dressed-limestone quoins

The four physical box corners use flat reinforced corner masonry: **quoins**, also described as **corner rustication** or **quoin stones**.

The quoin centres are derived from the cumulative wall-segment dimensions and coincide exactly with the four fold lines:

- **498.5 mm** — rear-left corner;
- **1423.5 mm** — front-left corner;
- **2421.5 mm** — front-right corner;
- **3346.5 mm** — rear-right corner.

Every masonry course crosses its fold line. Long and short legs alternate between the adjacent wall faces, so the corner reads as one continuous reinforced element after wrapping.

The quoins no longer copy the field-wall texture. Each block receives a separately generated rough dressed-limestone surface with:

- multi-scale mineral variation;
- pits and short chisel marks;
- occasional fine cracks;
- subtle printed edge bevels;
- a controlled warm limestone palette distinct from the dark irregular field masonry.

Current editable geometry:

- row height: **68 mm**;
- long leg: **205 mm** from the fold;
- short leg: **150 mm** from the fold;
- mortar gap: **5 mm**;
- fold shadow: **2 mm**.

`CORNER_QUOIN_ALIGNMENT_DIAGNOSTICS.jpg` verifies the four fold centres, and `FRONT_QUOIN_NEW_TEXTURE_DETAIL.jpg` shows the new material at print resolution.

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

The output is deterministic. `random_seed` controls masonry replacement choices, quoin material variation, wood grain, plank widths, board lengths and joints.

## Print materials

1. Wall: opaque white permanent polymeric or cast exterior PVC, matte UV laminate.
2. Stained glass: translucent/backlit film, without opaque white underprint behind colored areas.
3. Attic floor: exterior PVC with matte UV laminate rated for horizontal exposure.

Print all PDFs at **100%**, never `Fit to page`. The print shop should convert colors using its own printer/ink/film ICC profile and first test color, adhesion and actual LED backlighting.
