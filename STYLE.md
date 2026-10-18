# Icon Monks style guide

These rules apply to every new icon. `python3 scripts/lint.py` checks the ones marked **[lint]**.
Icons made before this guide are listed in `scripts/lint-baseline.json`. The lint skips their known problems,
but the same problems in a new icon fail the check.

## The system

Icon Monks uses the same construction as Phosphor, so the two sets sit together in one UI:

- **Grid**: 256 × 256, geometry inside the **32–224 live area** **[lint `live-area`]**.
- **Stroke**: 16 units, round caps, round joins **[lint `stroke`]**. The build turns this into thin 8, light 12,
  regular 16 and bold 24. Fill and duotone come from the roles.
- **Roles**: every shape sits in a `<g data-role>` group: `line`, `detail`, `area`, `hole`, `dot`, `dotcut`
  **[lint `role`]**. The README explains what each role does in each weight.
- **Metadata**: one `data-category` from the 30 categories and at least 3 `data-tags` **[lint `meta`]**.

## Rules

1. **Every closed silhouette gets an `area`** **[lint `no-fill`]**. If you draw a closed shape (a path that ends
   in `Z`, a circle, a rect) and the icon has no `area`, `detail`, `hole` or `dotcut`, the fill weight is just the
   regular outline. That's wrong. Letters, numbers and typographic symbols, where filling would close up the
   counters, stay outlined in every weight: mark them `data-fill="outline"` on the `<svg>` so it's a decision,
   not an oversight. `scripts/batches/195_fill.py` auto-fills or marks icons.
2. **Whole-number coordinates** for straight-segment endpoints, circle centres and rect corners **[lint `off-grid`]**.
   Prefer multiples of 4. Round rotated or computed points instead of keeping decimals. Arc radii and curve
   control points can be anything.
3. **At most 8 stroked elements** (`line` + `detail`) **[lint `detail`]**. Leave a gap of at least 24 units
   between parallel strokes. Anything finer disappears at 16 px. Leave out texture, feathers, fur and small text.
   Repeated simple strokes (dashed outlines, grids, sun rays) can go over the count and still read: check the icon
   at 16 px and, if it does, mark it `data-detail="reviewed"` on the `<svg>` (`reviewed=True` in `draw.py`).
4. **Same visual size: keylines** **[lint `keyline`, `small`]**. A container shape that spans the whole icon
   keeps to its keyline (centreline sizes): circle 192, square 176, wider or taller rectangle 192 on the long side.
   Open shapes use the full live area. The larger side spans at least 144 units; only carets, dots and similar
   small symbols stay below that, marked `data-size="symbol"` (`symbol=True` in `draw.py`).
   `scripts/batches/196_keylines.py` scales an icon onto its keyline.
5. **Slash icons are the base icon plus a slash** **[lint `slash`]**. `<name>-slash` repeats `<name>` unchanged and
   adds one `slash` group with `M48 48 L208 208`. Use the mirrored `M208 48 L48 208` only when the base already runs
   along that diagonal, like a magnifier handle. The build cuts a 16-unit gap around the slash in every weight, so
   never trim the icon by hand. Run `scripts/batches/194_slash.py` after changing a base icon.
6. **Dots**: `dot` uses r=16 (renders r=12 at regular). Eyes and other `dotcut`s use r=14.
7. **People**:
   - Full figures copy `person`: an open head circle r=24 and limbs as single strokes.
   - Busts copy `user`: head r=44 and a shoulder curve.
   - Don't mix a filled head with stick limbs, and don't use a different head size in the same family.
8. **Corners**: rect `rx` is 16 on large containers (cards, windows, devices) and 8 on small parts inside them.
   *Proposal, not yet linted. The existing set uses 8–20 freely.*
9. **Draw curves as curves** **[lint `tessellated`]**. Use arcs and cubics with anchors on the curve's
   horizontal and vertical extremes and smooth joins. Don't save a sampled formula or a flattened boolean result as
   dozens of straight segments. `scripts/batches/193_refit.py` converts such paths back to curves.
   **[lint `extremes`]** A curve that bulges more than a unit past its ends needs an anchor at that extreme
   (its leftmost, rightmost, top or bottom point). `scripts/batches/198_extremes.py` adds them without changing the
   shape.
10. **No text glyphs** inside icons (like "CI" in a triangle) except in Letters & Numbers and the file-type
   family (`file-jpg`, `file-html` and so on), where the label is the point of the icon. Text doesn't scale
   across weights.

## Adding icons

1. Find the closest clean reference icon (`house`, `bell`, `gear`, `envelope`, `person`, `user`) and build from it
   with `load()` in `scripts/draw.py`.
2. Run `python3 scripts/lint.py <names>` and fix everything it reports.
3. Render a sheet: `python3 scripts/preview.py out.png <names>`. Check the 16 px column. If you can't tell what an
   icon is at 16 px, remove detail.
4. Run `npm run build`.

Every rule is a hard failure. `scripts/lint-baseline.json` lists only the icons waiting to be redrawn
(`REDRAW` in `scripts/batches/199_marks.py`). When you redraw one, run `python3 scripts/lint.py --update-baseline`
and commit the smaller file. Never add an entry to it: fix the icon, or mark it after a 16 px review.
