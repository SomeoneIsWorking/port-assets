# port-assets

The art every game port in this tree keeps redrawing, in one place instead of
one copy per project.

Everything here is **SVG** and scales; nothing is authored at a pixel size.
What varies between consumers is the cell they rasterise into, and that ranges
from a 2005 font atlas's 18x18 to a modern HUD badge, so the sets are drawn
once in a 72-unit box and checked at the smallest size anything ships them at.

| Set | What it is |
|---|---|
| `sets/gamepad-xbox360` | Xbox 360 controller glyphs — face buttons, bumpers, triggers, d-pad (neutral **and one per direction**), sticks (click and each direction), Start/Back/Guide. |
| `sets/keyboard` | Key caps. The **label is not baked in** — the consumer composites the key that is actually bound, so a rebind changes the prompt with no new asset. Taken from zelda3d, which is why it is here rather than in that project. |

## Using it from a project

```python
import port_assets
port_assets.sets()                             # ['gamepad-xbox360', 'keyboard']
port_assets.names('gamepad-xbox360')           # every glyph, checked against the files
port_assets.path('gamepad-xbox360', 'dpad_up') # -> .../dpad_up.svg
python3 tools/draw_keyboard.py --label ENTER   # a labelled cap, to stdout
```

`resolve()` looks at `$PORT_ASSETS_DIR`, then `$SHARED_DIR/port-assets`, then
the sibling checkout the standard `shared/` layout implies, and **refuses by
naming every path it tried** rather than falling back to an in-tree copy. A
stale vendored copy that silently wins is the failure this split exists to end.

`names()` refuses a set whose manifest and files disagree in either direction.
A consumer that publishes ten of eleven glyphs draws a blank for one prompt and
looks like a game bug.

## The design rules, and why each one is here

Every one of these was learned by rasterising something that looked fine at
72x72 and was useless at 18x18. **Look at `tools/sheet.py` output before
accepting a glyph** — over a light, a dark and a mid-tone background, zoomed
with a point filter so the pixels are the pixels.

- **Light fill, dark outline.** On a dark HUD panel the fill carries the shape;
  on a bright scene the outline does. A mark drawn in the outline's own colour
  vanishes into a dark background while reading perfectly on a light one.
- **Name the thing, do not recolour it.** `LB` and `RB` and `LT` and `RT` all
  say so in two letters. An earlier set drew a single `R` and distinguished
  bumper from trigger by *inverting the fill*; the report that killed it was
  "the button says R but is it RB or RT?". Inverted colour is not a cue a
  player can act on.
- **Give the same family different silhouettes as well.** A bumper is the flat
  bar across the top of the pad; a trigger is the paddle underneath. When two
  small letters blur, the outline is what is left.
- **A direction is shown by lighting the arm, not by an interior mark.** The
  d-pad's named arm is filled; the stick's named direction hangs a solid wedge
  off the cap. Measured alternatives that failed at 18x18: an arm inset to keep
  a rim (a 2-pixel dot), an arrowhead drawn inside the arm (invisible), the cap
  nudged off-centre inside a travel ring (four identical circles).
- **One glyph per meaning.** The d-pad had a single unlit cross for all four
  directions once, and a screen offering four d-pad choices drew the same
  picture four times — strictly less than the `[UP] [LEFT]` text it replaced.
  `tests/test_sets.py` now fails if two members of a direction family
  rasterise identically.

## Checking a change

```sh
python3 tests/test_sets.py                        # every set; ctest-style, 77 = SKIP
python3 tools/sheet.py gamepad-xbox360            # look at it at 18px
python3 tools/sheet.py gamepad-xbox360 --size 48  # and at a HUD size
python3 tools/draw_xbox360.py --check             # the SVGs match their author script
```

The `draw_*.py` scripts author the sets and the SVGs are **checked in** — a
consumer never needs them. They exist so the set stays internally consistent
as it grows: one place holds the palette, the stroke weights and the geometry,
so a glyph added next year matches the ones drawn today instead of being
eyeballed against them. `--check` is the ratchet that keeps the two in step.

## Licence and what the art is not

MIT — see `LICENSE`. **Every glyph here is drawn from scratch**, in
`tools/draw_*.py`, and no console manufacturer's art is copied, traced or
shipped. That is deliberate and it is the reason the sets exist: the obvious
source for button prompts is a console build's own font atlas, and using one
means asking the player to own that build. The shapes here are the generic
public forms of the controls (a cross, a bar, a paddle, a lettered disc), not
anyone's assets.

`sets/keyboard` follows the design used in zelda3d.

## Adding a set

A directory under `sets/`, a `set.json` declaring its glyphs, and an entry in
`FAMILIES` in the selftest for any group a player must tell apart. If it is
authored by a script, add the script and wire its `--check`.
