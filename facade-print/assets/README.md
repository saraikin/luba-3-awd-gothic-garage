# Source assets

These files are the reproducible visual inputs for `scripts/generate_print_package.py`.
The JPEG bytes are stored as numbered Base64 text chunks; the generator concatenates and decodes them automatically.

- `wall_base_realistic.jpg.b64.*` — full 3875 × 610 mm wall artwork at the baseline raster size,
  before the two stained-glass window openings are removed. It already contains the stonework,
  entrance surround, buttresses, corner masonry and weathering.
- `wood_base_realistic.jpg.b64.*` — aged-wood texture source. The generator samples narrow vertical
  strips from this image to build correctly scaled 14–22 mm planks, then adds staggered joints
  and small nail heads.

The artwork was generated specifically for this garage project. No downloaded stock texture or
third-party photograph is required to reproduce the current output.
