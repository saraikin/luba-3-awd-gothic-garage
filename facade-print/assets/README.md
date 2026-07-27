# Facade source asset

The production source is `wall_artwork_realistic_75dpi.webp` at **11442 × 1801 px**, corresponding to **3875 × 610 mm at 75 dpi**.

The binary is restored from `luba_facade_source_asset_q85.zip`. The authoritative Drive file ID, archive checksum, extracted image checksum and original PNG checksum are stored in `source_asset.json`.

From `facade-print/`:

```bash
python scripts/bootstrap_asset.py --archive /path/to/luba_facade_source_asset_q85.zip
python scripts/bootstrap_asset.py --verify-only
```

The bootstrap operation is atomic. It refuses an archive with the wrong SHA-256, an image with the wrong SHA-256, or an image with dimensions other than 11442 × 1801 px.

Do not replace the source image without deliberately updating both `source_asset.json` and the project preview after visual review.
