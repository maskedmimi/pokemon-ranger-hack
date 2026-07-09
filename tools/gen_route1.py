#!/usr/bin/env python3
"""Generate a first-draft map.bin/border.bin for LAYOUT_ROUTE1 (Tidal Reach coastal
route east of Zeegem). Every metatile used here is defined in
tools/route1_metatile_legend.json, itself copied verbatim (ID, collision, elevation)
from Zeegem's own map data and Route101 (shared gTileset_General primary).

Usage:
    python3 tools/gen_route1.py
Writes data/layouts/LaekonRoute1/map.bin and data/layouts/LaekonRoute1/border.bin.
"""
import json
import struct
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEGEND = json.loads((REPO_ROOT / "tools/route1_metatile_legend.json").read_text())
OUT_DIR = REPO_ROOT / "data/layouts/LaekonRoute1"

WIDTH, HEIGHT = 40, 20


def tile(name):
    for group in LEGEND.values():
        if isinstance(group, dict) and name in group:
            e = group[name]
            return int(e["id"], 16), e["collision"], e["elevation"]
    raise KeyError(name)


GRASS = tile("GRASS")
TALL_GRASS = tile("TALL_GRASS")
SAND_PATH = tile("SAND_PATH")
CLEARING = tile("CLEARING")
TREE_WALL = tile("TREE_WALL")
TREE_EDGE = tile("TREE_EDGE")
TREE_SOLO = tile("TREE_SOLO")
ROCK = tile("ROCK")
LEDGE_CAP_LEFT = tile("LEDGE_CAP_LEFT")
LEDGE_HOP = tile("LEDGE_HOP")
LEDGE_CAP_RIGHT = tile("LEDGE_CAP_RIGHT")
SHORE_CORNER_L = tile("SHORE_CORNER_L")
SHORE_FILL = tile("SHORE_FILL")
SHORE_CORNER_R = tile("SHORE_CORNER_R")
SHORE_STEP_L = tile("SHORE_STEP_L")
SHORE_STEP_R = tile("SHORE_STEP_R")
SEA = tile("SEA")

# Cove spans: (corner_left_x, corner_right_x). Interior columns between the corners
# get the shore pulled one row further north (a bay); columns outside are baseline.
COVES = [(8, 14), (26, 32)]

FIELD_TOP = 2       # first field row (rows 0-1 are the north tree wall)
FIELD_BOTTOM = 14    # last field row before the shore band begins
BASELINE_EDGE_Y = 16  # baseline shore-fill row
COVE_EDGE_Y = 15      # shore-fill row inside a cove (one north of baseline)

grid = [[GRASS for _ in range(WIDTH)] for _ in range(HEIGHT)]


def set_tile(x, y, t):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        grid[y][x] = t


def in_cove(x):
    for l, r in COVES:
        if l < x < r:
            return True
    return False


def cove_corner(x):
    """Return 'L', 'R', or None if x is a cove transition column."""
    for l, r in COVES:
        if x == l:
            return "L"
        if x == r:
            return "R"
    return None


# ---- 1. Shoreline (rows FIELD_BOTTOM+1 .. HEIGHT-1) ----
for x in range(WIDTH):
    corner = cove_corner(x)
    cove = in_cove(x)
    if corner == "L":
        set_tile(x, COVE_EDGE_Y, SHORE_CORNER_L)
        set_tile(x, COVE_EDGE_Y + 1, SHORE_STEP_L)
        for y in range(COVE_EDGE_Y + 2, HEIGHT):
            set_tile(x, y, SEA)
    elif corner == "R":
        set_tile(x, COVE_EDGE_Y, SHORE_CORNER_R)
        set_tile(x, COVE_EDGE_Y + 1, SHORE_STEP_R)
        for y in range(COVE_EDGE_Y + 2, HEIGHT):
            set_tile(x, y, SEA)
    elif cove:
        set_tile(x, COVE_EDGE_Y, SHORE_FILL)
        for y in range(COVE_EDGE_Y + 1, HEIGHT):
            set_tile(x, y, SEA)
    else:
        # baseline: land at COVE_EDGE_Y, shore fill at BASELINE_EDGE_Y, sea below
        set_tile(x, COVE_EDGE_Y, GRASS)
        set_tile(x, BASELINE_EDGE_Y, SHORE_FILL)
        for y in range(BASELINE_EDGE_Y + 1, HEIGHT):
            set_tile(x, y, SEA)

# ---- 2. North tree wall ----
for x in range(WIDTH):
    set_tile(x, 0, TREE_WALL)
    set_tile(x, 1, TREE_WALL)

# ---- 3. Path spine: winding sand ribbon, width 3, from the west entrance to the
#         east gap. Control points (x, center_y); linearly interpolated between. ----
CONTROL_POINTS = [
    (0, 9), (6, 9), (10, 7), (14, 6), (19, 7), (21, 9),
    (25, 11), (29, 12), (33, 9), (37, 8), (39, 9),
]


