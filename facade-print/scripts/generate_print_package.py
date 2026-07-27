#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
import textwrap
from pathlib import Path

import cairosvg
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

from common import (
    data_uri,
    entrance_geometry,
    entrance_mask,
    image_pdf,
    load_asset,
    load_config,
    mm_to_pt,
    mm_to_px,
    pointed_mask,
    pointed_path,
)
from stained_glass import build_svg
from textures import generate_wood_piece


def _segment_bounds_px(segments_mm, dpi):
    bounds = [0]
    total = 0.0
    for segment in segments_mm:
        total += segment
        bounds.append(mm_to_px(total, dpi))
    return bounds


def _restore_rear_seam_buttress(wall, cfg):
    """Split one complete realistic buttress across the rear-centre overlap seam."""
    dpi = cfg["dpi"]
    w = cfg["wall"]
    bounds = _segment_bounds_px(w["segments_mm"], dpi)
    wrap_end = bounds[-2]
    source_center = mm_to_px(w["rear_seam_buttress_source_center_mm"], dpi)
    half = max(1, mm_to_px(w["rear_seam_buttress_half_width_mm"], dpi))
    patch = wall.crop((source_center - half, 0, source_center + half, wall.height))
    left = patch.crop((0, 0, half, patch.height))
    right = patch.crop((half, 0, patch.width, patch.height))
    feather = min(
        half,
        max(1, mm_to_px(w.get("rear_seam_buttress_feather_mm", 10), dpi)),
    )

    left_alpha = np.full((wall.height, left.width), 255, dtype=np.uint8)
    for x in range(feather):
        left_alpha[:, x] = round(255 * x / max(1, feather - 1))
    wall.paste(left, (wrap_end - left.width, 0), Image.fromarray(left_alpha, "L"))

    right_alpha = np.full((wall.height, right.width), 255, dtype=np.uint8)
    for i in range(feather):
        x = right.width - feather + i
        right_alpha[:, x] = round(255 * (feather - 1 - i) / max(1, feather - 1))
    wall.paste(right, (0, 0), Image.fromarray(right_alpha, "L"))

    overlap = bounds[-1] - bounds[-2]
    if overlap > 0:
        wall.paste(wall.crop((0, 0, overlap, wall.height)), (wrap_end, 0))
    return wall


def _apply_corner_quoins(wall, cfg):
    """Add flat quoin masonry centred exactly on the four physical box corners.

    Each corner is the cumulative boundary between adjacent wall segments. Every
    course crosses the fold line, so after wrapping the film one part of the
    masonry is on each neighbouring wall. Long and short legs alternate by row.
    """
    q = cfg["wall"].get("corner_quoins", {})
    if not q.get("enabled", True):
        return wall

    dpi = cfg["dpi"]
    bounds = _segment_bounds_px(cfg["wall"]["segments_mm"], dpi)
    boundary_indexes = q.get("boundary_indexes", [1, 2, 3, 4])
    fold_positions = [bounds[index] for index in boundary_indexes]

    row_height = max(2, mm_to_px(q.get("row_height_mm", 55.0), dpi))
    long_leg = max(2, mm_to_px(q.get("long_leg_mm", 150.0), dpi))
    short_leg = max(2, mm_to_px(q.get("short_leg_mm", 105.0), dpi))
    mortar = max(1, mm_to_px(q.get("mortar_mm", 3.0), dpi))
    fold_shadow = max(1, mm_to_px(q.get("fold_shadow_mm", 1.5), dpi))
    start_y = max(0, mm_to_px(q.get("start_y_mm", 0.0), dpi))

    source_center = mm_to_px(
        q.get(
            "texture_source_center_mm",
            cfg["wall"]["rear_seam_buttress_source_center_mm"],
        ),
        dpi,
    )
    source_half = max(
        2,
        mm_to_px(
            q.get(
                "texture_source_half_width_mm",
                cfg["wall"]["rear_seam_buttress_half_width_mm"],
            ),
            dpi,
        ),
    )
    source_inner_half = min(
        source_half,
        max(2, mm_to_px(q.get("texture_source_inner_half_width_mm", 34.0), dpi)),
    )
    source = wall.crop(
        (
            source_center - source_inner_half,
            0,
            source_center + source_inner_half,
            wall.height,
        )
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
                    y + rng.randint(-max(1, mortar * 2), max(1, mortar * 2)),
                ),
            )
            strip = source.crop(
                (0, source_y, source.width, source_y + (y1 - y))
            )
            left = strip.resize((left_width, y1 - y), Image.Resampling.LANCZOS)
            right = strip.transpose(Image.Transpose.FLIP_LEFT_RIGHT).resize(
                (right_width, y1 - y), Image.Resampling.LANCZOS
            )

            variation = 0.965 + 0.018 * ((row + corner_index) % 4)
            left = ImageEnhance.Contrast(
                ImageEnhance.Brightness(left).enhance(variation)
            ).enhance(1.05)
            right = ImageEnhance.Contrast(
                ImageEnhance.Brightness(right).enhance(variation * 0.985)
            ).enhance(1.05)

            wall.paste(left, (fold_x - left_width, y))
            wall.paste(right, (fold_x, y))

            draw = ImageDraw.Draw(wall, "RGBA")
            outline = (27, 23, 20, 220)
            highlight = (242, 225, 198, 65)
            outline_width = max(1, mortar // 2)
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
                [
                    fold_x - fold_shadow // 2,
                    y,
                    fold_x + fold_shadow // 2,
                    y1,
                ],
                fill=(14, 12, 11, 92),
            )

            y += row_height
            row += 1

    wrap_end = bounds[-2]
    overlap = bounds[-1] - bounds[-2]
    if overlap > 0:
        wall.paste(wall.crop((0, 0, overlap, wall.height)), (wrap_end, 0))
    return wall


