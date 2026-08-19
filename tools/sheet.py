#!/usr/bin/env python3
"""Rasterise a set at its TARGET size and show it, over several backgrounds.

This is the only honest way to accept a glyph. Everything in `sets/` is drawn
in a 72x72 viewBox and looks fine there; the question is always what survives
the 18x18 cell a 2005 font atlas gives it, and the answer has been "not what
you expected" every single time:

* two 26pt letters inside a pill became grey mush -- unreadable, and it was
  only obvious once rasterised;
* a d-pad arm marked with an inset block became a 2-pixel dot;
* an arrowhead drawn inside the arm vanished entirely;
* a mark filled in the outline's own colour disappeared into a DARK background
  while reading perfectly on a light one.

So: a sheet, at the real size, on a light, a dark and a mid-tone background,
zoomed with a POINT filter so the pixels are the pixels and not a smoothed
impression of them. If a glyph cannot be told from its neighbour here, it
cannot be told apart in the game.

    python3 tools/sheet.py gamepad-xbox360                 # every glyph, 18px
    python3 tools/sheet.py gamepad-xbox360 --size 24 --zoom 8
    python3 tools/sheet.py gamepad-xbox360 lb rb lt rt     # just these

Needs ImageMagick's `magick`, and REFUSES rather than writing a partial sheet
if a glyph fails to rasterise or comes out fully transparent -- a blank cell in
a contact sheet reads as "this glyph is subtle", which is the opposite of true.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
BACKGROUNDS = ("#DDDDDD", "#303030", "#6A8EA0")


def rasterise(src: Path, size: int, dst: Path) -> None:
    if not shutil.which("magick"):
        raise SystemExit("sheet: ImageMagick's `magick` is not on PATH, so "
                         "NOTHING was rasterised and no sheet was written.")
    run = subprocess.run(["magick", "-background", "none", str(src),
                          "-resize", "%dx%d" % (size, size),
                          "PNG32:" + str(dst)], capture_output=True)
    if run.returncode or not dst.is_file():
        raise SystemExit("sheet: REFUSING -- %s failed to rasterise: %s"
                         % (src.name, run.stderr.decode()[:200]))
    probe = subprocess.run(["magick", str(dst), "-format", "%[opaque]",
                            "info:"], capture_output=True, text=True)
    alpha = subprocess.run(["magick", str(dst), "-alpha", "extract",
                            "-format", "%[fx:maxima]", "info:"],
                           capture_output=True, text=True)
    if alpha.stdout.strip() in ("0", "0.0"):
        raise SystemExit("sheet: REFUSING -- %s rasterised to something fully "
                         "transparent at %dpx. It would publish as a blank "
                         "prompt." % (src.name, size))
    del probe


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("set_name")
    ap.add_argument("glyphs", nargs="*",
                    help="glyph names; default is the whole set")
    ap.add_argument("--size", type=int, default=18,
                    help="cell size in pixels (default 18)")
    ap.add_argument("--zoom", type=int, default=6)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    src_dir = ROOT / "sets" / args.set_name
    if not src_dir.is_dir():
        raise SystemExit("sheet: no set called %r under %s. Sets present: %s"
                         % (args.set_name, ROOT / "sets",
                            ", ".join(sorted(p.name for p in
                                             (ROOT / "sets").iterdir()
                                             if p.is_dir())) or "none"))
    names = args.glyphs or sorted(p.stem for p in src_dir.glob("*.svg"))
    missing = [n for n in names if not (src_dir / (n + ".svg")).is_file()]
    if missing:
        raise SystemExit("sheet: %s has no glyph(s) named %s"
                         % (args.set_name, ", ".join(missing)))

    out = args.out or (ROOT / "scratch" /
                       ("%s-%dpx.png" % (args.set_name, args.size)))
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="port-assets-sheet-") as tmp:
        tmpdir = Path(tmp)
        cells = []
        for name in names:
            cell = tmpdir / (name + ".png")
            rasterise(src_dir / (name + ".svg"), args.size, cell)
            cells.append(str(cell))
        rows = []
        for i, bg in enumerate(BACKGROUNDS):
            row = tmpdir / ("row%d.png" % i)
            subprocess.run(["magick", "montage", "-background", bg,
                            "-tile", "%dx1" % len(cells), "-geometry", "+2+2",
                            *cells, "PNG32:" + str(row)], check=True)
            rows.append(str(row))
        subprocess.run(["magick", *rows, "-append", "-filter", "point",
                        "-resize", "%d%%" % (args.zoom * 100),
                        "PNG32:" + str(out)], check=True)

    print("%s: %d glyph(s) at %dpx over %d background(s) -> %s"
          % (args.set_name, len(names), args.size, len(BACKGROUNDS), out))
    print("Look at it. A glyph you cannot tell from its neighbour here is a "
          "glyph the player cannot tell apart either.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