def path_center_y(x):
    for (x0, y0), (x1, y1) in zip(CONTROL_POINTS, CONTROL_POINTS[1:]):
        if x0 <= x <= x1:
            if x1 == x0:
                return y0
            t = (x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * t
    return CONTROL_POINTS[-1][1]


for x in range(WIDTH):
    cy = round(path_center_y(x))
    for y in range(cy - 1, cy + 2):
        if FIELD_TOP <= y <= FIELD_BOTTOM:
            set_tile(x, y, SAND_PATH)

# ---- 4. Tall grass gates: full-height bands, applied after the path so the path
#         itself visibly enters the grass (grass gates it, not decorative). ----
GATE_COLUMNS = [(11, 12), (29, 30)]
for x0, x1 in GATE_COLUMNS:
    for x in range(x0, x1 + 1):
        for y in range(FIELD_TOP, FIELD_BOTTOM + 1):
            set_tile(x, y, TALL_GRASS)

# ---- 5. Ledge shortcut: a rock barrier across the corridor at row 9, columns
#         19-27, with a single one-way hop-south gap at 21-25. Eastbound travelers
#         can hop straight down to the row-10+ band; westbound must detour around
#         the barrier's ends (x<19 or x>27) since MB_JUMP_SOUTH is one-directional. ----
LEDGE_ROW = 9
BARRIER_X0, BARRIER_X1 = 19, 27
LEDGE_CAP_L_X, LEDGE_HOP_X0, LEDGE_HOP_X1, LEDGE_CAP_R_X = 21, 22, 24, 25
for x in range(BARRIER_X0, BARRIER_X1 + 1):
    if x == LEDGE_CAP_L_X:
        set_tile(x, LEDGE_ROW, LEDGE_CAP_LEFT)
    elif LEDGE_HOP_X0 <= x <= LEDGE_HOP_X1:
        set_tile(x, LEDGE_ROW, LEDGE_HOP)
    elif x == LEDGE_CAP_R_X:
        set_tile(x, LEDGE_ROW, LEDGE_CAP_RIGHT)
    else:
        set_tile(x, LEDGE_ROW, ROCK)

# ---- 6. Rest-spot clearing: a small off-path pocket near the entrance. ----
for x in range(4, 7):
    for y in range(3, 6):
        if grid[y][x] == GRASS:
            set_tile(x, y, CLEARING)

# ---- 7. Scattered decoration: solo trees and rocks, off-path, only placed over
#         plain grass so nothing already placed (path/gate/ledge/shore) is clobbered. ----
SOLO_TREES = [(3, 3), (9, 13), (23, 3), (31, 13), (36, 3)]
for x, y in SOLO_TREES:
    if grid[y][x] == GRASS:
        set_tile(x, y, TREE_SOLO)
    else:
        print(f"skip solo tree at ({x},{y}): occupied by {grid[y][x]}")

SCATTERED_ROCKS = [(16, 3), (24, 4), (35, 12), (6, 13), (37, 5)]
for x, y in SCATTERED_ROCKS:
    if grid[y][x] == GRASS:
        set_tile(x, y, ROCK)
    else:
        print(f"skip rock at ({x},{y}): occupied by {grid[y][x]}")

# ---- 8. West/east edge seals -- applied LAST so they always win over the path,
#          which otherwise runs right through column 0/39. West edge open only at
#          y=9,10 (Zeegem's east exit gap, offset 0). East edge fully sealed; y=9,10
#          marked with TREE_EDGE instead of TREE_WALL as a visually distinct spot to
#          carve open once a future Route2 exists east of here -- still solid for now. ----
for y in range(HEIGHT):
    if y not in (9, 10):
        set_tile(0, y, TREE_WALL)

for y in range(HEIGHT):
    if y in (9, 10):
        set_tile(WIDTH - 1, y, TREE_EDGE)  # FUTURE EXIT: carve this 2-tile gap open when Route2 exists
    else:
        set_tile(WIDTH - 1, y, TREE_WALL)


def pack(t):
    mt, collision, elevation = t
    return (mt & 0x3FF) | ((collision & 0x3) << 10) | ((elevation & 0xF) << 12)


def write_map():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "map.bin", "wb") as f:
        for y in range(HEIGHT):
            for x in range(WIDTH):
                f.write(struct.pack("<H", pack(grid[y][x])))
    # Border: match Zeegem's own border.bin (4x SEA) so the horizon beyond the
    # coastline reads as more open water.
    with open(OUT_DIR / "border.bin", "wb") as f:
        for _ in range(4):
            f.write(struct.pack("<H", pack(SEA)))
    print(f"wrote {OUT_DIR / 'map.bin'} ({WIDTH}x{HEIGHT}) and border.bin")


if __name__ == "__main__":
    write_map()
