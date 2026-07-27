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

No rear-centre buttress is retained. The rear installation seam is plain masonry.

### Corner treatment: seamless dressed-limestone quoins

The four physical box corners use flat reinforced corner masonry: **quoins**, also described as **corner rustication** or **quoin stones**.

The nominal quoin centres coincide with the four fold lines:

- **498.5 mm** — rear-left corner;
- **1423.5 mm** — front-left corner;
- **2421.5 mm** — front-right corner;
- **3346.5 mm** — rear-right corner.

Each row is generated as one continuous dressed-stone block across the nominal fold. There is no printed divider, colour transition, black outline or artificial fold shadow at the corner coordinate. A small installation offset therefore remains inside the same stone texture.

Current geometry:

- row height: **34 mm**;
- long extent: **90 mm** from the fold;
- short extent: **65 mm** from the fold;
- mortar gap: **3 mm**.

The source stone is generated oversized and cropped inward by **4 mm** to remove any baked perimeter. Relief is created only with a soft blurred cast shadow and the stone's own tonal variation.

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

### Attic floor

- Print file: **1004 × 931 mm**.
- Trim size: **998 × 925 mm**.
- Render resolution: **150 dpi**.
- Plank width: **14–22 mm**.
- Plank-piece length: **180–360 mm**.
- Adjacent joints are kept at least **45 mm** apart where possible.

## Reproduce

```bash
cd facade-print
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_print_package_v2.py --config config.json --output generated
```

Print all PDFs at **100%**, never `Fit to page`.
