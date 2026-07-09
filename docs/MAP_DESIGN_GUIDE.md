# Map Design Guide
> Lessons from building LAYOUT_LAEKON_ROUTE1, the first from-scratch outdoor map in this hack.
> Written after Route 1 playtesting turned up a walkable-water bug and a broken map seam that
> an earlier "self-review" pass missed. CLAUDE.md points here (and at `tools/render_map.py`) as
> the map-tooling reference; note that CLAUDE.md's own `docs/TECHNICAL_CONTEXT.md` pointer does
> not currently exist in this repo -- worth creating or removing that reference separately.

This is not a tutorial on Porymap. It's a list of specific mistakes made while generating
Route 1 procedurally, why they happened, and the rule that would have caught each one --
so the next map (hand-drawn or generated) doesn't repeat them.

---

## 1. Decode vanilla maps first -- never invent a metatile ID

Every metatile ID, collision bit, and elevation value used for Route 1 was read out of a real,
already-working map.bin (Zeegem, Route101, Route104), never guessed from a tileset thumbnail or
a metatile label name. The workflow that worked:

1. Find an existing map using the same tileset pair that already has the feature you need
   (shoreline, ledge, tall grass, tree wall). `data/layouts/layouts.json` tells you the
   `primary_tileset`/`secondary_tileset` for every map -- match those, not just the biome.
2. Decode its `map.bin` directly (little-endian u16 per cell: bits 0-9 metatile ID, 10-11
   collision, 12-15 elevation -- see CLAUDE.md). Print the grid with collision and elevation
   alongside the ID, not just the ID.
3. Render the tileset itself (not just the map) to see what a candidate ID actually looks like
   in isolation, using `render_map.py`'s `Tileset`/`MapRenderer` classes directly. This caught a
   real mistake this round: `metatile_labels.h`'s official name for `0x121` is
   `SandPit_Center`, which sounds decorative, but Zeegem uses it as its everyday walkable ground.
   Names in that header describe the graphic, not necessarily the role a given hack uses it for.
4. Cross-check the SAME ID's usage in a second, independent map before trusting it. A single
   example can be misleading (see ELEVATION 1, below, and the tree tiles in section 6) --
   Route104 is what caught that Zeegem's water elevation, taken alone, could have been
   misread.
5. Save the legend as a JSON file (`tools/route1_metatile_legend.json` is the template) with a
   `source` field per entry pointing at which real map proved it. If you can't cite a source,
   don't ship the tile.

Write the generator (if using one) to *read* the legend, not hardcode IDs inline -- it forces
every tile choice through the same verification discipline, and a later correction (like the
elevation fix in section 2) becomes a one-line change instead of a find-and-replace across the
whole script.

---

## 2. A metatile's collision bit is not the traversability model -- the engine's is

The most serious bug this round: Route 1's water was walkable in-game. The generator's own
self-check said the map was fine, because that check only looked at the collision bit
(`collision == 0` => walkable), and pokeemerald's water tiles are *collision 0 by design* --
vanilla Route104 does this too. Collision alone was never going to catch it.

The real blocker is elevation. `src/event_object_movement.c`'s `IsElevationMismatchAt()` compares
the player's current elevation to the target tile's elevation and blocks the move if they
differ -- **except** it treats elevation `0` (`ELEVATION_TRANSITION`) and `15`
(`ELEVATION_MULTI_LEVEL`) as wildcards that never mismatch (`include/global.fieldmap.h`). Water
needs a real, specific, non-wildcard elevation (vanilla and this hack both use `1`, with land at
`3`) or the mismatch -- and the Surf prompt that depends on detecting it
(`field_player_avatar.c`) -- never fires.

**Rule:** before trusting any hand-rolled walkability check (BFS or otherwise), go read the
actual collision function in `src/event_object_movement.c` (`GetCollisionAtCoords` /
`GetVanillaCollision` / `IsElevationMismatchAt`) and make sure your model matches it -- collision
bit AND elevation-wildcard rule together. `tools/gen_route1.py`'s `is_walkable()` /
`verify_traversability()` now does this and is meant to be copied, not reinvented, for the next
map's generator.

This also means: **re-run the traversability check after every edit that touches elevation or
row layout**, not just once at the start. Shifting Route 1's shore down one row (section 3)
exposed a second, unrelated bug -- a bypass under the tall-grass gates -- that only showed up
once the corrected model was in place. The old, collision-only check had been silently
passing over both problems.

---

## 3. Connected edges are one shared terrain seam, not two independent edges

Once map A has a `connections` entry pointing at map B, the game draws A's edge column and B's
edge column right next to each other every time the player is near that boundary. Design them
as **one continuous strip of terrain**, at the same time, not as two separately-finished maps
that happen to touch.

Concretely, for Zeegem <-> Route 1 (offset 0, so row `y` in one lines up with row `y` in the
other):
- The shoreline had to start on the **same row** on both sides. Route 1's generated shore
  started one row further north than Zeegem's already-existing east-edge shore. The fix was to
  shift Route 1's shore to match Zeegem's established row, not the other way around -- the
  older, hand-authored map is the one whose shape is already committed to; the newer map
  conforms to it.
