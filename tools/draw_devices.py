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


def svg(*body: str) -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72 72" '
            'width="72" height="72">\n'
            + "".join("  " + line + "\n" for line in body)
            + "</svg>\n")


def keyboard() -> str:
    keys = []
    for y, start, count in ((28, 9, 8), (37, 12, 7)):
        for index in range(count):
            keys.append('<rect x="%d" y="%d" width="5" height="5" rx="1"/>'
                        % (start + index * 7, y))
    return svg(
        '<path d="M8 21 H64 Q67 21 68 25 L70 53 Q70 58 65 58 H7 '
        'Q2 58 2 53 L4 25 Q5 21 8 21 Z" fill="%s" stroke="%s" '
        'stroke-width="5" stroke-linejoin="round"/>' % (LIGHT, INK),
        '<g fill="%s">%s</g>' % (INK, "".join(keys)),
        '<rect x="9" y="46" width="8" height="5" rx="1" fill="%s"/>' % INK,
        '<rect x="21" y="46" width="30" height="5" rx="2" fill="%s"/>' % INK,
        '<rect x="55" y="46" width="8" height="5" rx="1" fill="%s"/>' % INK)


def gamepad() -> str:
    return svg(
        '<path d="M19 23 C12 23 8 29 6 39 L4 51 C3 58 7 63 13 62 '
        'Q16 61 20 57 L27 51 Q31 48 36 48 Q41 48 45 51 L52 57 '
        'Q56 61 59 62 C65 63 69 58 68 51 L66 39 C64 29 60 23 53 23 '
        'C47 23 43 27 36 27 C29 27 25 23 19 23 Z" fill="%s" '
        'stroke="%s" stroke-width="5" stroke-linejoin="round"/>' % (LIGHT, INK),
        '<path d="M14 35 h6 v-6 h6 v6 h6 v6 h-6 v6 h-6 v-6 h-6 z" fill="%s"/>' % INK,
        '<circle cx="52" cy="31" r="3.5" fill="%s"/>' % INK,
        '<circle cx="60" cy="39" r="3.5" fill="%s"/>' % INK,
        '<circle cx="44" cy="39" r="3.5" fill="%s"/>' % INK,
        '<circle cx="52" cy="47" r="3.5" fill="%s"/>' % INK,
        '<rect x="34" y="34" width="5" height="3" rx="1.5" fill="%s"/>' % INK)


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
