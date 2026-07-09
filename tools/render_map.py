#!/usr/bin/env python3
"""Render a pokeemerald-expansion map layout to a PNG using real tileset graphics.

Reads a layout's map.bin/border.bin (data/layouts/<Name>/) together with its
primary and secondary tileset's tiles.png, palettes/*.pal and metatiles.bin,
and composites the actual in-game tile graphics into a PNG.

Usage:
    python3 tools/render_map.py LAYOUT_ZEEGEM
    python3 tools/render_map.py LAYOUT_ZEEGEM -o tools/renders/zeegem.png --scale 4
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
LAYOUTS_JSON = REPO_ROOT / "data/layouts/layouts.json"
RENDERS_DIR = REPO_ROOT / "tools/renders"

# GBA BG screen-entry bit layout, used verbatim by metatiles.bin tile entries.
TILE_ID_MASK = 0x03FF
TILE_HFLIP = 0x0400
TILE_VFLIP = 0x0800
TILE_PALETTE_SHIFT = 12

NUM_TILES_IN_PRIMARY = 512
NUM_METATILES_IN_PRIMARY = 512
NUM_PALS_IN_PRIMARY = 6

TILE_SIZE = 8
METATILE_SIZE = TILE_SIZE * 2  # 2x2 tiles per layer -> 16x16px
DEFAULT_BORDER_DIM = 2


def camel_to_dir(symbol: str) -> str:
    """"DewfordGym" -> "dewford_gym", matching data/tilesets/*/<dir> naming."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", symbol).lower()


def tileset_symbol_to_dir(symbol: str, kind: str) -> Path:
    prefix = "gTileset_"
    if not symbol.startswith(prefix):
        raise SystemExit(f"Unrecognized tileset symbol: {symbol!r}")
    dirname = camel_to_dir(symbol[len(prefix):])
    path = REPO_ROOT / "data/tilesets" / kind / dirname
    if not path.is_dir():
        raise SystemExit(f"Could not find {kind} tileset directory for {symbol!r} (tried {path})")
    return path


def load_layout(layout_id: str) -> dict:
    data = json.loads(LAYOUTS_JSON.read_text())
    for layout in data["layouts"]:
        if layout["id"] == layout_id:
            return layout
    raise SystemExit(f"Layout {layout_id!r} not found in {LAYOUTS_JSON}")


def read_u16_grid(path: Path, width: int, height: int):
    raw = path.read_bytes()
    count = width * height
    return np.array(struct.unpack(f"<{count}H", raw[:count * 2]), dtype=np.uint16).reshape(height, width)


def load_pal(path: Path):
    lines = path.read_text().splitlines()
    count = int(lines[2])
    colors = [tuple(int(c) for c in line.split()) for line in lines[3:3 + count]]
    return np.array(colors, dtype=np.uint8)


class Tileset:
    def __init__(self, tileset_dir: Path):
        self.dir = tileset_dir
        im = Image.open(tileset_dir / "tiles.png")
        if im.mode != "P":
            raise SystemExit(f"Expected indexed (mode P) PNG at {tileset_dir / 'tiles.png'}, got {im.mode}")
        self.tile_indices = np.array(im)  # raw 4bpp palette indices (0-15) per pixel
        self.tiles_per_row = self.tile_indices.shape[1] // TILE_SIZE

        metatiles_raw = (tileset_dir / "metatiles.bin").read_bytes()
        num_metatiles = len(metatiles_raw) // 16
        self.metatiles = np.frombuffer(metatiles_raw, dtype="<u2").reshape(num_metatiles, 8)

        self.palettes = {}
        for pal_file in (tileset_dir / "palettes").glob("*.pal"):
            self.palettes[int(pal_file.stem)] = load_pal(pal_file)

    def get_tile_block(self, local_tile_id: int):
        row, col = divmod(local_tile_id, self.tiles_per_row)
        y0, x0 = row * TILE_SIZE, col * TILE_SIZE
        return self.tile_indices[y0:y0 + TILE_SIZE, x0:x0 + TILE_SIZE]


class MapRenderer:
    def __init__(self, primary: Tileset, secondary: Tileset):
        self.primary = primary
        self.secondary = secondary
        self.backdrop = tuple(int(c) for c in primary.palettes[0][0])

    def get_metatile_entries(self, metatile_id: int):
        if metatile_id < NUM_METATILES_IN_PRIMARY:
            return self.primary.metatiles[metatile_id]
        return self.secondary.metatiles[metatile_id - NUM_METATILES_IN_PRIMARY]

    def get_tile_block(self, tile_id: int):
        if tile_id < NUM_TILES_IN_PRIMARY:
            return self.primary.get_tile_block(tile_id)
        return self.secondary.get_tile_block(tile_id - NUM_TILES_IN_PRIMARY)

    def get_palette(self, pal_num: int):
        tileset = self.primary if pal_num < NUM_PALS_IN_PRIMARY else self.secondary
        return tileset.palettes[pal_num]

    def draw_metatile(self, canvas: np.ndarray, px: int, py: int, metatile_id: int):
        entries = self.get_metatile_entries(int(metatile_id))
        for layer, layer_entries in enumerate((entries[0:4], entries[4:8])):
            is_top_layer = layer == 1
            for i, entry in enumerate(layer_entries):
                entry = int(entry)
                tile_id = entry & TILE_ID_MASK
                hflip = bool(entry & TILE_HFLIP)
                vflip = bool(entry & TILE_VFLIP)
                pal_num = (entry >> TILE_PALETTE_SHIFT) & 0xF

                idx_block = self.get_tile_block(tile_id)
                if hflip:
                    idx_block = idx_block[:, ::-1]
                if vflip:
                    idx_block = idx_block[::-1, :]

                palette = self.get_palette(pal_num)
                rgb_block = palette[idx_block]

                dx, dy = (i % 2) * TILE_SIZE, (i // 2) * TILE_SIZE
                ox, oy = px + dx, py + dy
                region = canvas[oy:oy + TILE_SIZE, ox:ox + TILE_SIZE]
                transparent = idx_block == 0
                if is_top_layer:
                    region[~transparent] = rgb_block[~transparent]
                else:
                    rgb_block = rgb_block.copy()
                    rgb_block[transparent] = self.backdrop
                    region[:] = rgb_block


def render_layout(layout_id: str, scale: int, border_margin: int) -> Image.Image:
    layout = load_layout(layout_id)
    width, height = layout["width"], layout["height"]
    border_width = layout.get("border_width", DEFAULT_BORDER_DIM)
    border_height = layout.get("border_height", DEFAULT_BORDER_DIM)

    map_path = REPO_ROOT / layout["blockdata_filepath"]
    border_path = REPO_ROOT / layout["border_filepath"]
    map_grid = read_u16_grid(map_path, width, height) & 0x03FF  # strip collision/elevation bits
    border_grid = read_u16_grid(border_path, border_width, border_height) & 0x03FF

    primary = Tileset(tileset_symbol_to_dir(layout["primary_tileset"], "primary"))
    secondary = Tileset(tileset_symbol_to_dir(layout["secondary_tileset"], "secondary"))
    renderer = MapRenderer(primary, secondary)

    margin = max(border_margin, 0)
    total_w = (width + 2 * margin) * METATILE_SIZE
    total_h = (height + 2 * margin) * METATILE_SIZE
    canvas = np.zeros((total_h, total_w, 3), dtype=np.uint8)

    for gy in range(-margin, height + margin):
        for gx in range(-margin, width + margin):
            if 0 <= gx < width and 0 <= gy < height:
                metatile_id = map_grid[gy, gx]
            else:
                metatile_id = border_grid[gy % border_height, gx % border_width]
            px = (gx + margin) * METATILE_SIZE
            py = (gy + margin) * METATILE_SIZE
            renderer.draw_metatile(canvas, px, py, metatile_id)

    image = Image.fromarray(canvas)
    if scale != 1:
        image = image.resize((total_w * scale, total_h * scale), Image.NEAREST)
    return image, (width, height)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("layout", help="Layout id, e.g. LAYOUT_ZEEGEM")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output PNG path (default: tools/renders/<layout>.png)")
    parser.add_argument("--scale", type=int, default=2, help="Integer upscale factor for visibility (default: 2)")
    parser.add_argument("--border-margin", type=int, default=2, help="Metatiles of border padding to render around the map (default: 2, use 0 to disable)")
    args = parser.parse_args()

    image, (width, height) = render_layout(args.layout, args.scale, args.border_margin)

    output = args.output or (RENDERS_DIR / f"{args.layout}.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(f"Rendered {args.layout} ({width}x{height} metatiles) -> {output} ({image.width}x{image.height}px)")


if __name__ == "__main__":
    main()
