#!/usr/bin/env python3
"""Author generic touch-control direction buttons.

The checked-in SVGs are the portable artwork.  This script is their single
authoring source so every port gets the same clear cardinal-direction shapes.

    python3 tools/draw_touch_controls.py
    python3 tools/draw_touch_controls.py --check
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sets" / "touch-controls"

HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72 72" '
        'width="72" height="72">\n')
TAIL = "</svg>\n"
DARK = "#101820"
FILL = "#35516A"
LIGHT = "#F2F7FA"

ARROWS = {
    "up": "M36 17 17 43h12v12h14V43h12Z",
    "down": "M36 55 17 29h12V17h14v12h12Z",
    "left": "M17 36l26-19v12h12v14H43v12Z",
    "right": "M55 36 29 17v12H17v14h12v12Z",
}


def button(direction: str) -> str:
    return (
        HEAD
        + '  <circle cx="36" cy="36" r="31" fill="%s" stroke="%s" '
          'stroke-width="5"/>\n' % (FILL, DARK)
        + '  <path d="%s" fill="%s"/>\n' % (ARROWS[direction], LIGHT)
        + TAIL
    )


def build() -> dict[str, str]:
    return {"direction_" + direction: button(direction) for direction in ARROWS}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    glyphs = build()
    OUT.mkdir(parents=True, exist_ok=True)
    different, wrote = [], 0
    for name, content in sorted(glyphs.items()):
        path = OUT / (name + ".svg")
        old = path.read_text() if path.is_file() else None
        if old == content:
            continue
        if args.check:
            different.append(name)
        else:
            path.write_text(content, encoding="ascii")
            wrote += 1

    if args.check:
        extra = sorted(path.stem for path in OUT.glob("*.svg")
                       if path.stem not in glyphs)
        if different or extra:
            print("draw_touch_controls --check: %d glyph(s) differ (%s), "
                  "%d unowned SVG(s) (%s)" %
                  (len(different), ", ".join(different) or "none",
                   len(extra), ", ".join(extra) or "none"), file=sys.stderr)
            return 1
        print("draw_touch_controls --check: all %d glyph(s) match" % len(glyphs))
        return 0

    (OUT / "set.json").write_text(json.dumps({
        "name": "touch-controls",
        "description": "Generic cardinal-direction touch buttons",
        "authored_by": "tools/draw_touch_controls.py",
        "glyphs": sorted(glyphs),
    }, indent=2) + "\n", encoding="ascii")
    print("wrote %d changed glyph(s) of %d into %s" %
          (wrote, len(glyphs), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