def _save_corner_quoin_diagnostics(wall, cfg, out):
    dpi = cfg["dpi"]
    w = cfg["wall"]
    q = w.get("corner_quoins", {})
    bounds = _segment_bounds_px(w["segments_mm"], dpi)
    boundary_indexes = q.get("boundary_indexes", [1, 2, 3, 4])
    cumulative_mm = []
    running = 0.0
    for segment in w["segments_mm"]:
        running += segment
        cumulative_mm.append(running)

    crop_half_mm = max(
        q.get("long_leg_mm", 150.0), q.get("short_leg_mm", 105.0)
    ) + 35.0
    crops = []
    for number, boundary_index in enumerate(boundary_indexes, 1):
        fold_x = bounds[boundary_index]
        half = mm_to_px(crop_half_mm, dpi)
        crop = wall.crop(
            (
                max(0, fold_x - half),
                0,
                min(wall.width, fold_x + half),
                wall.height,
            )
        )
        draw = ImageDraw.Draw(crop, "RGBA")
        local_fold = min(half, crop.width - 1)
        draw.line(
            [(local_fold, 0), (local_fold, crop.height)],
            fill=(255, 0, 0, 255),
            width=max(2, mm_to_px(0.8, dpi)),
        )
        label = f"corner {number}: {cumulative_mm[boundary_index - 1]:.1f} mm"
        draw.rectangle([8, 8, 360, 42], fill=(255, 255, 255, 220))
        draw.text((16, 14), label, fill=(145, 0, 0, 255))
        crops.append(crop)

    gap = 24
    diagnostics = Image.new(
        "RGB",
        (sum(c.width for c in crops) + gap * (len(crops) - 1), wall.height),
        "white",
    )
    x = 0
    for crop in crops:
        diagnostics.paste(crop, (x, 0))
        x += crop.width + gap
    diagnostics.thumbnail((2400, 850), Image.Resampling.LANCZOS)
    diagnostics.save(
        out / "CORNER_QUOIN_ALIGNMENT_DIAGNOSTICS.jpg",
        quality=96,
        subsampling=0,
    )


