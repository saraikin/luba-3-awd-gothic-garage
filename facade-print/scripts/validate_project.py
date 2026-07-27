#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_GENERATED = {
    "01_WALLS_STONE_WINDOW_OPENINGS_3875x610mm_100pct.pdf",
    "01B_WALL_CUT_CONTOURS_3875x610mm.pdf",
    "01B_WALL_CUT_CONTOURS_3875x610mm.svg",
    "02_STAINED_GLASS_COMPLEX_TRANSLUCENT_280x330mm.pdf",
    "03_ATTIC_FLOOR_FINE_PLANKS_1004x931mm_100pct.pdf",
    "PREVIEW.jpg",
    "WALL_ALIGNMENT_DIAGNOSTICS.jpg",
    "CORNER_QUOIN_ALIGNMENT_DIAGNOSTICS.jpg",
    "BUTTRESS_AND_SHADOW_REMOVAL_DIAGNOSTICS.jpg",
    "FLOOR_DETAIL_250x250mm_PREVIEW.jpg",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def close(actual: float, expected: float, tolerance: float = 0.01) -> None:
    if abs(actual - expected) > tolerance:
        raise ValueError(f"Expected {expected}, received {actual}")


def validate_geometry(config: dict) -> None:
    wall = config["wall"]
    segments = wall["segments_mm"]
    close(sum(segments), wall["width_mm"])
    if len(segments) != 6:
        raise ValueError("Wall strip must contain five wall segments plus overlap")
    if segments[-1] != 30.0:
        raise ValueError("Installation overlap must remain 30 mm")

    physical_folds = []
    total = 0.0
    for segment in segments[:-1]:
        total += segment
        physical_folds.append(total)
    expected_folds = [498.5, 1423.5, 2421.5, 3346.5, 3845.0]
    for actual, expected in zip(physical_folds, expected_folds, strict=True):
        close(actual, expected)

    quoins = wall["corner_quoins"]
    if quoins["boundary_indexes"] != [1, 2, 3, 4]:
        raise ValueError("Quoins must be placed on the four physical box folds")
    close(quoins["row_height_mm"], 34.0)
    close(quoins["long_leg_mm"], 90.0)
    close(quoins["short_leg_mm"], 65.0)
    close(quoins["mortar_mm"], 3.0)

    entrance = config["entrance"]
    close(entrance["bottom_width_mm"], 604.0)
    close(entrance["top_width_mm"], 600.0)
    close(entrance["height_mm"], 365.0)
    close(entrance["corner_radius_mm"], 87.5)

    windows = config["windows"]
    if windows["centers_x_mm"] != [1047.5, 2733.5]:
        raise ValueError("Window centres have changed")
    close(windows["width_mm"], 90.0)
    close(windows["height_mm"], 294.0)
    close(windows["arch_height_mm"], 86.0)

    floor = config["floor"]
    close(floor["trim_width_mm"], 998.0)
    close(floor["trim_height_mm"], 925.0)
    if floor["dpi"] != 150:
        raise ValueError("Floor must be rendered at 150 dpi")


def validate_asset(config: dict, require: bool) -> None:
    manifest_path = ROOT / config["assets"]["manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    asset_path = ROOT / config["assets"]["wall_base"]
    if not asset_path.exists():
        if require:
            raise FileNotFoundError(
                f"Missing {asset_path}. Run scripts/bootstrap_asset.py first."
            )
        print(f"SKIP: source asset is not installed: {asset_path}")
        return

    actual_hash = sha256(asset_path)
    if actual_hash != manifest["asset_sha256"]:
        raise ValueError(
            f"Source asset checksum mismatch: {actual_hash} != "
            f"{manifest['asset_sha256']}"
        )
    with Image.open(asset_path) as image:
        expected_size = (manifest["width_px"], manifest["height_px"])
        if image.size != expected_size:
            raise ValueError(f"Source image size {image.size} != {expected_size}")
        image.verify()


def validate_generated(directory: Path) -> None:
    missing = sorted(name for name in EXPECTED_GENERATED if not (directory / name).is_file())
    if missing:
        raise FileNotFoundError("Missing generated files: " + ", ".join(missing))

    preview = Image.open(directory / "PREVIEW.jpg")
    if preview.width < 2000 or preview.height < 300:
        raise ValueError(f"Unexpected preview size: {preview.size}")

    wall_raster = directory / "wall_stone_with_window_openings.png"
    if wall_raster.is_file():
        with Image.open(wall_raster) as image:
            expected = (11442, 1801)
            if image.size != expected:
                raise ValueError(f"Wall raster size {image.size} != {expected}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate facade-print reproducibility")
    parser.add_argument("--config", type=Path, default=ROOT / "config.json")
    parser.add_argument("--generated", type=Path)
    parser.add_argument("--require-asset", action="store_true")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    validate_geometry(config)
    validate_asset(config, require=args.require_asset)
    if args.generated is not None:
        validate_generated(args.generated)
    print("OK: facade-print project is internally consistent")


if __name__ == "__main__":
    main()
