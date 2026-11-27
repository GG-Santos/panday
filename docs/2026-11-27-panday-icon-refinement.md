# Panday Icon System Refinement

## Intent

Make the 12 Panday skill icons feel like one product family while remaining
recognizable at README, catalog, and small UI sizes. The icons are repository
assets, not runtime instructions.

## Research-derived criteria

The refinement uses the following public design-system guidance:

- Material recommends bold, geometric silhouettes, consistent stroke treatment,
  optical correction, and generous clearance around the icon.
- Fluent recommends recognizable metaphors, fixed pixel sizes, and avoiding
  modifiers that add unnecessary complexity.
- Carbon recommends optical centering, consistent containers, accepted scale
  increments, and accessible text equivalents.

References: [Material system icons](https://m2.material.io/design/iconography/system-icons.html),
[Fluent iconography](https://fluent2.microsoft.design/iconography), and
[Carbon icon guidelines](https://www.carbondesignsystem.com/building-blocks/foundations/icons/guidelines).

## Shared design contract

- SVG `viewBox="0 0 64 64"`; no embedded wordmarks or external fonts.
- Dark `#0f172a` circular container with a 3px accent ring and a light glyph.
- 27.5px ring radius, leaving a consistent three-pixel outer clearance.
- One simple semantic metaphor per skill; labels live outside the glyph.
- `role="img"` plus a skill-specific `aria-label` on every asset.
- Icons remain vector-native so they scale cleanly in GitHub and host catalogs.

## Fifteen refinement passes

| Pass | Research / plan / refinement / analysis | Result |
| ---: | --- | --- |
| 1 | Audited all 12 existing assets and rendered a contact sheet. | Found label crowding, uneven clearance, and Inspect/Card similarity. |
| 2 | Compared the set with Material grid/stroke guidance. | Chose one 64px grid and a shared circular container. |
| 3 | Compared with Fluent semantic and fixed-size guidance. | Removed text from glyphs; retained accessible labels. |
| 4 | Compared with Carbon clearance and optical-centering guidance. | Changed the ring from 29px to 27.5px radius. |
| 5 | Re-rendered at catalog scale. | Confirmed no icon touches the container edge. |
| 6 | Refined Inspect’s metaphor. | Added a magnifier overlay to distinguish source review. |
| 7 | Refined Card’s metaphor. | Added a clear card header and content hierarchy. |
| 8 | Checked semantic uniqueness across the 12 names. | Kept search, pencil, document+magnifier, chart, wrench, download, card, plus, merge, trend, chain, and transfer metaphors. |
| 9 | Checked stroke rhythm and visual weight. | Preserved bold strokes and a common dark-node treatment. |
| 10 | Rendered a 128px contact sheet. | Confirmed consistent optical scale and balanced negative space. |
| 11 | Rendered a 64px contact sheet. | Confirmed glyphs remain legible without embedded labels. |
| 12 | Checked contrast and color separation. | Retained one accent family per icon with light glyphs on dark containers. |
| 13 | Checked accessibility metadata. | All 12 assets expose `role="img"` and a specific `aria-label`. |
| 14 | Checked package parity. | The source tree and release ZIP contain the same 12 refined icons and hero asset. |
| 15 | Checked publication parity. | `main` is source-first, `v1.0.0` owns the ZIP, and installers target the release asset. |

## Acceptance

- 12/12 skill folders contain `assets/icon.svg`.
- 12/12 icons use the shared 64px contract and contain no `<text>` elements.
- The rendered contact sheet shows no clipping, label collision, or container
  edge contact.
- The source tree and release asset are deliberately separated: source is
  browsable on `main`; the ZIP is attached to the GitHub release.
