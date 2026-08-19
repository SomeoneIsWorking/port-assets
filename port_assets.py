"""Locate and read the shared asset sets. The ONE entry point for a consumer.

    import port_assets
    port_assets.sets()                      # ['gamepad-xbox360', 'keyboard']
    port_assets.names('gamepad-xbox360')    # ['back', 'dpad', 'dpad_down', ...]
    port_assets.path('gamepad-xbox360', 'lb')   # -> .../lb.svg

A project consumes this repo, it does not vendor it. `resolve()` finds the
checkout and REFUSES by naming every path it tried, rather than falling back to
an in-tree copy -- a stale vendored copy that silently wins is the failure this
split exists to end.

Resolution order: `$PORT_ASSETS_DIR`, then `$SHARED_DIR/port-assets`, then the
sibling checkout the standard `shared/` layout implies.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

_HERE = Path(__file__).resolve().parent
MARKER = "sets"


def resolve(start: Path | None = None) -> Path:
    """The port-assets checkout.

    `start` is the calling project's root, used to find the sibling `shared/`
    directory. Defaults to this file's own repo, so importing it directly just
    works.
    """
    tried: list[Path] = []
    env = os.environ.get("PORT_ASSETS_DIR")
    if env:
        tried.append(Path(env))
    shared = os.environ.get("SHARED_DIR")
    if shared:
        tried.append(Path(shared) / "port-assets")
    if start is not None:
        # e.g. <root>/pc/xmen2 -> <root>/shared/port-assets
        tried.append(start.resolve().parent.parent / "shared" / "port-assets")
    tried.append(_HERE)

    for path in tried:
        if (path / MARKER).is_dir():
            return path
    raise SystemExit(
        "port_assets: no checkout found. Looked in:\n"
        + "".join("    %s\n" % p for p in tried)
        + "(each had to contain a %r directory)\n" % MARKER
        + "It is a separate repo that projects CONSUME rather than vendor.\n"
          "Clone it into `shared/` or set PORT_ASSETS_DIR.")


def set_dir(name: str, start: Path | None = None) -> Path:
    root = resolve(start)
    path = root / "sets" / name
    if not path.is_dir():
        raise SystemExit(
            "port_assets: %s has no set called %r. Sets present: %s"
            % (root, name, ", ".join(sets(start)) or "none"))
    return path


def sets(start: Path | None = None) -> list[str]:
    root = resolve(start)
    return sorted(p.name for p in (root / "sets").iterdir() if p.is_dir())


def manifest(name: str, start: Path | None = None) -> dict:
    path = set_dir(name, start) / "set.json"
    if not path.is_file():
        raise SystemExit("port_assets: %s has no set.json, so its contents are "
                         "undeclared and cannot be checked." % path.parent)
    return json.loads(path.read_text())


def names(name: str, start: Path | None = None) -> list[str]:
    """The set's glyph names, from its manifest, checked against the files.

    A manifest that names a file which is not there is refused rather than
    returned short: a consumer that publishes ten of eleven glyphs draws a
    blank for one prompt and looks like a game bug.
    """
    declared = list(manifest(name, start).get("glyphs", []))
    here = set_dir(name, start)
    missing = [g for g in declared if not (here / (g + ".svg")).is_file()]
    if missing:
        raise SystemExit("port_assets: %s declares %d glyph(s) whose SVG is "
                         "missing: %s" % (name, len(missing),
                                          ", ".join(missing)))
    present = {p.stem for p in here.glob("*.svg")}
    extra = sorted(present - set(declared))
    if extra:
        raise SystemExit("port_assets: %s holds %d SVG(s) its manifest does "
                         "not declare: %s" % (name, len(extra),
                                              ", ".join(extra)))
    return declared


def path(set_name: str, glyph: str, start: Path | None = None) -> Path:
    here = set_dir(set_name, start) / (glyph + ".svg")
    if not here.is_file():
        raise SystemExit("port_assets: %s has no glyph %r. It has: %s"
                         % (set_name, glyph, ", ".join(names(set_name, start))))
    return here
