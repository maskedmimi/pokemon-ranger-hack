# Technical Development Context
> Laekon ROM Hack — Developer Reference
> Last updated: July 2026 (v2 — full rewrite: current environment, tooling, and conventions)

Read this alongside `DESIGN_DOCUMENT.md` before any development work. `CLAUDE.md` (repo root) is the condensed session brief; this file is the full reference.

---

## Engine — pokeemerald-expansion

Built on **pokeemerald-expansion** (RHH community), NOT vanilla pokeemerald.
- Repo: https://github.com/rh-hideout/pokeemerald-expansion
- Provides all 1025+ species, modern battle mechanics, QoL features
- Not link-compatible with official GBA games (acceptable)
- **Credit "RHH (Rom Hacking Hideout)" on release**
- The expansion also carries FRLG/Kanto content — beware name collisions
  (e.g. `MAP_ROUTE1` is Kanto's; Laekon maps use the `LAEKON_` prefix)

## Terminology in code

- Corrupted Pokémon are **Shadow Pokémon** — all identifiers use `SHADOW`
  (never `OBSCURE`, which appears in old design drafts)
- Region: Laekon. Progression variable: Ranger star rank 0–3
  (0 Challenger, 1 Second Class, 2 First Class, 3 Elite) — rank gates
  map access and NPC interactions, never badge flags

---

## Environment (current, working)

- **WSL2 / Ubuntu 24.04** on Windows. Repo: `~/pokemon-ranger-hack`
  (Windows view: `\\wsl.localhost\Ubuntu-24.04\root\pokemon-ranger-hack`)
- Toolchain: devkitPro gba-dev + agbcc (pret), build-essential, libpng-dev.
  Note: the official devkitPro installer had 403 issues; the community
  installer (tristangnl/devkitPro-Debian-based-systems-installer) worked.
- **VS Code opened WSL-native**: `code .` from the Ubuntu terminal, with the
  Microsoft WSL extension installed; window must show "WSL: Ubuntu-24.04".
  Never open the repo via the Windows path — Windows-side sessions cause
  `wsl.exe` wrapping, git `safe.directory` friction, and permission spam.
  If `code .` throws "Exec format error", WSL interop is asleep: run
  `wsl --shutdown` in **PowerShell** (Windows side), reopen Ubuntu.
- **Claude Code**: runs in the WSL VS Code window. Reads `CLAUDE.md` at repo
  root automatically. Project permissions live in `.claude/settings.json`
  (gitignored): allow-list for make/python3/git, deny for `rm -rf` and sudo.
- Git: credential helper `store` configured; identity maskedmimi /
  maskedmimi96@gmail.com; branch `master` (solo project, no dev branch yet).

## Build & test loop

- Build: `make -j$(nproc)` → `pokeemerald.gba`
- Test in **mGBA**. Compiling ≠ working: every change gets an in-game check.
- **Save states do not survive rebuilds** — they snapshot RAM with pointers
  into the old ROM; loading one on a new build produces garbage tiles and
  glitched audio. Rule: delete and remake save states after every rebuild.
  In-game saves (.sav) are robust across builds.
- **Debug menu is enabled** (`include/config/debug.h`,
  `DEBUG_OVERWORLD_MENU TRUE`): R+START in the overworld →
  Utilities → "Warp to map warp" → group/map/warp digits.
  Zeegem = group 000, map 058, warp 000 (no warp → drops at map center).
  ⚠️ **PRE-RELEASE CHECKLIST: revert to `DISABLED_ON_RELEASE`.**

---

## Key tools

| Tool | Role |
|------|------|
| **Porymap 6.3.1** | Visual map editing & polish (human pass) |
| **Poryscript** | ALL event scripting (`.pory`) — never raw `.s` scripts |
| **tools/render_map.py** | Renders any layout's map.bin to PNG with real tileset graphics → `tools/renders/` (gitignored). Mandatory self-check after any data-level map edit. |
| **tools/route1_metatile_legend.json** | Metatile legend (IDs + collision + elevation) decoded from vanilla/own maps — extend it, don't rebuild it |
| **mGBA** | Emulator testing |
| **porytiles** (bookmarked, NOT installed) | Custom tileset compiler for the future graphics phase (pier, stilt houses, Flemish roofs). Existing tilesets only until then. |

## Map data format & conventions

- `data/maps/<Map>/map.json` — header, connections, warps, events (readable JSON)
- `data/layouts/layouts.json` — dimensions + tilesets per layout
- `data/layouts/<LAYOUT>/map.bin` — the tile grid: little-endian u16 per cell;
  bits 0–9 metatile ID, 10–11 collision, 12–15 elevation.
  `border.bin` — the 2×2 border block, same format.
- **Map groups:** outdoor maps (towns, routes) go in `gMapGroup_TownsAndRoutes`
  (appended after vanilla); `gMapGroup_Laekon` holds interiors only.
  Interiors reuse vanilla layouts where possible (Zeegem houses reuse
  Dewford's LAYOUT_HOUSE3/4) — maps and layouts are separate; share layouts,
  never duplicate blockdata.
- **Naming:** Laekon maps use `MAP_LAEKON_*` / `LAYOUT_LAEKON_*` where a
  vanilla collision is possible. Routes are numbered from 1 (vanilla Hoenn
  is 101+; FRLG's MAP_ROUTE1 exists — hence the prefix).
- **Warps** are per-tile point events: a 2-tile doormat needs 2 warp events.
- **Borders & connections:** the border block tiles infinitely in every
  direction that has NO connection; a connection replaces the border on that
  side and draws the neighbor's real tiles. Therefore **connected edges are
  one shared seam designed together** — adjacent columns/rows of both maps
  must agree (coastline heights, tree lines, terrain continuity).
- Water tiles: copy collision+elevation verbatim from vanilla ocean
  (Route 104) — generated traversability models must be validated in-engine
  once before trusting automated path checks (BFS on wrong collision data
  happily verifies wrong conclusions).
- See `docs/MAP_DESIGN_GUIDE.md` for the full map-craft lessons.

## Known gotchas

- **Porymap strips `"name_clone"` fields** when saving
  `src/data/region_map/region_map_sections.json`. Never commit that as a
  side effect; `git restore` the file if Porymap touched it incidentally.
- GBA text is **plain ASCII only** — smart quotes and em-dashes break the
  assembler ("unknown pseudo-op" errors usually mean malformed `.string`).
- MAPSEC placeholders: Zeegem currently displays "LITTLEROOT TOWN"
  (`MAPSEC_LITTLEROOT_TOWN`); real `MAPSEC_ZEEGEM` etc. wait for the Laekon
  region map (Porymap Region Map Editor session, later).
- **One editor at a time on map data.** Porymap and direct/scripted edits to
  `map.bin`/`border.bin` (e.g. `tools/gen_route1.py`-style generators, hex
  edits, `tools/check_map.py` fixes) must never run in the same working
  session. Porymap keeps its own in-memory copy of the layout and **a
  Porymap save clobbers any external binary patch made since it was
  opened** — it writes its own state back out, silently discarding the
  external change. Close Porymap fully before making a data-level edit, and
  reopen it fresh (don't rely on a stale open window's "reload") after, so
  it re-reads the patched file instead of overwriting it. See
  `docs/MAP_DESIGN_GUIDE.md` for the full rule.

## Cleanup backlog

- Delete the Littleroot practice duplicate (`MAP_LITTLEROOT_TOWN_2` + its
  renamed heal locations) — leftover learning exercise
- Eventually purge/repurpose vanilla Hoenn maps once Laekon replaces them
- Build the Laekon region map (creates real MAPSECs)
- Pre-release: disable debug menu (see above)

---

## Custom mechanics to implement (priority order)

1. **Ranger Star Rank System** — player variable 0–3, trainer card display, map/NPC gating
2. **The Catch Ceremony** — scripted Partnering Park opening: one Ball, timed catch, Globo debrief
3. **Tournament battle system** — Colosseum-style brackets vs challenger pool, public ranking
4. **Shadow Pokémon state** — aura visual, unruly AI, bond-based purification (identifiers: SHADOW)
5. **Sanctuary progress tracker** — contribution milestones, visual growth, rewards
6. **Partner Bond system** — separate from friendship; drives purification power; ties to the Catch Ceremony partner

## Workflow

- Small verifiable steps: one change → build → mGBA test → commit
- Commit convention: `[area] Short description`
  (`[map]`, `[script]`, `[tools]`, `[docs]`, `[fix]`, `[chore]`, `[battle]`, `[ui]`, `[data]`)
- Claude Code sessions: scoped goals, CLAUDE.md as standing brief,
  auto-accept/auto mode for autonomy, human playtests every milestone
- Map production pipeline: written brief → generated draft (legend-based
  generator + render self-review loop) → human polish in Porymap →
  in-game verification
- Pre-existing unrelated issues: report, fix only if asked, commit separately
- The design document is the source of truth — flag conflicts, never
  silently work around them

## Community resources

| Resource | URL |
|----------|-----|
| pokeemerald-expansion wiki | https://github.com/rh-hideout/pokeemerald-expansion/wiki |
| PokéCommunity decomp forums | https://www.pokecommunity.com/forums/decomp-disassembly-tutorials.475/ |
| pret/pokeemerald | https://github.com/pret/pokeemerald |
| Poryscript | https://github.com/huderlem/poryscript |
| Porymap | https://github.com/huderlem/porymap |
| porytiles | https://github.com/grunt-lucas/porytiles |