def _save_wall_diagnostics(wall, cfg, out):
    dpi = cfg["dpi"]
    w = cfg["wall"]
    win = cfg["windows"]
    crops = []
    for index, cx in enumerate(win["centers_x_mm"], 1):
        left = mm_to_px(cx - 120, dpi)
        right = mm_to_px(cx + 120, dpi)
        top = mm_to_px(60, dpi)
        bottom = mm_to_px(450, dpi)
        crop = wall.crop((left, top, right, bottom))
        crop.save(
            out / f"WINDOW_{index}_ALIGNMENT_DETAIL.jpg",
            quality=96,
            subsampling=0,
        )
        crops.append(crop)

    bounds = _segment_bounds_px(w["segments_mm"], dpi)
    wrap_end = bounds[-2]
    seam_width = mm_to_px(180, dpi)
    seam = Image.new("RGB", (seam_width * 2, wall.height), "white")
    seam.paste(
        wall.crop((wrap_end - seam_width, 0, wrap_end, wall.height)), (0, 0)
    )
    seam.paste(
        wall.crop((0, 0, seam_width, wall.height)), (seam_width, 0)
    )
    seam.save(
        out / "REAR_SEAM_ASSEMBLED_DETAIL.jpg",
        quality=96,
        subsampling=0,
    )

    gap = 30
    preview = Image.new(
        "RGB",
        (
            sum(c.width for c in crops) + seam.width + gap * 2,
            max([c.height for c in crops] + [seam.height]),
        ),
        "white",
    )
    x = 0
    for crop in crops:
        preview.paste(crop, (x, 0))
        x += crop.width + gap
    preview.paste(seam, (x, 0))
    preview.thumbnail((2200, 900), Image.Resampling.LANCZOS)
    preview.save(
        out / "WALL_ALIGNMENT_DIAGNOSTICS.jpg",
        quality=95,
        subsampling=0,
    )
    _save_corner_quoin_diagnostics(wall, cfg, out)


def build_wall(cfg, root, out):
    dpi = cfg["dpi"]
    w = cfg["wall"]
    win = cfg["windows"]
    wall = load_asset(root / cfg["assets"]["wall_base"])
    wall = wall.resize(
        (mm_to_px(w["width_mm"], dpi), mm_to_px(w["height_mm"], dpi)),
        Image.Resampling.LANCZOS,
    )
    wall = _restore_rear_seam_buttress(wall, cfg)
    wall = _apply_corner_quoins(wall, cfg)

    for cx in win["centers_x_mm"]:
        opening = pointed_mask(
            wall.size,
            cx,
            win["top_mm"],
            win["width_mm"],
            win["height_mm"],
            win["arch_height_mm"],
            dpi,
        )
        wall.paste((255, 255, 255), (0, 0), opening)
    wall.paste((255, 255, 255), (0, 0), entrance_mask(wall.size, cfg, dpi))

    _save_wall_diagnostics(wall, cfg, out)
    art = out / "wall_stone_with_window_openings.png"
    wall.save(art, optimize=True, dpi=(dpi, dpi))
    pdf = out / "01_WALLS_STONE_WINDOW_OPENINGS_3875x610mm_100pct.pdf"
    image_pdf(
        art,
        pdf,
        w["width_mm"],
        w["height_mm"],
        "Luba garage wall film",
    )

    entrance_path, _ = entrance_geometry(cfg)
    windows = "\n".join(
        f'<path d="{pointed_path(cx, win["top_mm"], win["width_mm"], win["height_mm"], win["arch_height_mm"])}"/>'
        for cx in win["centers_x_mm"]
    )
    cuts = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w['width_mm']}mm" height="{w['height_mm']}mm" viewBox="0 0 {w['width_mm']} {w['height_mm']}"><g id="ENTRANCE_CUT" fill="none" stroke="#ff00ff" stroke-width=".25"><path d="{entrance_path}"/></g><g id="WINDOW_CUTS" fill="none" stroke="#00a7ff" stroke-width=".25">{windows}</g></svg>'''
    (out / "01B_WALL_CUT_CONTOURS_3875x610mm.svg").write_text(
        cuts, encoding="utf-8"
    )
    cairosvg.svg2pdf(
        bytestring=cuts.encode(),
        write_to=str(out / "01B_WALL_CUT_CONTOURS_3875x610mm.pdf"),
        output_width=mm_to_pt(w["width_mm"]),
        output_height=mm_to_pt(w["height_mm"]),
    )

    guide_positions = []
    x = 0
    for segment in w["segments_mm"][:-1]:
        x += segment
        guide_positions.append(x)
    guides = "".join(
        f'<line x1="{x}" y1="0" x2="{x}" y2="{w["height_mm"]}"/>'
        for x in guide_positions
    )
    hybrid = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w['width_mm']}mm" height="{w['height_mm']}mm" viewBox="0 0 {w['width_mm']} {w['height_mm']}"><g id="ARTWORK"><image width="{w['width_mm']}" height="{w['height_mm']}" preserveAspectRatio="none" xlink:href="data:image/png;base64,{data_uri(art)}"/></g><g id="ENTRANCE_CUT" style="display:none;fill:none;stroke:#ff00ff;stroke-width:.25"><path d="{entrance_path}"/></g><g id="WINDOW_CUTS" style="display:none;fill:none;stroke:#00a7ff;stroke-width:.25">{windows}</g><g id="PANEL_GUIDES" style="display:none;fill:none;stroke:#777;stroke-width:.18;stroke-dasharray:3,2">{guides}<line x1="0" y1="{w['top_fold_mm']}" x2="{w['width_mm']}" y2="{w['top_fold_mm']}"/></g></svg>'''
    (out / "wall_wrap_hybrid_with_cut_layers.svg").write_text(
        hybrid, encoding="utf-8"
    )
    return wall


