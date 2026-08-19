#!/usr/bin/env python3
"""Selftest: every set is complete, and every glyph SURVIVES ITS TARGET SIZE.

The second half is the one that matters. An SVG that parses, has a manifest
entry and rasterises to a file can still be a blank cell or an unreadable smear
at the size it actually ships at, and every defect this repo has had so far was
exactly that. So the check rasterises at the smallest size any consumer uses
and requires each glyph to have real ink -- and requires the members of a
DIRECTION FAMILY to differ from each other, because the worst bug in the set's
history was four d-pad directions that all drew the same picture.

    python3 tests/test_sets.py
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import port_assets                                              # noqa: E402

SMALLEST = 18          # xmen2's font-atlas cell; the tightest consumer so far
MIN_INK = 0.04         # fraction of the cell that must be opaque

# Sets of glyphs that a player must be able to TELL APART. Membership is
# spelled out rather than derived from the names, so adding a family is a
# deliberate act and a typo cannot silently empty one.
FAMILIES = {
    "gamepad-xbox360": [
        ["dpad_up", "dpad_down", "dpad_left", "dpad_right"],
        ["lb", "rb", "lt", "rt"],
        ["face_a", "face_b", "face_x", "face_y"],
        ["ls_up", "ls_down", "ls_left", "ls_right"],
        ["rs_up", "rs_down", "rs_left", "rs_right"],
    ],
}


def cells(paths: dict[str, Path], size: int, tmp: Path) -> dict[str, bytes]:
    out = {}
    for name, src in paths.items():
        dst = tmp / (name + ".rgba")
        run = subprocess.run(
            ["magick", "-background", "none", str(src),
             "-resize", "%dx%d" % (size, size),
             "-gravity", "center", "-extent", "%dx%d" % (size, size),
             "-depth", "8", "RGBA:" + str(dst)], capture_output=True)
        if run.returncode or not dst.is_file():
            raise SystemExit("test_sets: %s failed to rasterise: %s"
                             % (src, run.stderr.decode()[:200]))
        out[name] = dst.read_bytes()
    return out


def main() -> int:
    if not shutil.which("magick"):
        print("test_sets: SKIP -- ImageMagick's `magick` is not on PATH, so "
              "NOTHING was rasterised and no glyph was checked at its target "
              "size. The manifest checks below did not run either.")
        return 77                       # ctest SKIP

    failures = []
    checked = 0
    for set_name in port_assets.sets():
        glyphs = port_assets.names(set_name)
        if not glyphs:
            failures.append("%s declares no glyphs at all" % set_name)
            continue
        paths = {g: port_assets.path(set_name, g) for g in glyphs}
        with tempfile.TemporaryDirectory(prefix="port-assets-test-") as tmp:
            raster = cells(paths, SMALLEST, Path(tmp))

        for name, px in raster.items():
            checked += 1
            opaque = sum(1 for i in range(0, len(px), 4) if px[i + 3] > 32)
            frac = opaque / float(SMALLEST * SMALLEST)
            if frac < MIN_INK:
                failures.append(
                    "%s/%s is %.1f%% ink at %dpx -- it would publish as a "
                    "blank prompt" % (set_name, name, frac * 100, SMALLEST))

        for family in FAMILIES.get(set_name, []):
            absent = [g for g in family if g not in raster]
            if absent:
                failures.append("%s: family %s names missing glyph(s) %s"
                                % (set_name, family, absent))
                continue
            for i, a in enumerate(family):
                for b in family[i + 1:]:
                    if raster[a] == raster[b]:
                        failures.append(
                            "%s: %s and %s rasterise IDENTICALLY at %dpx -- a "
                            "prompt cannot say which one it means"
                            % (set_name, a, b, SMALLEST))

    print("test_sets: %d set(s), %d glyph(s) rasterised at %dpx, %d family "
          "distinctness check(s)"
          % (len(port_assets.sets()), checked, SMALLEST,
             sum(len(f) * (len(f) - 1) // 2
                 for fs in FAMILIES.values() for f in fs)))
    if failures:
        for f in failures:
            print("  FAIL " + f, file=sys.stderr)
        return 1
    print("test_sets: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