- The tree wall had to be visually and mechanically uniform across the seam (section 6).
- Water tiles at the boundary need to use a pairing that's already proven adjacent somewhere in
  the source data (see section 1) -- Zeegem's own shore corner tile was already shaped to open
  eastward into more water, which is exactly what Route 1 needed to continue into.

**Before calling a connected edge done, render both maps and crop a side-by-side strip of the
last N columns of one against the first N columns of the other** (see
`tools/renders/` for the workflow used here). Looking at each map alone will not catch a seam
mismatch -- both renders looked individually fine before this was caught.

---

## 4. Borders: a connection replaces the border on that side; the border block covers
   everything else

`src/fieldmap.c`'s `InitBackupMapLayoutConnections` overwrites the map buffer with the
connected map's real tiles for whichever directions have a `connections` entry
(`FillNorthConnection`/`South`/`East`/`West`). Any edge or corner *without* a connection falls
back to `GetBorderBlockAt`, which just tiles the small `border.bin` block (2x2 for this hack's
map format) infinitely outward.

Practical consequence: `border.bin` only needs to look right for the edges that have **no**
map neighbor. Zeegem's border.bin is 4x deep-water because its south edge is unconnected open
sea; Route 1 copied that same border for the same reason. Don't try to make border.bin "match"
a connected neighbor -- the connection data supersedes it there entirely, and time spent on that
is wasted.

---

## 5. Ledges only where they shortcut a real detour

A one-way ledge (`MB_JUMP_SOUTH` etc.) only means something if there's an actual barrier
alongside it forcing a detour -- otherwise the player can just walk around it through open
ground and the ledge is pure decoration. Route 1's ledge works because it sits in a rock
barrier that spans the full corridor width except for the ledge gap; walking around means
leaving the barrier's column range entirely, which costs real distance.

Before shipping a ledge, verify programmatically that:
- a walkable detour exists that doesn't use the ledge (it's a shortcut, not the only path), and
- the ledge doesn't create a one-way trap (check the area it drops into isn't sealed off with
  no way back around).

Both are cheap BFS checks (see `verify_traversability()`) and both are easy to get wrong by eye.

---

## 6. Tree walls: one tile type, used consistently, or the wall looks broken

The Dewford tileset's forest tiles are not interchangeable:
- `0x243` is a dense **interior** canopy tile with no visible trunk -- meant to be surrounded by
  more forest on multiple sides.
- `0x23a` and `0x239` both render a visible trunk/mound. `0x23a` is for a genuine
  forest-edge-to-open-ground boundary (used once, correctly, in Zeegem's diagonal NW corner);
  `0x239` is for a deliberately placed standalone tree sitting alone in a field.

Route 1 had `0x23a` planted as a "marker" tile inside an otherwise-solid `0x243` wall (to flag a
future exit), and Zeegem had two stray `0x23a`/`0x239` tiles left over inside its own dry-land
wall from before Route 1 existed. Both create a ragged look -- a trunk poking out of what should
read as a single unbroken mass of canopy -- exactly the kind of thing that's hard to notice by
eye at 100% zoom but obvious once you render at 4x and crop.

**Rule: a sealing wall is 100% one tile end to end.** If you need to mark something for a future
edit (like an exit position), do it in a code comment or a design doc, not with a visually
different tile buried in the wall.

Verify tree tiles the same way as any other metatile (section 1): render the ID alone, and
separately render it in the context of a real, already-shipped wall, before trusting what it
looks like from a tileset thumbnail or a behavior label.

---

## 7. Grass gates as organic blobs, not straight rows

Route 1's tall-grass gates are full-height rectangular bands. They work mechanically (verified:
impossible to cross without touching grass), but a straight vertical band reads as an obviously
artificial gate rather than a natural patch of grass that happens to block the way. Real Hoenn
routes shape grass patches as irregular clusters that still fully block the relevant choke point.
Next map: build gates as an organic blob (varying width per row, ragged edges) that still passes
the same "no bypass without touching grass" check -- the shape is cosmetic, the chokepoint
guarantee is not.

(Route 1's existing gates were left as straight bands rather than reshaped after the fact --
this is a lesson for the next map, not a retroactive fix.)

---

## 8. Render, inspect, iterate -- every time, not just at the end

Every fix in this round was found or verified by rendering and cropping, not by reading map.bin
dumps alone:
- The tree-tile role confusion (section 6) was only clear once actual rendered pixels were
  compared against the tileset thumbnail -- the two did not agree with a first guess.
- The seam mismatch (section 3) was only visible in a side-by-side crop of both maps' edge
  columns -- neither map's own full render showed a problem in isolation.
- The gate bypass (section 2) was only caught because the traversability model was re-run
  after the shore-row shift, not assumed still valid from before.

Treat `python3 tools/render_map.py <LAYOUT> -o tools/renders/<LAYOUT>.png --scale 4` plus a crop
of anything that changed as a mandatory step after *any* map.bin edit, generated or hand-drawn --
not an optional nice-to-have at the end. A build succeeding and a traversability check passing
are necessary but not sufficient; they don't catch a wrong tile choice or a visual seam at all.
