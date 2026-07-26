# Generated files

Run `make generate` from `facade-print/` to rebuild the complete print package. Large PDFs, previews, texture rasters and hybrid SVG files are intentionally not committed because they are deterministic outputs of the tracked source code.

Generated print-shop files include:

- `01_WALLS_STONE_WINDOW_OPENINGS_3875x610mm_100pct.pdf`
- `01B_WALL_CUT_CONTOURS_3875x610mm.pdf` and `.svg`
- `02_STAINED_GLASS_COMPLEX_TRANSLUCENT_280x330mm.pdf`
- `03_ATTIC_FLOOR_FINE_PLANKS_1004x931mm_100pct.pdf`
- `wall_wrap_hybrid_with_cut_layers.svg`
- `attic_floor_fine_planks_hybrid_source.svg`
- `PREVIEW.jpg`

The GitHub Actions workflow uploads these files as a downloadable build artifact.
