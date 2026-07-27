#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "assets" / "source_asset.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "asset_file",
        "archive_sha256",
        "asset_sha256",
        "width_px",
        "height_px",
    }
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"Manifest is missing fields: {', '.join(missing)}")
    return data


def validate_image(path: Path, manifest: dict) -> None:
    actual_hash = sha256(path)
    if actual_hash != manifest["asset_sha256"]:
        raise ValueError(
            f"Asset SHA-256 mismatch: expected {manifest['asset_sha256']}, "
            f"received {actual_hash}"
        )
    with Image.open(path) as image:
        expected = (manifest["width_px"], manifest["height_px"])
        if image.size != expected:
            raise ValueError(
                f"Asset dimensions mismatch: expected {expected}, received {image.size}"
            )
        image.verify()


def install_from_archive(archive: Path, manifest: dict, destination: Path) -> None:
    if not archive.is_file():
        raise FileNotFoundError(archive)
    actual_archive_hash = sha256(archive)
    if actual_archive_hash != manifest["archive_sha256"]:
        raise ValueError(
            f"Archive SHA-256 mismatch: expected {manifest['archive_sha256']}, "
            f"received {actual_archive_hash}"
        )

    with tempfile.TemporaryDirectory(prefix="luba-facade-asset-") as temp_dir:
        temp = Path(temp_dir)
        with zipfile.ZipFile(archive) as package:
            members = {Path(name).name: name for name in package.namelist()}
            wanted = manifest["asset_file"]
            if wanted not in members:
                raise ValueError(f"Archive does not contain {wanted}")
            package.extract(members[wanted], temp)
            extracted = temp / members[wanted]
            validate_image(extracted, manifest)
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary_destination = destination.with_suffix(destination.suffix + ".tmp")
            shutil.copyfile(extracted, temporary_destination)
            os.replace(temporary_destination, destination)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install and verify the archived realistic wall source."
    )
    parser.add_argument(
        "--archive",
        type=Path,
        default=os.environ.get("LUBA_FACADE_ASSET_ARCHIVE"),
        help="Path to luba_facade_source_asset_q85.zip. Can also be set via "
        "LUBA_FACADE_ASSET_ARCHIVE.",
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    destination = ROOT / "assets" / manifest["asset_file"]

    if args.verify_only:
        validate_image(destination, manifest)
        print(f"OK: {destination}")
        return

    if args.archive is None:
        raise SystemExit(
            "Source archive is required. Download the Drive file recorded in "
            "assets/source_asset.json and pass --archive PATH."
        )
    install_from_archive(Path(args.archive), manifest, destination)
    print(f"Installed and verified: {destination}")


if __name__ == "__main__":
    main()
