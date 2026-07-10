#!/usr/bin/env python3
"""Validate a pokeemerald-expansion map layout's map.bin against the engine's real
walkability rules (see docs/MAP_DESIGN_GUIDE.md sections 1-2 for why this exists --
a naive collision-bit-only check missed a walkable-water bug that this script is
built to catch automatically, before it needs to be rediscovered by playtesting).

Checks:
  1. Walkable water -- cells whose metatile behavior (from the tileset's own
     metatile_attributes.bin, not a hand-written legend) marks them as
     surf-only water, but whose collision/elevation bits would let a grounded
     player walk onto them anyway (src/event_object_movement.c's
     IsElevationMismatchAt() elevation-wildcard rule).
  2. Passable perimeter cells outside known connection gaps -- walkable cells
     on an outer edge that has no `connections` entry in the owning map's
     map.json. Border.bin tiles infinitely beyond such an edge (see
     MAP_DESIGN_GUIDE.md section 4), so a walkable gap there is either a
     missing connection or an accidental hole in the perimeter wall.
  3. Metatile IDs not present in the legend -- "the legend" here is the
     layout's own tileset pair: an ID that doesn't correspond to any metatile
     actually defined in metatiles.bin (primary IDs 0..prim_count-1, secondary
     IDs 512..512+sec_count-1) reads garbage/undefined tile data in-engine.
     (tools/route1_metatile_legend.json is a curated, incomplete provenance
     record for one map's generator -- not a valid whitelist for arbitrary
     layouts, so it is deliberately not used as the source of truth here.)

Usage:
    python3 tools/check_map.py LAYOUT_ZEEGEM
    python3 tools/check_map.py LAYOUT_ZEEGEM LAYOUT_LAEKON_ROUTE1
Exits nonzero if any layout has violations, so it can gate commits.
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_map import (  # noqa: E402
    NUM_METATILES_IN_PRIMARY,
    load_layout,
    read_u16_grid,
    tileset_symbol_to_dir,
)

MAPS_DIR = REPO_ROOT / "data/maps"
BEHAVIORS_HEADER = REPO_ROOT / "include/constants/metatile_behaviors.h"

# Player elevation while grounded on land, per this hack's own documented
# convention (docs/MAP_DESIGN_GUIDE.md section 2, TECHNICAL_CONTEXT.md):
# land = 3, water = 1. Elevations 0 and 15 are engine-wide wildcards that
# never mismatch (include/global.fieldmap.h ELEVATION_TRANSITION / _MULTI_LEVEL).
LAND_ELEVATION = 3
WILDCARD_ELEVATIONS = (0, 15)

# direction string (map.json connections) -> which perimeter edge it opens.
DIRECTION_TO_EDGE = {"up": "north", "down": "south", "left": "west", "right": "east"}


def load_behavior_names() -> dict:
    text = BEHAVIORS_HEADER.read_text()
    names = re.findall(r"^\s*(MB_[A-Za-z0-9_]+|NUM_METATILE_BEHAVIORS)\s*,?\s*(?://.*)?$", text, re.M)
    return {name: i for i, name in enumerate(names)}


BEHAVIOR_NAMES = load_behavior_names()

# Behaviors that require Surf -- a grounded player must never be able to walk
# onto these. Excludes MB_PUDDLE, MB_SHALLOW_WATER (walkable by design) and the
# MB_BRIDGE_OVER_* family (bridges are supposed to be walkable over water).
SURF_ONLY_BEHAVIOR_NAMES = [
    "MB_POND_WATER", "MB_INTERIOR_DEEP_WATER", "MB_DEEP_WATER", "MB_WATERFALL",
    "MB_SOOTOPOLIS_DEEP_WATER", "MB_OCEAN_WATER",
    "MB_UNUSED_SOOTOPOLIS_DEEP_WATER", "MB_UNUSED_SOOTOPOLIS_DEEP_WATER_2",
    "MB_NO_SURFACING", "MB_SEAWEED", "MB_SEAWEED_NO_SURFACING",
    "MB_FAST_WATER", "MB_CYCLING_ROAD_WATER",
]
SURF_ONLY_BEHAVIORS = {BEHAVIOR_NAMES[n] for n in SURF_ONLY_BEHAVIOR_NAMES if n in BEHAVIOR_NAMES}


class TilesetAttrs:
    """Local metatile ID -> (behavior, count) for one primary or secondary tileset."""

    def __init__(self, tileset_dir: Path):
        metatiles_raw = (tileset_dir / "metatiles.bin").read_bytes()
        self.count = len(metatiles_raw) // 16
        attrs_raw = (tileset_dir / "metatile_attributes.bin").read_bytes()
        attrs = struct.unpack(f"<{len(attrs_raw) // 2}H", attrs_raw)
        self.behaviors = [a & 0x00FF for a in attrs]


def find_owning_map(layout_id: str):
    """Return (map_json_path, map_json_dict) for the map whose 'layout' is layout_id,
    or (None, None) if no map currently references it."""
    needle = f'"layout": "{layout_id}"'
    for map_json in MAPS_DIR.glob("*/map.json"):
        if needle in map_json.read_text():
            return map_json, json.loads(map_json.read_text())
    return None, None


def connected_edges(map_data: dict) -> set:
    edges = set()
    for conn in (map_data or {}).get("connections") or []:
        edge = DIRECTION_TO_EDGE.get(conn.get("direction"))
        if edge:
            edges.add(edge)
    return edges


def is_walkable(collision: int, elevation: int) -> bool:
    if collision != 0:
        return False
    if elevation in WILDCARD_ELEVATIONS:
        return True
    return elevation == LAND_ELEVATION


def check_layout(layout_id: str) -> list:
    """Returns a list of violation strings for the given layout id."""
    layout = load_layout(layout_id)
    width, height = layout["width"], layout["height"]

    map_path = REPO_ROOT / layout["blockdata_filepath"]
    raw_grid = read_u16_grid(map_path, width, height)

    primary_dir = tileset_symbol_to_dir(layout["primary_tileset"], "primary")
    secondary_dir = tileset_symbol_to_dir(layout["secondary_tileset"], "secondary")
    primary = TilesetAttrs(primary_dir)
    secondary = TilesetAttrs(secondary_dir)

    def behavior_of(metatile_id: int):
        if metatile_id < NUM_METATILES_IN_PRIMARY:
            return primary.behaviors[metatile_id] if metatile_id < primary.count else None
        local = metatile_id - NUM_METATILES_IN_PRIMARY
        return secondary.behaviors[local] if local < secondary.count else None

    def id_in_legend(metatile_id: int) -> bool:
        if metatile_id < NUM_METATILES_IN_PRIMARY:
            return metatile_id < primary.count
        return (metatile_id - NUM_METATILES_IN_PRIMARY) < secondary.count

    map_json_path, map_data = find_owning_map(layout_id)
    edges_with_connection = connected_edges(map_data)
    if map_data is None:
        print(f"  (no data/maps/*/map.json references {layout_id} -- treating all "
              f"perimeter edges as unconnected)")

    violations = []

    for y in range(height):
        for x in range(width):
            cell = int(raw_grid[y, x])
            metatile_id = cell & 0x03FF
            collision = (cell >> 10) & 0x3
            elevation = (cell >> 12) & 0xF

            if not id_in_legend(metatile_id):
                violations.append(
                    f"({x},{y}): metatile ID 0x{metatile_id:03x} not present in "
                    f"{layout['primary_tileset']}/{layout['secondary_tileset']} "
                    f"(primary has {primary.count}, secondary has {secondary.count})"
                )
                continue  # behavior lookup below would be meaningless for this cell

            behavior = behavior_of(metatile_id)
            if behavior in SURF_ONLY_BEHAVIORS and is_walkable(collision, elevation):
                behavior_name = next(n for n, v in BEHAVIOR_NAMES.items() if v == behavior)
                violations.append(
                    f"({x},{y}): walkable water -- metatile 0x{metatile_id:03x} has "
                    f"behavior {behavior_name} (surf-only) but collision={collision} "
                    f"elevation={elevation} lets a grounded player walk onto it"
                )

            on_edge = []
            if y == 0:
                on_edge.append("north")
            if y == height - 1:
                on_edge.append("south")
            if x == 0:
                on_edge.append("west")
            if x == width - 1:
                on_edge.append("east")
            for edge in on_edge:
                if edge not in edges_with_connection and is_walkable(collision, elevation):
                    violations.append(
                        f"({x},{y}): passable perimeter cell on unconnected {edge} edge "
                        f"(metatile 0x{metatile_id:03x}, collision={collision}, "
                        f"elevation={elevation}) -- no map.json connection covers this edge"
                    )

    return violations


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("layouts", nargs="+", help="Layout id(s), e.g. LAYOUT_ZEEGEM")
    args = parser.parse_args()

    any_violations = False
    for layout_id in args.layouts:
        print(f"=== {layout_id} ===")
        violations = check_layout(layout_id)
        if violations:
            any_violations = True
            for v in violations:
                print(f"  VIOLATION: {v}")
            print(f"  {len(violations)} violation(s)")
        else:
            print("  PASS -- no violations")

    sys.exit(1 if any_violations else 0)


if __name__ == "__main__":
    main()
