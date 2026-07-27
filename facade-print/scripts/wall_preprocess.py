from __future__ import annotations

import math
import random

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from common import entrance_mask, mm_to_px, pointed_mask


def _segment_bounds_px(segments_mm, dpi):
    bounds = [0]
    total = 0.0
    for segment in segments_mm:
        total += segment
        bounds.append(mm_to_px(total, dpi))
    return bounds


def _cosine_ramp(length: int) -> np.ndarray:
    if length <= 0:
        return np.empty((0,), dtype=np.float32)
    t = np.linspace(0.0, 1.0, length, dtype=np.float32)
    return 0.5 - 0.5 * np.cos(np.pi * t)


def _compose_clean_masonry(original, width, cfg, rng):
    """Build shadow-free masonry from clean full-height source strips."""
    dpi = cfg["dpi"]
    settings = cfg["wall"]["buttress_removal"]
    intervals = settings["clean_source_intervals_mm"]
    overlap = max(1, mm_to_px(settings.get("tile_overlap_mm", 18.0), dpi))
    min_tile = max(overlap + 2, mm_to_px(settings.get("tile_min_width_mm", 72.0), dpi))
    max_tile = max(min_tile, mm_to_px(settings.get("tile_max_width_mm", 118.0), dpi))

    canvas = Image.new("RGB", (width, original.height))
    filled = 0
    tile_index = 0
    while filled < width:
        interval = intervals[(tile_index + rng.randrange(len(intervals))) % len(intervals)]
        ia = mm_to_px(interval[0], dpi)
        ib = mm_to_px(interval[1], dpi)
        available = ib - ia
        if available <= overlap + 2:
            raise ValueError(f"Clean source interval is too narrow: {interval}")

        remaining = width - filled
        tile_width = min(
            remaining + (overlap if filled else 0),
            rng.randint(min_tile, max_tile),
            available,
        )
        sx0 = ia + rng.randint(0, max(0, available - tile_width))
        tile = original.crop((sx0, 0, sx0 + tile_width, original.height))
        if rng.random() < 0.45:
            tile = tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        tile = ImageEnhance.Brightness(tile).enhance(rng.uniform(0.96, 1.06))
        tile = ImageEnhance.Contrast(tile).enhance(rng.uniform(0.97, 1.07))

        dest_x = max(0, filled - (overlap if filled else 0))
        if filled == 0:
            canvas.paste(tile, (0, 0))
            filled = tile_width
        else:
            overlap_actual = min(overlap, tile_width, filled)
            alpha = np.full((original.height, tile_width), 255, dtype=np.uint8)
            alpha[:, :overlap_actual] = (
                _cosine_ramp(overlap_actual) * 255
            ).astype(np.uint8)[None, :]
            canvas.paste(tile, (dest_x, 0), Image.fromarray(alpha, "L"))
            filled = min(width, dest_x + tile_width)
        tile_index += 1
    return canvas.crop((0, 0, width, original.height))


def _frame_masks(size, cfg):
    dpi = cfg["dpi"]
    settings = cfg["wall"]["buttress_removal"]
    preserve = Image.new("L", size, 0)

    windows = cfg["windows"]
    border = mm_to_px(settings.get("window_frame_preserve_mm", 27.0), dpi)
    for cx in windows["centers_x_mm"]:
        opening = pointed_mask(
            size,
            cx,
            windows["top_mm"],
            windows["width_mm"],
            windows["height_mm"],
            windows["arch_height_mm"],
            dpi,
        )
        kernel = max(3, border * 2 + 1)
        opening_array = np.asarray(opening, dtype=np.uint8)
        outer = cv2.dilate(
            opening_array,
            np.ones((kernel, kernel), np.uint8),
            iterations=1,
        )
        ring = np.maximum(
            0, outer.astype(np.int16) - opening_array.astype(np.int16)
        ).astype(np.uint8)
        preserve = Image.fromarray(
            np.maximum(np.asarray(preserve), ring), "L"
        )

    entry = entrance_mask(size, cfg, dpi)
    border = mm_to_px(settings.get("entrance_frame_preserve_mm", 48.0), dpi)
    kernel = max(3, border * 2 + 1)
    entry_array = np.asarray(entry, dtype=np.uint8)
    outer = cv2.dilate(
        entry_array,
        np.ones((kernel, kernel), np.uint8),
        iterations=1,
    )
    ring = np.maximum(
        0, outer.astype(np.int16) - entry_array.astype(np.int16)
    ).astype(np.uint8)
    return Image.fromarray(np.maximum(np.asarray(preserve), ring), "L")


