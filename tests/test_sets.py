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
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
SCRATCH = ROOT / "scratch"
sys.path.insert(0, str(ROOT))

import port_assets                                              # noqa: E402

SMALLEST = 18          # xmen2's font-atlas cell; the tightest consumer so far
MIN_INK = 0.04         # fraction of the cell that must be opaque
FONT_INDEPENDENT_SETS = {"gamepad-xbox360"}

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


def live_text_nodes(path: Path) -> int:
    """Count SVG text nodes, including namespaced spellings such as svg:text."""
    root = ElementTree.parse(path).getroot()
    return sum(1 for node in root.iter()
               if isinstance(node.tag, str)
               and node.tag.rsplit("}", 1)[-1] == "text")


def main() -> int:
    failures = []
    resolved = {}
    path_only_checked = 0
    set_names = port_assets.sets()
    for set_name in set_names:
        glyphs = port_assets.names(set_name)
        if not glyphs:
            failures.append("%s declares no glyphs at all" % set_name)
            continue
        paths = {g: port_assets.path(set_name, g) for g in glyphs}
        resolved[set_name] = paths
        if set_name not in FONT_INDEPENDENT_SETS:
            continue
        for name, path in paths.items():
            try:
                count = live_text_nodes(path)
            except ElementTree.ParseError as exc:
                failures.append("%s/%s is malformed SVG: %s"
                                % (set_name, name, exc))
                continue
            path_only_checked += 1
            if count:
                failures.append(
                    "%s/%s contains %d live SVG text node(s) -- its pixels "
                    "would depend on the fonts installed on the host"
                    % (set_name, name, count))

    if not shutil.which("magick"):
        if failures:
            for failure in failures:
                print("  FAIL " + failure, file=sys.stderr)
            return 1
        print("test_sets: SKIP -- ImageMagick's `magick` is not on PATH, so "
              "nothing was rasterised at its target size. Manifest and "
              "path-only checks passed for %d glyph(s)." % path_only_checked)
        return 77                       # ctest SKIP

    checked = 0
    SCRATCH.mkdir(parents=True, exist_ok=True)
    for set_name, paths in resolved.items():
        with tempfile.TemporaryDirectory(prefix="port-assets-test-",
                                         dir=SCRATCH) as tmp:
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
          "distinctness check(s), %d path-only glyph check(s)"
          % (len(set_names), checked, SMALLEST,
             sum(len(f) * (len(f) - 1) // 2
                 for fs in FAMILIES.values() for f in fs),
             path_only_checked))
    if failures:
        for f in failures:
            print("  FAIL " + f, file=sys.stderr)
        return 1
    print("test_sets: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
