# CLAUDE.md — Laekon ROM Hack

Pokémon Emerald ROM hack built on **pokeemerald-expansion**: a Pokémon Ranger-themed
fangame set in the region of Laekon. Developer: Rémy (GitHub: maskedmimi).

## Read these first
- `docs/DESIGN_DOCUMENT.md` — game design, story, hierarchy. **Source of truth.**
  If a technical decision conflicts with it, flag the conflict — never silently work around it.
- `docs/CHARACTERS.md` — full cast (Morimorty, the Wardens, Mimi, challengers).
- `docs/NAMING_GUIDE.md` — town/title naming system. Use it when naming anything.
- `docs/TECHNICAL_CONTEXT.md` — environment details and file-location map.

## Canon quick reference (v3 — supersedes anything older you may find)
- Region: **Laekon**. Starter village: **Zeegem** (built). Capital: **Kroonveld**.
- Villain: **Morimorty** & **the Madkings** (NOT "Dante" / "Team Cipher" — old drafts).
- Corrupted Pokémon: **Shadow Pokémon** (NOT "Obscure"). Code identifiers use `SHADOW`.
- Ladder: Challenger → Ranger Second/First Class → Elite Ranger → Trial Champion → Heartwarden.
- Legendary: Mew — never caught, only recognized.

## Hard technical rules
1. This is **pokeemerald-expansion**, never vanilla pokeemerald.
2. All event scripting in **Poryscript** (`.pory`) — never raw `.s` script assembly.
3. Game text is **plain ASCII only** — no smart quotes, no em-dashes (assembler breaks).
4. Progression gating uses the Ranger star rank variable, not badge flags.
5. Existing tilesets only for now (custom tilesets deferred; porytiles bookmarked for later).
6. Any mechanic touching the player's Pokémon must consider the Partner Bond system.

## Build & test
- Build: `make -j$(nproc)` → `pokeemerald.gba`. Test in mGBA (user runs it, you cannot).
- Compiling ≠ working: after building, tell the user exactly what to verify in mGBA.
- Debug menu is enabled (`include/config/debug.h`, R+START in overworld).
  **Pre-release checklist item: revert `DEBUG_OVERWORLD_MENU` to `DISABLED_ON_RELEASE`.**

## Map tooling
- `tools/render_map.py <LAYOUT_NAME>` renders any layout's map.bin to a PNG in
  `tools/renders/` using real tileset graphics. **Always render and inspect your own
  output after editing map data.**
- map.bin format: little-endian u16 per cell — bits 0-9 metatile ID, 10-11 collision,
  12-15 elevation. Layout dims in `data/layouts/layouts.json`.
- Porymap may strip `"name_clone"` fields when saving
  `src/data/region_map/region_map_sections.json` — never commit that as a side effect.

## Workflow
- Small verifiable steps: one change → build → (user tests in mGBA) → commit.
- Branches: `master` is the working branch (solo project). Commit style:
  `[area] Short description` — e.g. `[map] Zeegem metadata`, `[script] Catch Ceremony intro`.
- Before large or multi-file changes, state the plan and files you'll touch.
- Stay in scope: pre-existing unrelated issues get reported, fixed only if asked,
  and committed separately.
- The user is a CS engineer but new to GBA decomp and git: give exact commands,
  explain pokeemerald-specific patterns, flag anything destructive before doing it.
- Open design questions live in `docs/DESIGN_DOCUMENT.md` → Open Questions:
  ask the user rather than deciding them.
