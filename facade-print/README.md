# Facade print package

This directory is the reproducible source for the lower-box vinyl graphics: measured geometry, realistic wall cleanup, seamless corner quoins, exact cut paths, stained glass, floor texture generation, validation and GitHub Actions automation.

## Fixed physical geometry

### Main wall film

- Finished file size: **3875 × 610 mm**.
- Wall sequence: **498.5 + 925 + 998 + 925 + 498.5 + 30 mm**.
- The upper **40 mm** folds over the top surface.
- Entrance: **604 mm** lower width, **600 mm** upper width, **365 mm** height and **87.5 mm** corner radius.
- The final **30 mm** is an exact copy of the beginning and forms the rear installation overlap.

### Windows

- Left centre: **1047.5 mm**.
- Right centre: **2733.5 mm**.
- Visible opening: **90 × 294 mm**.
- Opening top: **118 mm**.
- Pointed-arch height: **86 mm**.
- Mounting bleed: **8 mm**.

The raster openings and vector cut contours use the same geometry functions.

### Buttress removal

The realistic source originally contained seven projecting buttresses and broad cast shadows. The current preprocessing rebuilds wider cleanup zones from selected shadow-free masonry strips, preserves the entrance/window surrounds and normalizes residual low-frequency darkness. No rear-centre buttress remains.

### Seamless dressed-limestone quoins

The four physical corners are centred on the fold coordinates:

- **498.5 mm** — rear-left;
- **1423.5 mm** — front-left;
- **2421.5 mm** — front-right;
- **3346.5 mm** — rear-right.

Each row is one continuous stone spanning the nominal fold. There is no divider, colour transition, black outline or artificial fold line, so a small installation offset remains hidden inside the same texture.

Current geometry:

- row height: **34 mm**;
- long extent: **90 mm** from the fold;
- short extent: **65 mm** from the fold;
- mortar gap: **3 mm**.

The quoin material is generated independently from the wall masonry. Relief comes from mineral variation and a soft blurred shadow, not a drawn frame.

### Attic floor

- Print file: **1004 × 931 mm**.
- Trim size: **998 × 925 mm**.
- Render resolution: **150 dpi**.
- Plank width: **14–22 mm**.
- Plank-piece length: **180–360 mm**.
- Adjacent joints are separated by at least **45 mm** where possible.

## Source asset

The production wall raster is intentionally not committed as an ordinary Git binary. Its authoritative archive is recorded in `assets/source_asset.json` with:

- Google Drive file ID and owner-access URL;
- archive SHA-256;
- extracted asset SHA-256;
- original PNG SHA-256;
- dimensions, DPI, format and encoding quality.

The expected archive is `luba_facade_source_asset_q85.zip`. The bootstrap script refuses to install an archive or image with a different checksum or size.

## Reproduce from a clean checkout

```bash
cd facade-print
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
make setup
make reproduce ASSET_ARCHIVE=/path/to/luba_facade_source_asset_q85.zip
```

Equivalent individual commands:

```bash
python scripts/bootstrap_asset.py --archive /path/to/luba_facade_source_asset_q85.zip
python scripts/validate_project.py --config config.json --require-asset
python scripts/generate_print_package_v2.py --config config.json --output generated
python scripts/validate_project.py --config config.json --require-asset --generated generated
```

`requirements.lock` pins the exact tested Python dependency versions. `config.json` contains every editable physical dimension and visual parameter. `random_seed` makes procedural parts deterministic.

## Validation

`validate_project.py` checks:

- total strip length and all fold coordinates;
- current quoin dimensions and corner indexes;
- entrance and window geometry;
- floor dimensions and DPI;
- source asset checksum and pixel dimensions;
- presence and basic dimensions of generated deliverables.

GitHub Actions always validates the code and geometry. It generates the full package when the source archive is available through a direct workflow input URL or repository variable `FACADE_ASSET_ARCHIVE_URL`.

## Important files

```text
facade-print/
├── config.json
├── requirements.txt
├── requirements.lock
├── Makefile
├── assets/
│   └── source_asset.json
├── scripts/
│   ├── bootstrap_asset.py
│   ├── validate_project.py
│   ├── generate_print_package.py
│   ├── generate_print_package_v2.py
│   ├── wall_preprocess.py
│   ├── wall_preprocess_v2.py
│   ├── common.py
│   ├── stained_glass.py
│   └── textures.py
└── generated/
```

Print every production PDF at **100%**, never `Fit to page`.
