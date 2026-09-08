#!/usr/bin/env python3
"""Author generic touch-control directions and action silhouettes.

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

# Bold, font-independent silhouettes. Outlined light shapes remain readable
# over both the game's dark scenes and bright sky; tiny rays and text do not.
ACTIONS = {
    "attack": '<path d="M18 39V25q0-5 5-5h5V14h9v5h9v5h8v17L43 56H27Z"/>'
              '<path d="M28 22v12m9-13v13m9-8v10M19 39h14l7 7" fill="none"/>',
    "smash": '<path d="m15 18 17-9 23 23-10 15-13-7-7-13Z"/>'
             '<path d="m28 31-16 22 8 6 16-21Z"/>'
             '<path d="m45 54 8 8m2-18 9 2" fill="none"/>',
    "use": '<path d="M26 39V17a5 5 0 0 1 10 0v15l5-4 6 4 6 3v12'
           'L42 59H29L16 45q-5-8 1-10 3-1 9 4Z"/>'
           '<path d="M44 14h12m-6-6v12" fill="none"/>',
    "jump": '<path d="M36 8 16 29h13v20h14V29h13Z"/>'
            '<path d="M14 60q22-16 44 0" fill="none"/>',
    "powers": '<circle cx="36" cy="36" r="27"/>'
              '<path d="m39 16-18 24h13l-2 16 19-25H38Z" fill="#101820" stroke="none"/>',
    "pause": '<rect x="17" y="13" width="13" height="46" rx="3"/>'
             '<rect x="42" y="13" width="13" height="46" rx="3"/>',
    "power1": '<path d="M42 7 15 40h19l-5 25 29-38H39Z"/>',
    "power2": '<path d="m36 7 7 17 18-7-8 18 12 9-19 4-6 17-10-16'
              '-21 7 10-19L8 24l20 2Z"/>'
              '<circle cx="36" cy="36" r="6" fill="#101820" stroke="none"/>',
    "power3": '<path d="m36 8 23 9v18Q57 51 36 64 15 51 13 35V17Z"/>'
              '<path d="M36 23v25M24 35h24" fill="none"/>',
    "power4": '<path d="m36 5 8 21 22 10-22 9-8 22-9-22L5 36l22-10Z"/>'
              '<path d="m15 14 7 7m28 30 7 7m-42 0 7-7m28-30 7-7" fill="none"/>',
}


def action_icon(markup: str) -> str:
    return (HEAD + '  <g fill="%s" stroke="%s" stroke-width="4" '
            'stroke-linecap="round" stroke-linejoin="round">\n    '
            % (LIGHT, DARK) + markup + '\n  </g>\n' + TAIL)


def button(direction: str) -> str:
    return (
        HEAD
        + '  <circle cx="36" cy="36" r="31" fill="%s" stroke="%s" '
          'stroke-width="5"/>\n' % (FILL, DARK)
        + '  <path d="%s" fill="%s"/>\n' % (ARROWS[direction], LIGHT)
        + TAIL
    )


def build() -> dict[str, str]:
    return {**{"direction_" + direction: button(direction) for direction in ARROWS},
            **{name: action_icon(markup) for name, markup in ACTIONS.items()}}


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
        "description": "Generic touch direction buttons and action silhouettes",
        "authored_by": "tools/draw_touch_controls.py",
        "glyphs": sorted(glyphs),
    }, indent=2) + "\n", encoding="ascii")
    print("wrote %d changed glyph(s) of %d into %s" %
          (wrote, len(glyphs), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
