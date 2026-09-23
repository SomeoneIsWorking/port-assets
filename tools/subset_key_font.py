#!/usr/bin/env python3
"""Make fonts/NotoSans-Bold-keys.ttf, the keyboard set's own typeface.

A key's label used to name "DejaVu Sans,Verdana,sans-serif" and take whatever
the rasterising host had: this set's letters looked different on every machine
that drew them, and a consumer lettering a key at RUNTIME -- a game whose key
names are localized, so no label can be drawn ahead of time -- had no font to
letter it with at all. The typeface now ships here, subset to the scripts key
names are written in.

    python3 tools/subset_key_font.py /path/to/NotoSans-Bold.ttf

The source is Noto Sans Bold 2.015 (SIL Open Font License 1.1, fonts/OFL.txt),
checked by digest so the committed subset is reproducible.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "fonts" / "NotoSans-Bold-keys.ttf"
SOURCE_SHA256 = "1df075a380fc7cb898acf64c1f7b3b4dd780de3caa860178bf929de35817a913"
# Basic Latin, Latin-1, Latin Extended-A, Greek, Cyrillic, general punctuation.
UNICODES = "U+0020-007E,U+00A0-017F,U+0370-03FF,U+0400-04FF,U+2010-2027"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    digest = hashlib.sha256(args.source.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        print(f"subset_key_font: {args.source} is not Noto Sans Bold 2.015 "
              f"(sha256 {digest}); refusing to change the set's typeface",
              file=sys.stderr)
        return 1
    from fontTools import subset
    subset.main([str(args.source), f"--unicodes={UNICODES}",
                 "--layout-features=kern,liga,locl", "--no-hinting",
                 "--drop-tables+=DSIG", f"--output-file={OUT}"])
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
