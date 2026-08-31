# Project state

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
