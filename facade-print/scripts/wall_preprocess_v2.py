from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter

from common import mm_to_px
from wall_preprocess import (
    _make_dressed_stone,
    _segment_bounds_px,
    remove_source_buttresses,
    save_buttress_removal_diagnostics,
)


def _soft_shadow_mask(size, radius_px, offset_x_px, offset_y_px, opacity):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [0, 0, size[0] - 1, size[1] - 1],
        radius=radius_px,
        fill=opacity,
    )
    blurred = mask.filter(ImageFilter.GaussianBlur(radius=max(1, radius_px)))
    shifted = Image.new("L", size, 0)
    shifted.paste(blurred, (offset_x_px, offset_y_px))
    return shifted


def apply_corner_quoins(wall, cfg):
    """Draw one continuous dressed-stone block across each corner fold.

    The artwork contains no split line, no fold shadow and no texture change at
    the nominal corner coordinate. A small installation error therefore remains
    inside the same uninterrupted stone surface and is not visually exposed.
    """
    settings = cfg["wall"].get("corner_quoins", {})
    if not settings.get("enabled", True):
        return wall

    dpi = cfg["dpi"]
    bounds = _segment_bounds_px(cfg["wall"]["segments_mm"], dpi)
    folds = [
        bounds[index]
        for index in settings.get("boundary_indexes", [1, 2, 3, 4])
    ]

    row_height = max(4, mm_to_px(settings.get("row_height_mm", 34.0), dpi))
    long_leg = max(4, mm_to_px(settings.get("long_leg_mm", 150.0), dpi))
    short_leg = max(4, mm_to_px(settings.get("short_leg_mm", 105.0), dpi))
    mortar = max(1, mm_to_px(settings.get("mortar_mm", 3.0), dpi))
    start_y = max(0, mm_to_px(settings.get("start_y_mm", 0.0), dpi))

    corner_radius = max(
        1, mm_to_px(settings.get("corner_radius_mm", 1.8), dpi)
    )
    shadow_blur = max(
        1, mm_to_px(settings.get("relief_shadow_blur_mm", 2.2), dpi)
    )
    shadow_offset_x = mm_to_px(
        settings.get("relief_shadow_offset_x_mm", 1.2), dpi
    )
    shadow_offset_y = mm_to_px(
        settings.get("relief_shadow_offset_y_mm", 1.8), dpi
    )
    shadow_opacity = int(settings.get("relief_shadow_opacity", 92))

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
            total_width = left_width + right_width
            height = y1 - y
            x0 = fold_x - left_width

            stone = _make_dressed_stone(
                total_width,
                height,
                cfg["random_seed"] + 30000 + corner_index * 503 + row * 17,
                cfg,
            )

            shape_mask = Image.new("L", (total_width, height), 0)
            ImageDraw.Draw(shape_mask).rounded_rectangle(
                [0, 0, total_width - 1, height - 1],
                radius=min(corner_radius, max(1, height // 3)),
                fill=255,
            )

            shadow_margin = shadow_blur * 3 + max(
                abs(shadow_offset_x), abs(shadow_offset_y)
            )
            shadow_size = (
                total_width + shadow_margin * 2,
                height + shadow_margin * 2,
            )
            shadow_shape = Image.new("L", shadow_size, 0)
            shadow_shape.paste(
                shape_mask,
                (
                    shadow_margin + shadow_offset_x,
                    shadow_margin + shadow_offset_y,
                ),
            )
            shadow_shape = shadow_shape.filter(
                ImageFilter.GaussianBlur(radius=shadow_blur)
            )
            shadow_shape = shadow_shape.point(
                lambda value: round(value * shadow_opacity / 255)
            )
            shadow_rgba = Image.new("RGBA", shadow_size, (18, 13, 9, 0))
            shadow_rgba.putalpha(shadow_shape)
            wall.paste(
                shadow_rgba.convert("RGB"),
                (x0 - shadow_margin, y - shadow_margin),
                shadow_rgba.getchannel("A"),
            )

            stone_rgba = stone.convert("RGBA")
            stone_rgba.putalpha(shape_mask)
            wall.paste(
                stone_rgba.convert("RGB"),
                (x0, y),
                stone_rgba.getchannel("A"),
            )

            # No outline and no mark at fold_x. Relief is created only by the
            # soft cast shadow and the stone's own light/dark bevels.
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
