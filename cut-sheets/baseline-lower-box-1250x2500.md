# Current lower box cut sheet — 1250 × 2500 mm sheet

## Decision

Use one standard plywood sheet **1250 × 2500 mm** for the **lower functional box only**.

The current lower-box baseline is fixed at:

- **Length:** 1000 mm
- **Width:** 900 mm
- **Wall / robot-bay height:** 560 mm

The hinged gable roof and wide tower are separate upper architectural modules and must be cut and framed separately.

## Measured minimum envelope

Measured charging-station / robot minimum envelope:

| Dimension | Minimum clear size |
|---|---:|
| Length | 850 mm |
| Width | 650 mm |
| Height | 450 mm |

## Current lower box size

Assumptions:

- **12 mm exterior plywood**
- no plywood floor
- robot stands on concrete slabs or prepared ground
- rear wall fits between the two side walls

| Dimension | Current external size | Approx. clear internal size |
|---|---:|---:|
| Length | 1000 mm | ~976 mm |
| Width | 900 mm | ~876 mm |
| Wall / bay height | 560 mm | ~560 mm |

Clearance over the measured minimum:

| Dimension | Minimum | Approx. clear internal | Clearance |
|---|---:|---:|---:|
| Length | 850 mm | ~976 mm | +126 mm |
| Width | 650 mm | ~876 mm | +226 mm |
| Height | 450 mm | ~560 mm | +110 mm |

## Assembly issue discovered

The first assembly attempt exposed a dimensional error in the planning method:

- Panel dimensions had been treated as external dimensions without consistently accounting for plywood thickness at square butt joints.
- With **12 mm plywood**, two overlapping side sheets add **24 mm**.
- As a result, a panel cut to the full nominal external width is 24 mm too wide or causes the assembled box to become 24 mm wider, depending on which panel overlaps.
- A 45° mitred joint would preserve the external dimension, but the current construction method uses straight joints fixed to timber battens.

### Required correction rule

For every square joint, define the overlap before cutting:

- Panel fitting **between two 12 mm side panels**: subtract **24 mm** from the external dimension.
- Panel fitting behind or inside **one 12 mm panel**: subtract **12 mm**.
- Panel covering the outside edges of adjacent panels: keep the full external dimension.

The actual plywood thickness must be measured with calipers before final production cutting. Nominal 12 mm plywood may differ slightly from its real thickness.

## Aesthetic rationale

The visible front lower-box proportion is close to the golden ratio:

- External width: **900 mm**
- Wall height: **560 mm**
- Ratio: **900 / 560 = 1.607**
- Golden ratio: **1.618**

The deviation is approximately 0.7%, giving the lower module a balanced church-like facade while preserving useful working height.

## Current upper-module proportions

- Lower wall height: **560 mm**
- Gable rise above wall: **280–300 mm**
- Height to roof ridge: **840–860 mm**
- Roof footprint: approximately **1040 × 940 mm** with about 20 mm overhang on each side
- Wide tower width: **480–520 mm**
- Wide tower depth: **450–500 mm**
- Visible tower height above roof: approximately **450–500 mm**
- Approximate total structure height: **1290–1360 mm**

The wide tower is centered over both roof slopes and must transfer its load into internal roof framing or a structural tower base, not into roof cladding alone.

## Panel list — lower functional box

All dimensions are in millimetres.

| Part | Qty | Nominal size | Notes |
|---|---:|---:|---|
| Side wall | 2 | 1000 × 560 | Full-length left and right walls. |
| Rear wall | 1 | 876 × 560 | Fits between 12 mm side walls. Confirm actual plywood thickness before cutting. |
| Top ceiling / service shelf | 1 | 1000 × 900 | Supports the removable/hinged upper roof module through structural framing. |
| Front upper lintel | 1 | 900 × 100 | Provisional; final height depends on gate design and overlap rule. |
| Front side jamb | 2 | 560 × 70 | Optional/provisional; may be replaced by external timber battens. |
| Hinge, corner and roof-stop reinforcement | as needed | from offcuts | Size after hinge and tower-support details are fixed. |

With two 70 mm jambs, the nominal front opening is approximately:

- Width: **760 mm**
- Height below a 100 mm lintel: **460 mm**

This provides more clearance than the measured minimum envelope, but the opening must still be tested against the actual charging trajectory before production.

## Current purchase list

- Staples compatible with the available staple gun.
- Nails compatible with the available nailer.
- Exterior wood glue: preferably **D4**, or **D3** for protected joints.
- Approximately **4–5 timber mounting battens**, each about **30 × 45 mm** in section.

Confirm staple and nail dimensions after checking the tool models, plywood thickness and batten orientation.

## One-sheet layout

Sheet orientation: **2500 mm length × 1250 mm width**.

The following arrangement fits the principal lower-box panels on one sheet before allowing for saw kerf and trimming:

```text
SHEET 2500 × 1250 mm

Zone A — length 0–900 mm:
- Top ceiling / service shelf rotated: 900 × 1000 mm
- Remaining strip: 900 × 250 mm

Zone B — length 900–1900 mm:
- Side wall: 1000 × 560 mm
- Side wall: 1000 × 560 mm
- Remaining strip: 1000 × 130 mm

Zone C — length 1900–2460 mm:
- Rear wall rotated: 560 × 876 mm
- Remaining area below it: approximately 560 × 374 mm

Zone D — length 2460–2500 mm:
- Narrow residual strip: 40 × 1250 mm
```

Use the remaining **900 × 250 mm** and **560 × 374 mm** areas for the front lintel, optional jambs, hinge backing, stops and test pieces.

## Production cautions

- Allow for actual saw kerf and edge trimming; do not mark every panel directly from nominal sheet edges without checking the cutting sequence.
- Measure actual plywood thickness. The nominal rear-wall width of **876 mm** assumes exactly 12 mm side panels.
- Define the overlap direction for every joint before marking the sheet.
- Do not reuse an external dimension directly for a panel that must fit between two other sheets.
- Confirm whether the top shelf sits over the side walls or between them; this changes its final cutting size and load path.
- Confirm hinge geometry before drilling or cutting reinforcement parts.
- Verify tower support framing before using the top shelf as a structural member.
- Test the front opening and docking path using a temporary timber or cardboard mock-up before cutting the decorative facade.

## Roof interface

- Roof module footprint: approximately **1040 × 940 mm**.
- Gable rise: **280–300 mm** above the 560 mm lower box.
- Hinge line: rear top edge of the lower box or a raised rear hinge batten.
- Roof module should land on structural roof stops fixed to framing.
- Wide tower footprint: approximately **480–520 × 450–500 mm**.
- Tower support must bridge or reinforce both roof slopes.

## Final recommendation

Use the **1000 × 900 × 560 mm lower box** as the current project baseline.

It provides practical clearance over the measured Luba 3 AWD envelope and keeps the front facade close to the golden ratio. Before any further cutting, revise every panel dimension using the defined joint-overlap rule and the actual measured plywood thickness.