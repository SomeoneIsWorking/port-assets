#!/usr/bin/env python3
"""Author the HUD set: the frames and counters a game HUD is put together from.

The consumer composites what changes at runtime: a glyph or an item icon inside
`ring` or `slot`, `heart` cropped over `heart_empty` for a part of a heart,
`bar_fill` cropped over `bar` for a meter. Every glyph is a 72-unit box; `bar`
and `bar_fill` are 216x24 and stretch along their length.

    python3 tools/draw_hud.py
    python3 tools/draw_hud.py --check
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sets" / "hud"

DARK = "#101820"
LIGHT = "#F2F7FA"
HEART = "M36 62C10 42 6 30 6 22a15 15 0 0 1 30-4 15 15 0 0 1 30 4c0 8-4 20-30 40Z"
RUPEE = "M36 5 56 22v28L36 67 16 50V22Z"


def svg(markup: str, width: int = 72, height: int = 72) -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'width="%d" height="%d">\n' % (width, height, width, height)
            + markup + "</svg>\n")


def build() -> dict[str, str]:
    outline = 'stroke="%s" stroke-width="5" stroke-linejoin="round"' % DARK
    return {
        "heart": svg('  <path d="%s" fill="#E8203A" %s/>\n'
                     '  <path d="M17 20a7 7 0 0 1 9-4" fill="none" stroke="#FFFFFF" '
                     'stroke-width="4" stroke-linecap="round" stroke-opacity="0.7"/>\n'
                     % (HEART, outline)),
        "heart_empty": svg('  <path d="%s" fill="#2A3038" fill-opacity="0.8" %s/>\n'
                           % (HEART, outline)),
        "rupee": svg('  <path d="%s" fill="#35C24A" %s/>\n'
                     '  <path d="M36 15 48 25v22L36 57 24 47V25Z" fill="#8FE79A"/>\n'
                     % (RUPEE, outline)),
        # A small key: a round bow with a hole, a shaft and two teeth.
        "key": svg('  <path d="M36 6a15 15 0 0 1 5 29v31h-10v-6h-8v-8h8v-4h-8v-8h8v-5A15 15 0 0 1 36 6Z'
                   'm0 9a6 6 0 1 0 0 12 6 6 0 0 0 0-12Z" fill="#C9CED6" fill-rule="evenodd" %s/>\n'
                   % outline),
        # A button: a dark glass disc the game's view shows through.
        "ring": svg('  <circle cx="36" cy="36" r="31" fill="%s" fill-opacity="0.45" '
                    'stroke="%s" stroke-width="4"/>\n' % (DARK, LIGHT)),
        # A touch-only item button: the same glass, squared.
        "slot": svg('  <rect x="5" y="5" width="62" height="62" rx="12" fill="%s" '
                    'fill-opacity="0.45" stroke="%s" stroke-width="4"/>\n' % (DARK, LIGHT)),
        "bar": svg('  <rect x="3" y="3" width="210" height="18" rx="9" fill="%s" '
                   'fill-opacity="0.6" stroke="%s" stroke-width="4"/>\n' % (DARK, LIGHT),
                   216, 24),
        "bar_fill": svg('  <rect x="7" y="7" width="202" height="10" rx="5" fill="#35C24A"/>\n',
                        216, 24),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    glyphs = build()
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.dumps({
        "name": "hud",
        "description": "HUD frames and counters: hearts, a rupee, a key, button rings, a meter",
        "authored_by": "tools/draw_hud.py",
        "glyphs": sorted(glyphs),
    }, indent=2) + "\n"
    files = {name + ".svg": content for name, content in glyphs.items()}
    files["set.json"] = manifest
    different = [name for name, content in sorted(files.items())
                 if not (OUT / name).is_file() or (OUT / name).read_text() != content]
    extra = sorted(path.name for path in OUT.glob("*.svg") if path.name not in files)
    if args.check:
        for name in different + extra:
            print("draw_hud: %s differs from the generator" % name, file=sys.stderr)
        return 1 if different or extra else 0
    for name in different:
        (OUT / name).write_text(files[name], encoding="ascii")
    print("draw_hud: wrote %d of %d" % (len(different), len(files)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