def _plank_widths(total, minimum, maximum, rng):
    n = max(
        math.ceil(total / maximum),
        min(
            math.floor(total / minimum),
            round(total / ((minimum + maximum) / 2)),
        ),
    )
    base = total / n
    raw = [rng.uniform(-1, 1) for _ in range(n)]
    mean = sum(raw) / n
    raw = [value - mean for value in raw]
    max_abs = max(abs(value) for value in raw) or 1
    amplitude = 0.9 * min(base - minimum, maximum - base)
    return [base + value / max_abs * amplitude for value in raw]


def _floor_breaks(height, minimum, maximum, clearance, previous, rng):
    n_min = math.ceil(height / maximum)
    n_max = math.floor(height / minimum)
    candidates = []
    for _ in range(80):
        count = rng.randint(n_min, n_max)
        remaining = height
        lengths = []
        for index in range(count - 1):
            left = count - index - 1
            low = max(minimum, remaining - maximum * left)
            high = min(maximum, remaining - minimum * left)
            length = rng.uniform(low, high)
            lengths.append(length)
            remaining -= length
        lengths.append(remaining)
        breaks = []
        acc = 0
        for length in lengths[:-1]:
            acc += length
            breaks.append(acc)
        distance = min(
            (abs(a - b) for a in breaks for b in previous),
            default=height,
        )
        candidates.append((distance, breaks))
        if distance >= clearance:
            return breaks
    return max(candidates, key=lambda item: item[0])[1]


