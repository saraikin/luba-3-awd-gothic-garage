#!/usr/bin/env python3
from __future__ import annotations

import generate_print_package as generator
from wall_preprocess import (
    apply_corner_quoins,
    remove_source_buttresses,
    save_buttress_removal_diagnostics,
)


_original_wall_diagnostics = generator._save_wall_diagnostics


def _save_wall_diagnostics(wall, cfg, out):
    _original_wall_diagnostics(wall, cfg, out)
    save_buttress_removal_diagnostics(wall, cfg, out)


# The existing generator keeps the stable PDF/SVG/floor pipeline. These three
# wall-specific hooks replace the old rear-seam buttress and corner treatment.
generator._restore_rear_seam_buttress = remove_source_buttresses
generator._apply_corner_quoins = apply_corner_quoins
generator._save_wall_diagnostics = _save_wall_diagnostics


if __name__ == "__main__":
    generator.main()
