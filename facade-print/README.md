# Facade print package

This directory contains the complete, reproducible source for the lower-box vinyl graphics.
It includes the measured geometry, source textures, generator script, technical cut layers,
vector stained glass and a preview of the current result. Print-ready PDFs are generated reproducibly.

## Current design

### Main wall film

- Finished file size: **3875 × 610 mm**.
- Wall sequence: **498.5 + 925 + 998 + 925 + 498.5 + 30 mm**.
- The final **30 mm** is the rear-wall overlap.
- The upper **40 mm** folds over the top surface.
- The entrance cut follows the measured **604 mm** lower width, **600 mm** upper width,
  **365 mm** height and **87.5 mm** corner radius.

### Lit stained-glass windows

The main white exterior PVC film is opaque, so the stained-glass graphics are not printed
as part of the wall film. Two openings are cut through the film and plywood. The colored
inserts are printed separately on translucent/backlit film and attached from inside.

- Left window: Tree of Life.
- Right window: rose, stars and fleur-de-lis.
- Visible opening: **98 × 300 mm**.
- Pointed-arch height: **98 mm**.
- Mounting bleed: **8 mm** around each insert.

### Attic floor

- Print file: **1004 × 931 mm**.
- Trim size: **998 × 925 mm**.
- Model plank width: **14–22 mm**.
- At approximately 1:16 architectural scale, this represents boards about **220–350 mm** wide.

## Directory structure

```text
facade-print/
├── config.json                         Exact editable dimensions and generation settings
├── requirements.txt                    Python dependencies
├── Makefile                            Convenience commands
├── assets/
│   ├── wall_base_realistic.jpg         Master realistic stone wall artwork before window cuts
│   ├── wood_base_realistic.jpg         Master aged-wood texture used to construct narrow planks
│   └── README.md                        Asset provenance and usage notes
├── scripts/
│   └── generate_print_package.py       Complete deterministic generator
└── generated/
    ├── 01B_WALL_CUT_CONTOURS_...svg   Exact entrance/window cutting paths
    ├── stained_glass_...svg            Editable vector stained glass
    └── README_FOR_PRINT_SHOP_...       Material and installation instructions

.github/workflows/facade-print.yml      Builds downloadable print PDFs as an Actions artifact
```

## Reproducing the result

Python 3.11 or newer is recommended.

```bash
cd facade-print
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_print_package.py --config config.json --output generated
```

Or run:

```bash
make generate
```

The generator is deterministic: the floor-plank arrangement is controlled by
`random_seed` in `config.json`.

## Modifying the design

Most dimensional changes require editing only `config.json`:

- `wall.segments_mm` — panel widths and rear overlap;
- `entrance` — opening size and corner radius;
- `windows.centers_x_mm` — window positions along the unwrapped wall strip;
- `windows.width_mm`, `height_mm`, `arch_height_mm` — opening geometry;
- `floor.plank_width_min_mm`, `plank_width_max_mm` — model plank scale;
- `dpi` — output raster resolution.

The stained-glass geometry and colors are generated in
`scripts/generate_print_package.py`, primarily in `glass_group()`.
The two designs are intentionally vector-based and can be modified without changing the
stone or wood texture assets.

## Print materials

1. **Wall film:** opaque white permanent polymeric or cast exterior PVC, with matte UV laminate.
2. **Stained glass:** translucent/backlit or clear stained-glass film. Do not add an opaque white
   underprint behind the colored areas.
3. **Attic floor:** exterior PVC film with matte UV laminate rated for horizontal exposure.

Print every PDF at **100% scale**. Do not use `Fit to page`. The print shop should perform
color conversion using the ICC profile for its selected printer, ink, film and laminate.
A color, adhesion and actual-LED backlighting test is required before full production.

## Source-art note

The realistic stone, wood and visual-reference images in `assets/` were generated specifically
for this project and then refined into the measured print layout. They are committed with the
project so the output does not depend on an unavailable external image or an earlier chat session.