def build_floor(cfg, root, out):
    f = cfg["floor"]
    dpi = f.get("dpi", cfg["dpi"])
    rng = random.Random(cfg["random_seed"])
    size = (
        mm_to_px(f["file_width_mm"], dpi),
        mm_to_px(f["file_height_mm"], dpi),
    )
    floor = Image.new("RGB", size, (58, 37, 25))
    draw = ImageDraw.Draw(floor, "RGBA")
    widths = _plank_widths(
        f["trim_width_mm"],
        f["plank_width_min_mm"],
        f["plank_width_max_mm"],
        rng,
    )
    top = f["trim_offset_y_mm"]
    bottom = top + f["trim_height_mm"]
    xmm = f["trim_offset_x_mm"]
    previous = []

    for i, plank_width in enumerate(widths):
        breaks = _floor_breaks(
            f["trim_height_mm"],
            f.get("plank_length_min_mm", 180),
            f.get("plank_length_max_mm", 360),
            f.get("joint_clearance_mm", 45),
            previous,
            rng,
        )
        positions = [0.0] + breaks + [f["trim_height_mm"]]
        x0 = mm_to_px(xmm, dpi)
        x1 = mm_to_px(xmm + plank_width, dpi)
        for j, (a, b) in enumerate(zip(positions, positions[1:])):
            y0 = mm_to_px(top + a, dpi)
            y1 = mm_to_px(top + b, dpi)
            piece = generate_wood_piece(
                max(2, x1 - x0),
                max(2, y1 - y0),
                cfg["random_seed"] + 10000 + i * 101 + j * 17,
                dpi,
            )
            floor.paste(piece, (x0, y0))
            if j > 0:
                draw.line(
                    [(x0 + 1, y0), (x1 - 1, y0)],
                    fill=(27, 18, 13, 235),
                    width=max(1, mm_to_px(0.8, dpi)),
                )
                for nail_x in (
                    x0 + max(2, mm_to_px(2.3, dpi)),
                    x1 - max(2, mm_to_px(2.3, dpi)),
                ):
                    radius = max(1, mm_to_px(0.65, dpi))
                    draw.ellipse(
                        [
                            nail_x - radius,
                            y0 - radius,
                            nail_x + radius,
                            y0 + radius,
                        ],
                        fill=(30, 28, 26, 220),
                    )
        draw.line(
            [(x0, mm_to_px(top, dpi)), (x0, mm_to_px(bottom, dpi))],
            fill=(26, 18, 13, 230),
            width=max(1, mm_to_px(0.75, dpi)),
        )
        previous = breaks
        xmm += plank_width

    art = out / "attic_floor_fine_planks.jpg"
    floor.save(art, quality=95, subsampling=0, dpi=(dpi, dpi))
    image_pdf(
        art,
        out / "03_ATTIC_FLOOR_FINE_PLANKS_1004x931mm_100pct.pdf",
        f["file_width_mm"],
        f["file_height_mm"],
        "Luba garage attic floor",
    )
    hybrid = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{f['file_width_mm']}mm" height="{f['file_height_mm']}mm" viewBox="0 0 {f['file_width_mm']} {f['file_height_mm']}"><image width="{f['file_width_mm']}" height="{f['file_height_mm']}" preserveAspectRatio="none" xlink:href="data:image/jpeg;base64,{data_uri(art)}"/><g id="TRIM_CONTOUR" style="display:none;fill:none;stroke:#ff00ff;stroke-width:.25"><rect x="{f['trim_offset_x_mm']}" y="{f['trim_offset_y_mm']}" width="{f['trim_width_mm']}" height="{f['trim_height_mm']}"/></g></svg>'''
    (out / "attic_floor_fine_planks_hybrid_source.svg").write_text(
        hybrid, encoding="utf-8"
    )
    crop_mm = 250
    crop_px = mm_to_px(crop_mm, dpi)
    centre_x = mm_to_px(
        f["trim_offset_x_mm"] + f["trim_width_mm"] / 2, dpi
    )
    centre_y = mm_to_px(
        f["trim_offset_y_mm"] + f["trim_height_mm"] / 2, dpi
    )
    detail = floor.crop(
        (
            centre_x - crop_px // 2,
            centre_y - crop_px // 2,
            centre_x + crop_px // 2,
            centre_y + crop_px // 2,
        )
    )
    detail.save(
        out / "FLOOR_DETAIL_250x250mm_PREVIEW.jpg",
        quality=95,
        subsampling=0,
        dpi=(dpi, dpi),
    )
    return floor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--output", default="generated")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    root = config_path.parent
    out = (
        (root / args.output).resolve()
        if not Path(args.output).is_absolute()
        else Path(args.output)
    )
    out.mkdir(parents=True, exist_ok=True)
    cfg = load_config(config_path)

    wall = build_wall(cfg, root, out)
    floor = build_floor(cfg, root, out)

    glass = build_svg(cfg)
    (out / "stained_glass_complex_vector_source.svg").write_text(
        glass, encoding="utf-8"
    )
    windows = cfg["windows"]
    cairosvg.svg2pdf(
        bytestring=glass.encode(),
        write_to=str(out / "02_STAINED_GLASS_COMPLEX_TRANSLUCENT_280x330mm.pdf"),
        output_width=mm_to_pt(windows["sheet_width_mm"]),
        output_height=mm_to_pt(windows["sheet_height_mm"]),
    )
    cairosvg.svg2png(
        bytestring=glass.encode(),
        write_to=str(out / "stained_glass_complex_preview.png"),
        output_width=mm_to_px(windows["sheet_width_mm"], cfg["dpi"]),
        output_height=mm_to_px(windows["sheet_height_mm"], cfg["dpi"]),
    )

    note = textwrap.dedent(
        """\
        LUBA 3 AWD GOTHIC GARAGE
        Print files 01, 02 and 03 at exactly 100%; never Fit to page.
        Wall: opaque white exterior PVC + matte UV laminate.
        Stained glass: translucent/backlit film, no opaque white underprint; install from inside.
        Floor: exterior PVC + matte UV laminate suitable for horizontal exposure.
        Use the print shop ICC profile and test color, adhesion and actual LED illumination.
        """
    )
    (out / "README_FOR_PRINT_SHOP_RU_SI.txt").write_text(
        note, encoding="utf-8"
    )

    wall_preview = wall.resize(
        (1800, int(1800 * wall.height / wall.width))
    )
    floor_preview = floor.resize(
        (1200, int(1200 * floor.height / floor.width))
    )
    preview = Image.new(
        "RGB",
        (1880, wall_preview.height + floor_preview.height + 110),
        "white",
    )
    preview.paste(wall_preview, (40, 35))
    preview.paste(floor_preview, (40, 70 + wall_preview.height))
    preview.save(out / "PREVIEW.jpg", quality=92)


if __name__ == "__main__":
    main()
