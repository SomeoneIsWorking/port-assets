#!/usr/bin/env python3
"""Author generic keyboard and gamepad device icons.

These identify an input-device column; individual button prompts continue to use the
keyboard and gamepad-xbox360 sets. Both icons use the shared 72-unit cell and remain legible
at the library's 18-pixel minimum.

    python3 tools/draw_devices.py
    python3 tools/draw_devices.py --check
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sets" / "devices"
INK = "#101014"
LIGHT = "#F0F0F2"
MID = "#C8C8CC"


def svg(*body: str) -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72 72" '
            'width="72" height="72">\n'
            + "".join("  " + line + "\n" for line in body)
            + "</svg>\n")


def keyboard() -> str:
    keys = []
    for y, count in ((24, 8), (34, 8), (44, 7)):
        for x in range(count):
            keys.append('<rect x="%d" y="%d" width="5" height="6" rx="1"/>'
                        % (12 + x * 7, y))
    keys.append('<rect x="24" y="54" width="25" height="6" rx="2"/>')
    return svg(
        '<rect x="5" y="14" width="62" height="50" rx="7" fill="%s" '
        'stroke="%s" stroke-width="5"/>' % (LIGHT, INK),
        '<g fill="%s">%s</g>' % (INK, "".join(keys)),
        '<path d="M11 19 h50" stroke="#FFFFFF" stroke-width="3" '
        'stroke-linecap="round" opacity="0.75"/>')


def gamepad() -> str:
    return svg(
        '<path d="M19 22 C10 23 6 32 5 44 C4 56 9 63 16 59 L27 50 '
        'H45 L56 59 C63 63 68 56 67 44 C66 32 62 23 53 22 '
        'C47 22 43 27 36 27 C29 27 25 22 19 22 Z" fill="%s" '
        'stroke="%s" stroke-width="5" stroke-linejoin="round"/>' % (LIGHT, INK),
        '<path d="M16 37 h7 v-7 h7 v7 h7 v7 h-7 v7 h-7 v-7 h-7 z" fill="%s"/>' % INK,
        '<circle cx="52" cy="34" r="4" fill="%s"/>' % INK,
        '<circle cx="59" cy="42" r="4" fill="%s"/>' % INK,
        '<circle cx="45" cy="42" r="4" fill="%s"/>' % INK,
        '<circle cx="52" cy="50" r="4" fill="%s"/>' % INK,
        '<circle cx="36" cy="38" r="3" fill="%s"/>' % MID)


def build() -> dict[str, str]:
    return {"keyboard": keyboard(), "gamepad": gamepad()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    icons = build()
    OUT.mkdir(parents=True, exist_ok=True)
    different = []
    wrote = 0
    for name, body in sorted(icons.items()):
        path = OUT / (name + ".svg")
        old = path.read_text() if path.is_file() else None
        if old == body:
            continue
        if args.check:
            different.append(name)
        else:
            path.write_text(body, encoding="ascii")
            wrote += 1
    if args.check:
        if different:
            print("draw_devices --check: generated SVG differs: " + ", ".join(different),
                  file=sys.stderr)
            return 1
        print("draw_devices --check: all %d icons match" % len(icons))
        return 0
    (OUT / "set.json").write_text(json.dumps({
        "name": "devices",
        "description": "Generic keyboard and gamepad icons for device labels",
        "authored_by": "tools/draw_devices.py",
        "glyphs": sorted(icons),
    }, indent=2) + "\n", encoding="ascii")
    print("wrote %d changed icon(s) of %d into %s" % (wrote, len(icons), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
