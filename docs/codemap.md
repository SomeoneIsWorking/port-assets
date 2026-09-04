# port-assets ownership map

This repository owns original, scalable control artwork and the deterministic authoring checks that
keep the checked-in SVG sets complete and legible at consumer target sizes. It owns no game runtime,
platform package, or Android integration.

## Ownership

| Subsystem | Responsibility | Current location | Entry point | Deep doc |
| --- | --- | --- | --- | --- |
| SVG sets | Original device, controller, keyboard, and touch glyphs | `sets/` | `port_assets.path()` | `README.md` |
| Authoring | Deterministic source for checked-in SVGs | `tools/` (`draw_*.py`) | each script's `--check` | `README.md` |
| Validation | Manifest, SVG, raster, and direction-family checks | `tests/test_sets.py` | `python tests/test_sets.py` | `docs/project-state.md` |
| Hosted verification | Asset-free Linux raster validation | `.github/workflows/ci.yml` | GitHub Actions | `docs/project-state.md` |

## Placement index

- New glyph artwork belongs in the owning family under `sets/` and its authoring script.
- New completeness or target-size invariants belong in `tests/test_sets.py`.
- New host-specific runtime or packaging behavior belongs in the consuming port, not here.
