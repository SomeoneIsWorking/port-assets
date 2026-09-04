# Project state

## Comparison baseline

The baseline is every port drawing or sourcing its own inconsistent controller, keyboard, device, and
touch prompts. port-assets provides one original, scalable, target-size-checked visual language that
consumers can label and render for their actual bindings.

## Current focus

None. The current shared glyph families are verified.

## Capability inventory

| ID | Capability or outcome | State | Factual dependency | Goals |
| --- | --- | --- | --- | --- |
| S001 | Generic keyboard and gamepad device indicators are available as original SVGs | verified | — | G001 |
| S002 | A complete Xbox 360-style controller prompt family covers buttons, triggers, sticks, and directions | verified | — | G001 |
| S003 | Label-neutral keyboard keycaps can display the consumer's actual binding | verified | — | G001 |
| S004 | Authored touch-direction controls provide distinct up, down, left, and right prompts | verified | — | G001 |
| S005 | Manifests and authoring checks prevent missing, stale, or indistinguishable glyphs, with target-background review required for legibility | verified | S001, S002, S003, S004 | G001 |
| S006 | Asset authoring and target-size raster checks run in hosted verification | partial | S005 | G001 |

## Capability details

### S001 — Device indicators

Evidence: the devices set ships keyboard and gamepad silhouettes and its authoring check reproduces the
committed SVGs.

### S002 — Controller prompts

Evidence: the Xbox 360-style set covers the documented controls and tests reject duplicate direction
rasters and manifest/file drift at target size.

### S003 — Keyboard keycaps

Evidence: the keyboard set keeps labels out of the base art and `draw_keyboard.py` composes arbitrary
binding labels for consumers.

### S004 — Touch controls

Evidence: the touch-control set has four direction-specific SVGs, an authoritative drawing script, and
the same small-size family checks.

### S005 — Verification tooling

Evidence: `tests/test_sets.py` and the `draw_*.py --check` routes automate set completeness,
deterministic source generation, nonblank target-size rasters, and distinct direction families. The
documented sheet review remains the required human check over light, dark, and mid-tone backgrounds.

### S006 — Hosted verification

The Linux workflow runs every authoring check and the ImageMagick-backed 18px raster test without
game files or consumer repositories.

Gap: the first hosted run is still required before this item can be marked verified.

Platform applicability: Windows and macOS have no asset-specific runtime, compiler, or packaging
boundary; the SVG and Python behavior is host-independent and is covered by the Linux raster job.
Android is inapplicable because this repository ships no Android runtime or package; consuming ports
own their Android integration and use these same source SVGs.
