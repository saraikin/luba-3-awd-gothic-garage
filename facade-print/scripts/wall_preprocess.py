from __future__ import annotations

import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageStat

from common import mm_to_px


def _segment_bounds_px(segments_mm, dpi):
    bounds = [0]
    total = 0.0
    for segment in segments_mm:
        total += segment
        bounds.append(mm_to_px(total, dpi))
    return bounds


def remove_source_buttresses(wall, cfg):
    """Replace all projecting buttresses in the realistic raster with plain masonry."""
    settings = cfg["wall"].get("buttress_removal", {})
    if not settings.get("enabled", True):
        return wall

    dpi = cfg["dpi"]
    feather = max(1, mm_to_px(settings.get("feather_mm", 18.0), dpi))
    original = wall.copy()

    for zone in settings.get("zones", []):
        x0 = mm_to_px(zone["start_mm"], dpi)
        x1 = mm_to_px(zone["end_mm"], dpi)
        width = x1 - x0
        if width <= 0:
            raise ValueError(f"Invalid buttress-removal zone: {zone}")

        source_center = mm_to_px(zone["source_center_mm"], dpi)
        sx0 = source_center - width // 2
        sx1 = sx0 + width
        if sx0 < 0 or sx1 > original.width:
            raise ValueError(f"Buttress-removal source is outside wall raster: {zone}")

        replacement = original.crop((sx0, 0, sx1, original.height))
        if zone.get("flip", False):
            replacement = replacement.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

        side = max(feather, mm_to_px(25.0, dpi))
        context_parts = []
        if x0 - side >= 0:
            context_parts.append(original.crop((x0 - side, 0, x0, original.height)))
        if x1 + side <= original.width:
            context_parts.append(original.crop((x1, 0, x1 + side, original.height)))
        if context_parts:
            target_mean = sum(
                ImageStat.Stat(part.convert("L")).mean[0] for part in context_parts
            ) / len(context_parts)
            source_mean = max(1.0, ImageStat.Stat(replacement.convert("L")).mean[0])
            brightness = max(0.86, min(1.16, target_mean / source_mean))
            replacement = ImageEnhance.Brightness(replacement).enhance(brightness)

        mask_array = np.full((wall.height, width), 255, dtype=np.uint8)
        edge = min(feather, max(1, width // 3))
        for x in range(edge):
            alpha = round(255 * (x + 1) / (edge + 1))
            mask_array[:, x] = alpha
            mask_array[:, width - 1 - x] = alpha
        wall.paste(replacement, (x0, 0), Image.fromarray(mask_array, "L"))

    return wall


def apply_corner_quoins(wall, cfg):
    """Add prominent flat quoin masonry centred exactly on the four folds."""
    q = cfg["wall"].get("corner_quoins", {})
    if not q.get("enabled", True):
        return wall

    dpi = cfg["dpi"]
    bounds = _segment_bounds_px(cfg["wall"]["segments_mm"], dpi)
    boundary_indexes = q.get("boundary_indexes", [1, 2, 3, 4])
    fold_positions = [bounds[index] for index in boundary_indexes]

    row_height = max(2, mm_to_px(q.get("row_height_mm", 62.0), dpi))
    long_leg = max(2, mm_to_px(q.get("long_leg_mm", 185.0), dpi))
    short_leg = max(2, mm_to_px(q.get("short_leg_mm", 135.0), dpi))
    mortar = max(1, mm_to_px(q.get("mortar_mm", 4.0), dpi))
    fold_shadow = max(1, mm_to_px(q.get("fold_shadow_mm", 2.5), dpi))
    start_y = max(0, mm_to_px(q.get("start_y_mm", 0.0), dpi))

    source_center = mm_to_px(q.get("texture_source_center_mm", 820.0), dpi)
    source_half = max(2, mm_to_px(q.get("texture_source_half_width_mm", 130.0), dpi))
    source = wall.crop(
        (source_center - source_half, 0, source_center + source_half, wall.height)
    )

    rng = random.Random(cfg["random_seed"] + 417)
    for corner_index, fold_x in enumerate(fold_positions):
        y = start_y
        row = 0
        while y < wall.height:
            y1 = min(wall.height, y + row_height - mortar)
            if y1 <= y:
                break

            left_width, right_width = (
                (long_leg, short_leg) if row % 2 == 0 else (short_leg, long_leg)
            )
            source_y = max(
                0,
                min(
                    source.height - (y1 - y),
                    y + rng.randint(-max(1, mortar), max(1, mortar)),
                ),
            )
            strip = source.crop((0, source_y, source.width, source_y + (y1 - y)))
            if strip.width < max(left_width, right_width):
                raise ValueError("corner_quoins texture source is narrower than a quoin leg")

            left_x = rng.randint(0, strip.width - left_width)
            right_x = rng.randint(0, strip.width - right_width)
            left = strip.crop((left_x, 0, left_x + left_width, y1 - y))
            right = strip.crop((right_x, 0, right_x + right_width, y1 - y))
            if (row + corner_index) % 2:
                right = right.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

            variation = 1.075 + 0.022 * ((row + corner_index) % 4)
            left = ImageEnhance.Contrast(
                ImageEnhance.Brightness(left).enhance(variation)
            ).enhance(1.16)
            right = ImageEnhance.Contrast(
                ImageEnhance.Brightness(right).enhance(variation * 0.985)
            ).enhance(1.16)

            wall.paste(left, (fold_x - left_width, y))
            wall.paste(right, (fold_x, y))

            draw = ImageDraw.Draw(wall, "RGBA")
            outline = (24, 20, 17, 242)
            highlight = (250, 233, 205, 105)
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
            draw.line(
                [(fold_x - left_width + 2, y + 2), (fold_x - 3, y + 2)],
                fill=highlight,
                width=1,
            )
            draw.line(
                [(fold_x + 3, y + 2), (fold_x + right_width - 2, y + 2)],
                fill=highlight,
                width=1,
            )
            draw.rectangle(
                [fold_x - fold_shadow // 2, y, fold_x + fold_shadow // 2, y1],
                fill=(12, 10, 9, 125),
            )

            y += row_height
            row += 1

    wrap_end = bounds[-2]
    overlap = bounds[-1] - bounds[-2]
    if overlap > 0:
        wall.paste(wall.crop((0, 0, overlap, wall.height)), (wrap_end, 0))
    return wall


def save_buttress_removal_diagnostics(wall, cfg, out):
    settings = cfg["wall"].get("buttress_removal", {})
    zones = settings.get("zones", [])
    if not settings.get("enabled", True) or not zones:
        return

    dpi = cfg["dpi"]
    pad = mm_to_px(35.0, dpi)
    crops = []
    for index, zone in enumerate(zones, 1):
        x0 = mm_to_px(zone["start_mm"], dpi)
        x1 = mm_to_px(zone["end_mm"], dpi)
        left = max(0, x0 - pad)
        right = min(wall.width, x1 + pad)
        crop = wall.crop((left, 0, right, wall.height))
        draw = ImageDraw.Draw(crop, "RGBA")
        local_x0 = x0 - left
        local_x1 = x1 - left
        line_width = max(2, mm_to_px(0.7, dpi))
        draw.line(
            [(local_x0, 0), (local_x0, crop.height)],
            fill=(0, 170, 255, 220),
            width=line_width,
        )
        draw.line(
            [(local_x1, 0), (local_x1, crop.height)],
            fill=(0, 170, 255, 220),
            width=line_width,
        )
        label = (
            f"removed buttress {index}: "
            f"{zone['start_mm']:.0f}-{zone['end_mm']:.0f} mm"
        )
        draw.rectangle([8, 8, 430, 42], fill=(255, 255, 255, 220))
        draw.text((16, 14), label, fill=(0, 75, 120, 255))
        crops.append(crop)

    gap = 20
    columns = 4
    rows = math.ceil(len(crops) / columns)
    cell_width = max(crop.width for crop in crops)
    cell_height = max(crop.height for crop in crops)
    diagnostics = Image.new(
        "RGB",
        (
            cell_width * columns + gap * (columns - 1),
            cell_height * rows + gap * (rows - 1),
        ),
        "white",
    )
    for index, crop in enumerate(crops):
        x = (index % columns) * (cell_width + gap)
        y = (index // columns) * (cell_height + gap)
        diagnostics.paste(crop, (x, y))
    diagnostics.thumbnail((2400, 1500), Image.Resampling.LANCZOS)
    diagnostics.save(
        out / "BUTTRESS_REMOVAL_DIAGNOSTICS.jpg",
        quality=96,
        subsampling=0,
    )
