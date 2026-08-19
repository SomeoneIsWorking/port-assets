#!/usr/bin/env python3
"""Author the `gamepad-xbox360` glyph set.

The SVGs are CHECKED IN -- they are the resource, and a consumer must never
need this script to get them. It exists so the set stays internally consistent
when it grows: one place holds the palette, the stroke weights and the cell
geometry, so a glyph added next year matches the ones drawn today instead of
being eyeballed against them.

    python3 tools/draw_xbox360.py            # rewrite sets/gamepad-xbox360/
    python3 tools/draw_xbox360.py --check    # fail if the checked-in files differ

Every glyph is drawn in a 72x72 viewBox and is meant to be rasterised into a
SQUARE cell as small as 18x18. That size is the whole design constraint and it
is measured, not assumed -- see `tools/sheet.py` and the README.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sets" / "gamepad-xbox360"

# ---- palette -------------------------------------------------------------
# The 360's own button colours, plus a light body and a dark outline. Light
# fill and dark outline together are what let a glyph survive BOTH a dark HUD
# panel and a bright scene: on a dark background the fill carries it, on a
# light one the outline does.
DARK = "#101010"
LIGHT = "#DCDCDC"
WHITE = "#FFFFFF"
BODY_DARK = "#303030"
FACE = {"a": "#5FB13A", "b": "#D13B33", "x": "#2E6DB4", "y": "#E8B21F"}

FONT = 'font-family="DejaVu Sans,Verdana,sans-serif" font-weight="bold"'
HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72 72"'
        ' width="72" height="72">\n')
TAIL = "</svg>\n"


def svg(*body: str) -> str:
    return HEAD + "".join("  " + line + "\n" for line in body) + TAIL


def text(x, y, size, fill, s, length=None):
    fit = (' textLength="%d" lengthAdjust="spacingAndGlyphs"' % length
           if length else "")
    return ('<text x="%d" y="%d" %s font-size="%d" fill="%s" '
            'text-anchor="middle"%s>%s</text>' % (x, y, FONT, size, fill, fit, s))


# ---- face buttons --------------------------------------------------------
def face(letter: str) -> str:
    return svg(
        '<circle cx="36" cy="36" r="30" fill="%s" stroke="%s" stroke-width="6"/>'
        % (FACE[letter], DARK),
        text(36, 52, 46, WHITE, letter.upper()))


# ---- shoulders and triggers ----------------------------------------------
# TWO letters, because the platform prints two and because one letter cannot
# say which of the four a prompt means. An earlier version of this set drew a
# single `R` and distinguished bumper from trigger by INVERTING the fill; at
# 18x18 that is not a cue a player can act on, and the report that killed it
# was "the button says R but is it RB or RT?".
# The SHAPE differs too, and not only the letters: a bumper is the flat bar
# across the top of the pad, a trigger is the paddle underneath it, and at very
# small sizes the silhouette is what survives when the two letters have blurred
# into one grey smudge. Two cues, so neither has to carry it alone.
def shoulder(name: str) -> str:
    if name.endswith("b"):                       # bumper: a squat flat bar
        shape = ('<rect x="2" y="18" width="68" height="36" rx="16" fill="%s" '
                 'stroke="%s" stroke-width="5"/>' % (LIGHT, DARK))
    else:                                        # trigger: a tapering paddle
        shape = ('<path d="M8 18 a10 10 0 0 1 10 -8 h36 a10 10 0 0 1 10 8 '
                 'v14 a22 22 0 0 1 -22 22 h-12 a22 22 0 0 1 -22 -22 z" '
                 'fill="%s" stroke="%s" stroke-width="5" '
                 'stroke-linejoin="round"/>' % (LIGHT, DARK))
    return svg(shape, text(36, 46, 30, DARK, name.upper(), length=50))


# ---- menu buttons --------------------------------------------------------
def start() -> str:
    return svg(
        '<circle cx="36" cy="36" r="30" fill="%s" stroke="%s" stroke-width="6"/>'
        % (LIGHT, DARK),
        '<g fill="%s"><rect x="18" y="25" width="36" height="9" rx="4"/>'
        '<rect x="18" y="40" width="36" height="9" rx="4"/></g>' % DARK)


def back() -> str:
    return svg(
        '<circle cx="36" cy="36" r="30" fill="%s" stroke="%s" stroke-width="6"/>'
        % (LIGHT, DARK),
        '<path d="M46 20 L26 36 L46 52 z" fill="%s"/>' % DARK,
        '<rect x="18" y="20" width="7" height="32" rx="3" fill="%s"/>' % DARK)


def guide() -> str:
    return svg(
        '<circle cx="36" cy="36" r="30" fill="%s" stroke="%s" stroke-width="6"/>'
        % (LIGHT, DARK),
        '<path d="M36 14 a22 22 0 0 1 0 44 a14 22 0 0 0 0 -44 z" fill="%s"/>'
        % "#5FB13A")


# ---- d-pad ---------------------------------------------------------------
# The named direction is shown by LIGHTING that arm of the cross. The cross
# itself is kept -- a prompt for a d-pad direction has to read as the d-pad,
# not as a bare arrow -- and the lit arm is what says which one. All four
# collapsed to a single unlit cross once, and a screen offering four d-pad
# choices then drew the same picture four times.
CROSS = "M27 8 h18 v19 h19 v18 h-19 v19 h-18 v-19 h-19 v-18 h19 z"
ARM = {"up":    "M28 9 h16 v18 h-16 z",
       "down":  "M28 45 h16 v18 h-16 z",
       "left":  "M9 28 h18 v16 h-18 z",
       "right": "M45 28 h18 v16 h-18 z"}


def dpad(direction: str | None) -> str:
    body = ('<path d="%s" fill="%s" stroke="%s" stroke-width="6" '
            'stroke-linejoin="round"/>' % (CROSS, BODY_DARK, LIGHT))
    if direction is None:
        return svg(body)
    return svg(body, '<path d="%s" fill="%s"/>' % (ARM[direction], WHITE))


# ---- sticks --------------------------------------------------------------
# A stick is the cap seen from above. Click marks the centre; a direction hangs
# a SOLID WEDGE off the side it is pushed -- the same device as the d-pad's lit
# arm, and for the same measured reason. The first version drew the cap
# slightly off-centre inside a dashed travel ring, which at 18x18 rasterised
# into four circles nobody could tell apart.
STICK_WEDGE = {
    "up":    "M36 3 l22 26 h-44 z",
    "down":  "M36 69 l22 -26 h-44 z",
    "left":  "M3 36 l26 -22 v44 z",
    "right": "M69 36 l-26 -22 v44 z",
}
STICK_CAP = {"up": (36, 46), "down": (36, 26), "left": (46, 36),
             "right": (26, 36), "click": (36, 36)}


def stick(side: str, what: str) -> str:
    cx, cy = STICK_CAP[what]
    r = 20 if what == "click" else 16
    cap = ('<circle cx="%d" cy="%d" r="%d" fill="%s" stroke="%s" '
           'stroke-width="6"/>' % (cx, cy, r, BODY_DARK, LIGHT))
    if what == "click":
        return svg(cap, '<circle cx="36" cy="36" r="9" fill="%s"/>' % WHITE)
    return svg('<path d="%s" fill="%s" stroke="%s" stroke-width="4" '
               'stroke-linejoin="round"/>'
               % (STICK_WEDGE[what], WHITE, BODY_DARK), cap)


# ---- the set -------------------------------------------------------------
def build() -> dict[str, str]:
    out: dict[str, str] = {}
    for letter in ("a", "b", "x", "y"):
        out["face_" + letter] = face(letter)
    for name in ("lb", "rb", "lt", "rt"):
        out[name] = shoulder(name)
    out["start"] = start()
    out["back"] = back()
    out["guide"] = guide()
    out["dpad"] = dpad(None)
    for d in ("up", "down", "left", "right"):
        out["dpad_" + d] = dpad(d)
    for side in ("ls", "rs"):
        out[side] = stick(side, "click")
        for d in ("up", "down", "left", "right"):
            out["%s_%s" % (side, d)] = stick(side, d)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="compare against the checked-in files, write nothing")
    args = ap.parse_args()

    glyphs = build()
    OUT.mkdir(parents=True, exist_ok=True)
    differ, wrote = [], 0
    for name, body in sorted(glyphs.items()):
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
        extra = sorted(p.stem for p in OUT.glob("*.svg")
                       if p.stem not in glyphs)
        if differ or extra:
            print("draw_xbox360 --check: %d glyph(s) differ from this script "
                  "(%s), %d checked-in file(s) it does not author (%s)"
                  % (len(differ), ", ".join(differ) or "none",
                     len(extra), ", ".join(extra) or "none"), file=sys.stderr)
            return 1
        print("draw_xbox360 --check: all %d glyph(s) match the checked-in set"
              % len(glyphs))
        return 0

    manifest = OUT / "set.json"
    manifest.write_text(json.dumps({
        "name": "gamepad-xbox360",
        "description": "Xbox 360 controller button glyphs, drawn for cells as "
                       "small as 18x18",
        "authored_by": "tools/draw_xbox360.py",
        "glyphs": sorted(glyphs),
    }, indent=2) + "\n", encoding="ascii")
    print("wrote %d changed glyph(s) of %d into %s"
          % (wrote, len(glyphs), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