def remove_source_buttresses(wall, cfg):
    """Remove projecting buttresses and their broad cast shadows."""
    settings = cfg["wall"].get("buttress_removal", {})
    if not settings.get("enabled", True):
        return wall

    dpi = cfg["dpi"]
    original = wall.copy()
    frame_mask = _frame_masks(wall.size, cfg)
    feather = max(1, mm_to_px(settings.get("feather_mm", 28.0), dpi))
    rng = random.Random(cfg["random_seed"] + 901)

    for start_mm, end_mm in settings.get("cleanup_zones", []):
        x0 = max(0, mm_to_px(start_mm, dpi))
        x1 = min(wall.width, mm_to_px(end_mm, dpi))
        width = x1 - x0
        if width <= 0:
            continue
        replacement = _compose_clean_masonry(original, width, cfg, rng)
        mask = np.full((wall.height, width), 255, dtype=np.uint8)
        edge = min(feather, max(1, width // 3))
        ramp = (_cosine_ramp(edge) * 255).astype(np.uint8)
        mask[:, :edge] = ramp[None, :]
        mask[:, -edge:] = ramp[::-1][None, :]
        wall.paste(replacement, (x0, 0), Image.fromarray(mask, "L"))

    # Restore the original decorative window and entrance surrounds.
    wall.paste(original, (0, 0), frame_mask)

    # Remove any residual low-frequency shadow while preserving bottom moss.
    array = np.asarray(wall).astype(np.float32)
    for start_mm, end_mm in settings.get("cleanup_zones", []):
        x0 = max(0, mm_to_px(start_mm, dpi))
        x1 = min(wall.width, mm_to_px(end_mm, dpi))
        if x1 <= x0:
            continue
        band = array[:, x0:x1, :]
        luminance = (
            0.2126 * band[:, :, 0]
            + 0.7152 * band[:, :, 1]
            + 0.0722 * band[:, :, 2]
        )
        sigma = max(6.0, float(mm_to_px(18.0, dpi)))
        low = cv2.GaussianBlur(
            luminance.astype(np.float32),
            (0, 0),
            sigmaX=sigma,
            sigmaY=sigma,
        )
        side = mm_to_px(35.0, dpi)
        contexts = [
            context
            for context in (
                array[:, max(0, x0 - side):x0, :],
                array[:, x1:min(wall.width, x1 + side), :],
            )
            if context.shape[1] > 0
        ]
        if not contexts:
            continue
        target = np.mean(
            [
                np.mean(
                    0.2126 * context[:, :, 0]
                    + 0.7152 * context[:, :, 1]
                    + 0.0722 * context[:, :, 2],
                    axis=1,
                )
                for context in contexts
            ],
            axis=0,
        )
        target = cv2.GaussianBlur(
            target.astype(np.float32).reshape(-1, 1),
            (0, 0),
            sigmaX=0.0,
            sigmaY=max(3.0, float(mm_to_px(10.0, dpi))),
        ).reshape(-1)
        gain = np.clip(target[:, None] / np.maximum(low, 20.0), 0.82, 1.45)
        taper = np.ones((wall.height, 1), dtype=np.float32)
        bottom = mm_to_px(90.0, dpi)
        if bottom > 0:
            taper[-bottom:, 0] = np.linspace(1.0, 0.35, bottom)
        gain = 1.0 + (gain - 1.0) * taper
        array[:, x0:x1, :] = np.clip(band * gain[:, :, None], 0, 255)

    wall = Image.fromarray(array.astype(np.uint8), "RGB")
    wall.paste(original, (0, 0), frame_mask)
    return wall


def _make_dressed_stone(width, height, seed, cfg):
    """Generate rough dressed limestone, separate from field-wall masonry."""
    settings = cfg["wall"]["corner_quoins"]
    rng = np.random.default_rng(seed)
    base = np.array(
        settings.get("material_base_rgb", [136, 121, 98]),
        dtype=np.float32,
    )

    coarse_seed = rng.normal(0.0, 1.0, (height, width)).astype(np.float32)
    medium_seed = rng.normal(0.0, 1.0, (height, width)).astype(np.float32)
    coarse = cv2.GaussianBlur(
        coarse_seed,
        (0, 0),
        sigmaX=max(5.0, min(width, height) / 3.2),
    )
    medium = cv2.GaussianBlur(
        medium_seed,
        (0, 0),
        sigmaX=max(1.2, min(width, height) / 22.0),
    )
    coarse /= max(1e-6, float(coarse.std()))
    medium /= max(1e-6, float(medium.std()))
    fine = rng.normal(0.0, 1.0, (height, width)).astype(np.float32)

    array = (
        base[None, None, :]
        + coarse[:, :, None] * 13.0
        + medium[:, :, None] * 9.0
        + fine[:, :, None] * 5.0
    )
    array[:, :, 0] += medium * 1.1
    array[:, :, 1] += coarse * 0.7
    array[:, :, 2] -= medium * 0.5
    array += (
        rng.normal(0, 1, 3).astype(np.float32)
        * np.array([2.2, 1.8, 1.4], dtype=np.float32)
    )[None, None, :]
    stone = Image.fromarray(np.clip(array, 28, 225).astype(np.uint8), "RGB")
    stone = ImageEnhance.Contrast(stone).enhance(
        settings.get("material_contrast", 1.32)
    )

    draw = ImageDraw.Draw(stone, "RGBA")
    for _ in range(max(30, width * height // 3500)):
        x = int(rng.integers(4, max(5, width - 4)))
        y = int(rng.integers(4, max(5, height - 4)))
        rx = int(rng.integers(1, max(2, width // 90 + 1)))
        ry = int(rng.integers(1, max(2, height // 35 + 1)))
        color = (
            (38, 32, 27, int(rng.integers(18, 58)))
            if rng.random() < 0.72
            else (235, 220, 191, int(rng.integers(12, 38)))
        )
        draw.ellipse([x - rx, y - ry, x + rx, y + ry], fill=color)

    for _ in range(max(12, width // 28)):
        x = int(rng.integers(8, max(9, width - 8)))
        y = int(rng.integers(8, max(9, height - 8)))
        length = int(rng.integers(max(4, width // 60), max(6, width // 24)))
        angle = rng.uniform(-0.35, 0.35)
        x2 = int(x + length * math.cos(angle))
        y2 = int(y + length * math.sin(angle))
        draw.line(
            [(x, y), (x2, y2)],
            fill=(48, 41, 34, int(rng.integers(22, 52))),
            width=max(1, height // 70),
        )
        draw.line(
            [(x, y - 1), (x2, y2 - 1)],
            fill=(235, 219, 187, int(rng.integers(10, 28))),
            width=1,
        )

    if width > 120 and rng.random() < 0.35:
        x = int(rng.integers(width // 4, 3 * width // 4))
        points = [(x, int(height * 0.12))]
        for step in range(1, 5):
            x += int(
                rng.integers(
                    -max(2, width // 45),
                    max(3, width // 45 + 1),
                )
            )
            points.append((x, int(height * (0.12 + step * 0.15))))
        draw.line(
            points,
            fill=(48, 40, 33, 72),
            width=max(1, height // 55),
        )

    bevel = max(4, min(width, height) // 13)
    for index in range(bevel):
        fade = 1.0 - index / bevel
        highlight = int(82 * fade)
        shadow = int(95 * fade)
        draw.line(
            [(index, index), (width - 1 - index, index)],
            fill=(255, 241, 211, highlight),
        )
        draw.line(
            [(index, index), (index, height - 1 - index)],
            fill=(255, 241, 211, highlight // 2),
        )
        draw.line(
            [
                (index, height - 1 - index),
                (width - 1 - index, height - 1 - index),
            ],
            fill=(22, 18, 15, shadow),
        )
        draw.line(
            [
                (width - 1 - index, index),
                (width - 1 - index, height - 1 - index),
            ],
            fill=(22, 18, 15, shadow),
        )
    return ImageEnhance.Sharpness(stone).enhance(1.15)


def apply_corner_quoins(wall, cfg):
    """Draw large dressed-stone corner blocks on the exact fold positions."""
    settings = cfg["wall"].get("corner_quoins", {})
    if not settings.get("enabled", True):
        return wall
    dpi = cfg["dpi"]
    bounds = _segment_bounds_px(cfg["wall"]["segments_mm"], dpi)
    folds = [
        bounds[index]
        for index in settings.get("boundary_indexes", [1, 2, 3, 4])
    ]
    row_height = max(4, mm_to_px(settings.get("row_height_mm", 68.0), dpi))
    long_leg = max(4, mm_to_px(settings.get("long_leg_mm", 205.0), dpi))
    short_leg = max(4, mm_to_px(settings.get("short_leg_mm", 150.0), dpi))
    mortar = max(2, mm_to_px(settings.get("mortar_mm", 5.0), dpi))
    fold_shadow = max(1, mm_to_px(settings.get("fold_shadow_mm", 2.0), dpi))
    start_y = max(0, mm_to_px(settings.get("start_y_mm", 0.0), dpi))

    for corner_index, fold_x in enumerate(folds):
        y = start_y
        row = 0
        while y < wall.height:
            y1 = min(wall.height, y + row_height - mortar)
            if y1 <= y:
                break
            left_width, right_width = (
                (long_leg, short_leg)
                if row % 2 == 0
                else (short_leg, long_leg)
            )
            left = _make_dressed_stone(
                left_width,
                y1 - y,
                cfg["random_seed"] + 10000 + corner_index * 503 + row * 17,
                cfg,
            )
            right = _make_dressed_stone(
                right_width,
                y1 - y,
                cfg["random_seed"] + 20000 + corner_index * 503 + row * 17,
                cfg,
            )
            wall.paste(left, (fold_x - left_width, y))
            wall.paste(right, (fold_x, y))
            draw = ImageDraw.Draw(wall, "RGBA")
            outline = tuple(settings.get("outline_rgba", [38, 29, 21, 245]))
            outline_width = max(2, mortar // 2)
            draw.rectangle(
                [fold_x - left_width, y, fold_x - 1, y1],
                outline=outline,
                width=outline_width,
            )
            draw.rectangle(
                [fold_x, y, fold_x + right_width, y1],
                outline=outline,
                width=outline_width,
            )
            draw.rectangle(
                [
                    fold_x - fold_shadow // 2,
                    y,
                    fold_x + fold_shadow // 2,
                    y1,
                ],
                fill=(12, 9, 7, 95),
            )
            y += row_height
            row += 1

    wrap_end = bounds[-2]
    overlap = bounds[-1] - bounds[-2]
    if overlap > 0:
        wall.paste(
            wall.crop((0, 0, overlap, wall.height)),
            (wrap_end, 0),
        )
    return wall


def save_buttress_removal_diagnostics(wall, cfg, out):
    """Export checks for shadow removal and the separate quoin material."""
    dpi = cfg["dpi"]
    zones = cfg["wall"].get("buttress_removal", {}).get("cleanup_zones", [])
    if not zones:
        return

    pad = mm_to_px(28.0, dpi)
    crops = []
    for index, (start_mm, end_mm) in enumerate(zones, 1):
        x0 = max(0, mm_to_px(start_mm, dpi))
        x1 = min(wall.width, mm_to_px(end_mm, dpi))
        left = max(0, x0 - pad)
        right = min(wall.width, x1 + pad)
        crop = wall.crop((left, 0, right, wall.height))
        draw = ImageDraw.Draw(crop, "RGBA")
        width = max(2, mm_to_px(0.7, dpi))
        draw.line(
            [(x0 - left, 0), (x0 - left, crop.height)],
            fill=(0, 170, 255, 230),
            width=width,
        )
        draw.line(
            [(x1 - left, 0), (x1 - left, crop.height)],
            fill=(0, 170, 255, 230),
            width=width,
        )
        draw.rectangle([8, 8, 470, 42], fill=(255, 255, 255, 225))
        draw.text(
            (16, 14),
            f"shadow cleanup {index}: {start_mm:.0f}-{end_mm:.0f} mm",
            fill=(0, 75, 120, 255),
        )
        crops.append(crop)

    gap = 20
    columns = 2
    rows = math.ceil(len(crops) / columns)
    cell_width = max(crop.width for crop in crops)
    cell_height = max(crop.height for crop in crops)
    montage = Image.new(
        "RGB",
        (
            cell_width * columns + gap * (columns - 1),
            cell_height * rows + gap * (rows - 1),
        ),
        "white",
    )
    for index, crop in enumerate(crops):
        montage.paste(
            crop,
            (
                (index % columns) * (cell_width + gap),
                (index // columns) * (cell_height + gap),
            ),
        )
    montage.thumbnail((2600, 1700), Image.Resampling.LANCZOS)
    montage.save(
        out / "BUTTRESS_AND_SHADOW_REMOVAL_DIAGNOSTICS.jpg",
        quality=96,
        subsampling=0,
    )

    preview = wall.copy()
    preview.thumbnail((2800, 700), Image.Resampling.LANCZOS)
    preview.save(
        out / "WALL_SHADOW_FREE_PROMINENT_QUOINS_PREVIEW.jpg",
        quality=96,
        subsampling=0,
    )

    bounds = _segment_bounds_px(cfg["wall"]["segments_mm"], dpi)
    wall.crop((bounds[2], 0, bounds[3], wall.height)).save(
        out / "FRONT_QUOIN_NEW_TEXTURE_DETAIL.jpg",
        quality=96,
        subsampling=0,
    )
