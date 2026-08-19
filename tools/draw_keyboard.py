#!/usr/bin/env python3
"""Author the `keyboard` set: a blank key cap, and labelled caps on demand.

Taken from zelda3d, which draws its HUD key badges this way and is the reason
this is a SHARED set rather than a per-project one. The important idea there is
that **the label is not baked into the art**: one cap is drawn, and the text
composited over it comes from the key that is actually bound, so a rebind
changes the prompt with no new asset. Keeping that split is what makes a
keyboard set finite -- there are a hundred key names and one cap.

    python3 tools/draw_keyboard.py                 # rewrite sets/keyboard/
    python3 tools/draw_keyboard.py --label ENTER   # print a labelled cap to stdout
    python3 tools/draw_keyboard.py --check

`cap.svg` is the blank. `labelled(text)` composes one, and a consumer that
rasterises into a fixed cell should ask for the WIDE cap when the label is more
than a character or two -- a five-letter key name squeezed into a square cell
is the same unreadable mush that a two-letter one is at 18x18.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sets" / "keyboard"

FONT = 'font-family="DejaVu Sans,Verdana,sans-serif" font-weight="bold"'
FACE_TOP, FACE_BOTTOM = "#F4F4F5", "#D8D8DA"
EDGE, INK = "#3A3A3E", "#101014"


def cap(width: int = 72, label: str | None = None) -> str:
    """A key cap `width` units wide in a 72-unit-tall box, optionally labelled.

    The cap is drawn as a face with a lighter top bevel, which is what makes it
    read as a KEY rather than as a plain box at small sizes -- the same reason
    the square brackets it replaces read as a key in text.
    """
    inner = width - 10
    body = [
        '<defs>',
        '  <linearGradient id="cap" x1="0" y1="0" x2="0" y2="1">',
        '    <stop offset="0%%" stop-color="%s"/>' % FACE_TOP,
        '    <stop offset="100%%" stop-color="%s"/>' % FACE_BOTTOM,
        '  </linearGradient>',
        '</defs>',
        '<rect x="5" y="6" width="%d" height="60" rx="10" ry="10" '
        'fill="url(#cap)" stroke="%s" stroke-width="5"/>' % (inner, EDGE),
        '<rect x="11" y="12" width="%d" height="9" rx="4" ry="4" '
        'fill="#FFFFFF" fill-opacity="0.6"/>' % (inner - 12),
    ]
    if label:
        # textLength keeps a long name inside the cap instead of overflowing it
        # invisibly, which is what an unconstrained <text> does when rasterised.
        body.append(
            '<text x="%d" y="50" %s font-size="38" fill="%s" '
            'text-anchor="middle" textLength="%d" '
            'lengthAdjust="spacingAndGlyphs">%s</text>'
            % (width // 2, FONT, INK, inner - 14, escape(label)))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d 72" '
            'width="%d" height="72">\n' % (width, width)
            + "".join("  " + line + "\n" for line in body)
            + "</svg>\n")


def escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))


def build() -> dict[str, str]:
    """The checked-in files: the blanks, in the three widths a prompt needs."""
    return {
        "cap": cap(72),
        "cap_wide": cap(120),
        "cap_extra_wide": cap(180),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--label", help="print a labelled cap instead of writing")
    ap.add_argument("--width", type=int, default=0,
                    help="cap width in viewBox units (default: fits the label)")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if args.label:
        width = args.width or max(72, 34 + 26 * len(args.label))
        sys.stdout.write(cap(width, args.label))
        return 0

    caps = build()
    OUT.mkdir(parents=True, exist_ok=True)
    differ, wrote = [], 0
    for name, body in sorted(caps.items()):
        path = OUT / (name + ".svg")
        old = path.read_text() if path.is_file() else None
        if old == body:
            continue
        if args.check:
            differ.append(name)
            continue
        path.write_text(body, encoding="ascii")
        wrote += 1

    if args.check:
        if differ:
            print("draw_keyboard --check: %d cap(s) differ from this script: %s"
                  % (len(differ), ", ".join(differ)), file=sys.stderr)
            return 1
        print("draw_keyboard --check: all %d cap(s) match" % len(caps))
        return 0

    (OUT / "set.json").write_text(
        '{\n  "name": "keyboard",\n'
        '  "description": "Keyboard key caps. The LABEL is composited by the '
        'consumer, not baked in -- see tools/draw_keyboard.py --label.",\n'
        '  "authored_by": "tools/draw_keyboard.py",\n'
        '  "glyphs": [%s]\n}\n'
        % ", ".join('"%s"' % n for n in sorted(caps)), encoding="ascii")
    print("wrote %d changed cap(s) of %d into %s" % (wrote, len(caps), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
