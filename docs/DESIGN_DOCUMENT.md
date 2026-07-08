# Pokémon ROM Hack — Design Document
> Base: Pokémon Emerald (GBA) | Engine: pokeemerald-expansion
> Status: Pre-production — core concepts locked
> Last updated: July 2026 (v3 — hierarchy rework, Shadow terminology, Madkings, Warden redesign)

---

## Table of Contents
1. [Vision & Tone](#vision--tone)
2. [The Region — Laekon](#the-region--laekon)
3. [The Ranger Corps & Hierarchy](#the-ranger-corps--hierarchy)
4. [The Ranger Trials — Challenge Structure](#the-ranger-trials--challenge-structure)
5. [The Catch Ceremony](#the-catch-ceremony)
6. [Shadow Pokémon](#shadow-pokémon)
7. [The Villain — Morimorty & the Madkings](#the-villain--morimorty--the-madkings)
8. [The Legendary — Mew](#the-legendary--mew)
9. [The Final Confrontation & Redemption](#the-final-confrontation--redemption)
10. [The Rival Trio](#the-rival-trio)
11. [Key NPCs](#key-npcs)
12. [The Sanctuary](#the-sanctuary)
13. [Biomes & Outposts](#biomes--outposts)
14. [Open Questions](#open-questions)

> Companion documents: `NAMING_GUIDE.md` (naming system & titles), `CHARACTERS.md` (full cast reference), `TECHNICAL_CONTEXT.md` (dev environment).
> Terminology note: corrupted Pokémon are called **Shadow Pokémon** (the term "Obscure" from earlier drafts is retired everywhere, including code identifiers).

---

## Vision & Tone

This hack blends the epic journey feel of **Blazed Glazed**, the rich NPC storytelling of **Dreamstone Mysteries**, and the catch-for-purpose hook of **Pokémon Lazarus**. The tone sits between cozy-emotional and grand-adventurous — never edgy for the sake of it, but not afraid of weight and genuine stakes. Keep it simple and lighthearted on the surface; let the weight live underneath.

### Core Philosophical Thesis
> *A great trainer doesn't seek power for themselves. They earn it so they can protect something bigger than themselves.*

Everything revolves around one central question asked from three different angles:

**Is a bond something you build, something you're given, or something you choose to see?**

The Three Wardens embody the three answers: Halthir *builds* it, Hesianor believes it is *given*, Hippotes learns to *see* it. Morimorty is the man who abandoned all three — and is saved, in the end, by all three.

### What Makes This Hack Different
- The gym challenge is replaced by the **Ranger Trials** — a public tournament circuit that is the one and only recruitment path into the Ranger Corps
- Starters are chosen through a **Catch Ceremony** in a nature park rather than assigned in a lab
- Catching Pokémon has **real purpose** — the Sanctuary grows and evolves based on your contributions
- **Shadow Pokémon** exist as both a natural phenomenon and an artificially triggered weapon
- The main villain is the **region's greatest living hero**, hidden in plain sight at the top of the institution
- The legendary (Mew) is **never caught** — it withdrew from the region long ago, and in the finale you *rescue* it

---

## The Region — Laekon

### Identity
A land that built its entire civilization around the idea that humans and Pokémon thrive together. Settlements exist *within* the wilderness rather than pushing it back — a forest growing through the center of a city, rivers that split towns in two that nobody ever dammed, mountain ranges visible from everywhere that nobody has fully mapped.

The region feels **ancient and alive simultaneously**. Human infrastructure bends around Pokémon ecosystems, not the other way around. Towns are built where the Pokémon already were.

### Name — RESOLVED
**Laekon** — derived from Laeken (Belgium). The region's culture carries a Belgian/Flemish coastal flavor throughout.

### Town Naming Theme — RESOLVED
**Flemish geographic suffixes + biome flavor prefixes.** Full generator, glossary, and per-biome palettes in `NAMING_GUIDE.md`.

Canon names so far:
- **Zeegem** ("sea-home") — the coastal starter village, adjacent to the Partnering Park. Tidal Reach.
- **Kroonveld** ("crown field") — Heartlands capital; hosts the Grand Final and Ranger Corps HQ.

---

## The Ranger Corps & Hierarchy

### What It Is
The Ranger Corps is the region's highest civic institution — a public, celebrated order of elite trainers who serve as Laekon's protectors, habitat managers, and crisis responders. **The Ranger Trials are the one and only way to become a ranger** — the Trials ARE the Corps' recruitment pipeline. The public watches them the way people watch national sporting events, knowing the participants are the region's future guardians.

### The Hierarchy — RESOLVED (final)

One ladder, climbed through the Trials:

| Title | How it is earned |
|-------|------------------|
| **Challenger** | Enter the Ranger Trials (starts with the Catch Ceremony) |
| **Ranger Second Class** ⭐ | Zone 1: participate in its 3 tournaments + complete the Warden's mission → duel and defeat Warden Hesianor |
| **Ranger First Class** ⭐⭐ | Zone 2: same loop → defeat Warden Hippotes |
| **Elite Ranger** ⭐⭐⭐ | Zone 3: same loop → defeat Warden Halthir |
| **Trial Champion** | Win the Grand Final, open to all Elite Rangers of the season — one Champion per year |
| **Heartwarden** | The Trial Champion is presented to Mew in the Heart of Laekon. Only if Mew recognizes them. It has not happened in decades. |

Outside the ladder:
- **The Three Wardens** — appointed guardians of the three zones, chosen from among veteran Elite Rangers. Not a rank you win.
- **The Heartwarden leads the Corps** — Morimorty, the only living person Mew ever recognized. New Elites and Champions are minted every year; none of it touches his seat, because his seat was never won.

### Key design consequences
- **Participation, not victory:** challengers must *compete in* each zone's three tournaments, not win them. The gate to promotion is the Warden — their mission, then their duel. Challengers can lose brackets (to the player, to each other) and still become rangers. Losing to the player costs nobody their dream.
- **Elite Ranger is accessible by design** — the Corps genuinely staffs itself from the Trials every year. Elite Rangers of past seasons appear across the region as NPCs (see Mimi).
- **Trial Champion keeps the classic Pokémon "Champion" alive** — with the twist that in Laekon, being Champion was never the real prize. Every year the region holds its breath for the recognition that never comes.
- **The star ranks (0–3) map 1:1 onto the player progression variable** — 0 Challenger, ⭐ Second Class, ⭐⭐ First Class, ⭐⭐⭐ Elite. This is what gates map access in code. (Code identifiers should use SHADOW, not OBSCURE.)

### The Three Wardens
Appointed zone guardians, each embodying a pillar of the ranger craft. Full personalities in `CHARACTERS.md`.

| Warden | Zone | Pillar | Partner |
|--------|------|--------|---------|
| **Hesianor** | Zone 1 | **Coexistence** — the bond between people, Pokémon, and the land itself | Ludicolo (alt: Whiscash) |
| **Hippotes** | Zone 2 | **Understanding** — the bond studied, measured, optimized | Metagross |
| **Halthir** | Zone 3 | **Protection** — the bond as a shield; crisis command | Alolan Ninetales |

### The Wardens' Blind Spot — story-critical
Morimorty and the three Wardens were **challengers of the same Trials generation** — four friends who adventured together. They witnessed him become the Hero of Laekon (see The Villain). They trust him deep in their hearts. Each of them can feel that *something in him changed* after the crisis of their youth — but loyalty finishes none of those thoughts. You don't suspect the friend who saved your life at twenty. Their blindness is love, not foolishness — and it is why the betrayal, when revealed, devastates.

### Governance — The Circuit Council
A **triumvirate**: the Ranger Corps leadership (Morimorty and the Wardens), the Professor's Institute (bond research, the Corps' scientific backbone), and the Gym Leaders (guardians of battle tradition). Every major decision requires all three to agree. Its balance is its vulnerability — and Morimorty is quietly tilting it.

---

## The Ranger Trials — Challenge Structure

### The Zone Loop (repeated three times)
1. **Three city tournaments** — Colosseum-style multi-round brackets against fellow challengers, held in public arenas across the zone's cities. These are the gym equivalents. Participation is mandatory; victory is not. Rankings build publicly; NPCs recognize you as you climb.
2. **The Warden's mission** — one real ranger field mission commissioned by the zone's Warden, reflecting their pillar. The in-fiction proof that the Corps values work, not just winning.
3. **The Warden duel** — the Warden grants their battle to challengers who completed the mission. Victory = promotion.

### Zone Flavor

**Zone 1 — The Open Circuit** (Warden Hesianor)
Festive, public, accessible. The zone teaches *why rangers exist*: coexistence with the wild. Shadow incidents are distant rumours.
→ ⭐ Ranger Second Class.

**Zone 2 — The Proving Grounds** (Warden Hippotes)
The skill-check midgame. Hippotes' EV/IV appraisal service unlocks here. Shadow incidents hit closer to home; the Sanctuary comes under threat; Morimorty begins his public narrative.
→ ⭐⭐ Ranger First Class.

**Zone 3 — The Vanguard Circuit** (Warden Halthir)
The Shadow crisis peaks — supervised by the Corps' crisis commander himself. The player's first close Shadow encounter happens alongside Halthir. The truth starts surfacing. Rivals scatter, each confronting the crisis differently.
→ ⭐⭐⭐ Elite Ranger + entry to the Grand Final.

**The Grand Final** — Kroonveld. All Elite Rangers of the season compete; the winner is the year's **Trial Champion** and is presented to Mew in the Heart of Laekon.

---

## The Catch Ceremony

At the start of every Trials season, new challengers don't receive a starter from a lab. They participate in the **Catch Ceremony** — a public tradition held in the **Partnering Park**, a sprawling nature reserve adjacent to Zeegem, managed by the Professor.

### How It Works
- The park is populated with wild Pokémon of all kinds — common, rare, regionally unique
- Each new challenger is given **one Poké Ball** and released into the park for a limited time
- The goal: find a Pokémon that calls to you and catch it — your first partner
- Supervised, festive, a rite of passage — locals come to watch
- The Professor observes from a tower and comments on notable catches at the post-ceremony gathering

### Why It Works
- No arbitrary restriction to 3 choices; the single ball creates meaningful tension
- Other challengers catch alongside you — narrative introduction to the rivals and challenger cast (Q, Sanka, Riri, Arthur...)
- The Professor's comments on your catch echo throughout the game
- Framed as the **first Ranger assessment** — senior Rangers observe how you approach wild Pokémon

### Mechanical Considerations
- Possible time-of-day or seasonal variation in park availability
- The caught partner is referenced by NPCs throughout the journey
- The post-ceremony debrief doubles as tutorial and world introduction

---

## Shadow Pokémon

### The Natural Phenomenon
Rare, tragic, and ancient. Laekon has old folklore about them — cautionary tales, monuments, a town damaged by one centuries ago. They occur when a Pokémon's emotional bond is catastrophically broken: loss of a partner trainer, extreme habitat destruction, prolonged isolation.

A natural Shadow Pokémon is **shattered, overwhelmed, suffering** — not evil, not controlled. The Corps has protocols for them (written by Halthir); the Professor studies natural cases.

**The defining historical case:** decades ago, a Shadow Pokémon crisis struck Laekon during Morimorty's own Trials year. He ended it — at a devastating personal cost — and Mew recognized him for it. The hero and the villain were born on the same day.

### The Source of the Artificial Version — Marshadow
The artificial phenomenon originates from **Marshadow**, Morimorty's genuinely bonded partner. Marshadow's shadow energy can jam a Pokémon's heart shut directly — flooding it with emotional overload until it tips into the Shadow state.

### The Madkings' Serum — The Delivery System
The Madkings' scientists distilled Marshadow's shadow energy into a **serum** — scalable, portable, deniable. Ordinary operatives can corrupt Pokémon anywhere while Marshadow (and therefore Morimorty) stays invisible.

- **Invisible and fast** — infection shows no external sign until the Pokémon turns
- **Reversible** — wears off eventually; can be countered through purification
- **Mimics the natural phenomenon** — experts conclude incidents are natural; the synthetic signature requires very specific analysis to detect (Hippotes' instruments are what eventually isolate it)

**Power tiers:** serum corruption is diluted and reversible. **Direct corruption by Marshadow is raw and vastly stronger** — it happens once in the story, to Mew, in the finale.

### Purification
The bond between a trainer and their partner Pokémon breaks through the artificial emotional noise — the partner lends its own bond energy to reach the Shadow Pokémon.

- The player's partner matters mechanically, not just narratively
- Bond strength affects purification effectiveness
- Every Shadow encounter is framed as an emotional rescue, not just a boss fight

### The Mid-Game Turning Point
The Professor discovers the synthetic signature in a sample (isolated with Hippotes' analytical tools) — proof the incidents are manufactured, and evidence pointing toward the very top of the institution.

---

## The Villain — Morimorty & the Madkings

### Morimorty — Profile
- **Age:** ~50
- **Appearance:** Warm, distinguished, soft-spoken. The kind of person people instinctively trust.
- **Public role:** **The Heartwarden** — the Hero of Laekon, head of the Ranger Corps, the only living person Mew ever recognized.
- **Partner:** **Marshadow** — his one remaining genuine bond.
- **Name notes:** echoes *memento mori* and "the Mad King." Distinct from canon Gym Leader Morty — always "Morimorty" in-game.

### The Hero of Laekon
During his own Trials year, a Shadow Pokémon crisis struck the region. Morimorty — a young challenger adventuring alongside Hesianor, Hippotes, and Halthir — ended it, at a devastating personal cost. Mew recognized him in the Heart of Laekon: the last Heartwarden ever named. He led the Corps ever since, beloved, unassailable — not because of his office, but because he is the one man the region's guardian ever chose.

### The Fall — the Mad King
The crisis never left him. *"What if next time is worse? What if my bond isn't enough?"* Over decades the fear became obsession: the legendary must be **controlled** — not trusted, wielded. He restages the worst day of his life, over and over, in manufactured miniature — because it is the only day Mew ever looked at him. He never makes a villainous speech. He still believes he is the hero.

**Key tragic detail:** Mew would not recognize him anymore even if he controlled it — and some part of him knows.

### Marshadow — The Bond That Stayed
Marshadow bonded with Morimorty genuinely, in his heroic years — a Pokémon drawn to the shadows in people's hearts, living literally in his shadow. When grief consumed him, Marshadow stayed. It never judged him; it only reflected him. A poisoned, enabling bond — and the game's thesis made flesh: **even the villain's power comes from a bond.** It is also his way back (see Redemption).

### Mew's Withdrawal — why his power is self-reinforcing
Mew, sensing the growing shadow in the region, withdrew — stopped appearing entirely. Citizens feel abandoned by their guardian and rally ever harder behind the one man Mew ever chose. Every Madkings incident deepens the fear; the fear deepens devotion to Morimorty. **The shadow Mew fled from is Morimorty's own heart** — the region rallies behind the very cause of its abandonment.

### The Madkings — Structure
A **small, secretive cell** of scientists and field operatives — no uniforms, no grunts. Some don't know who funds them; some genuinely believe they are developing defenses against natural Shadow events.

- A handful of trusted operatives with serums
- Strategic targeting — Pokémon near populated areas, tournament venues, the Sanctuary
- Morimorty stays completely clean — publicly horrified by every incident, calling for stronger measures each time. A slow drip of manufactured fear, never an assault.
- As Heartwarden, **he directs the investigation into his own attacks** — assigning investigators (Mimi) and quietly curating their leads.

### The Political Play
As incidents multiply, public fear rises. People question whether the Trials, the bonding philosophy, and the Rangers are sufficient. Morimorty positions himself as the voice of reason: *"We need something more powerful. We need certainty. We need the legendary under our protection."*

### How Everything Connects
- The Catch Ceremony and bonding philosophy are directly threatened by the narrative that bonds are not enough
- The Sanctuary is a target — and the site of the player's first close Shadow encounter (alongside Halthir)
- The Circuit Council is being driven apart
- Mimi's investigation is steered onto false trails by the man he reports to
- The Wardens feel their old friend has changed but cannot finish the thought — their loyalty is his best camouflage
- Mew's recognition becomes the finale: it chooses between the man who wants to control it and the player who earned its trust

---

## The Legendary — Mew

### Species — RESOLVED
**Mew.** The ancestor of all Pokémon, said to appear only to those pure of heart — the embodiment of Laekon's bonding philosophy. (Mythical rather than Legendary officially; in Laekon it is simply "the legendary.")

### Role
Laekon's ancient protector — present in mythology, folklore, and Ranger tradition for thousands of years. It dwelled hidden in the **Heart of Laekon**, revealing itself only to Trial Champions it deemed worthy. Recognition was always rare — perhaps once in a generation. The last: Morimorty. Then, sensing the growing shadow, **Mew withdrew entirely** — Champions come and go, presented to an empty Heart. The region grieves its silence.

### The Recognition
Not a battle. Mew approaches, looks at the champion, and scans their journey — their bond with their partner, every challenge, every rival. It communicates in feeling, not words. If it recognizes them as worthy, it touches their partner Pokémon and something passes between them. From that moment it is aware of them.

### Why Morimorty Cannot Have It
Mew recognizes bonds, not power. It could not recognize him anymore even if he physically controlled it — the connection died with the philosophy that built it. So he will not try to open its heart. He will jam it shut.

---

## The Final Confrontation & Redemption

Morimorty and Marshadow reach the Heart of Laekon. Marshadow — the source, undiluted — corrupts Mew directly. A Shadow Mew doesn't choose anyone; it can be *taken*. Morimorty finally holds the legendary — a hollowed-out puppet of the thing that once looked at him with love. Some part of him knows.

**The battle — two phases:**
1. **Morimorty, the champion he used to be** — his ace team anchored by Marshadow.
2. **Shadow Mew unleashed** — boosted (direct-corruption tier). The fight becomes a **purification battle**: the player's partner bond is the real weapon, purifying Mew mid-battle. Beating him with stats would be a boss fight; **saving Mew while he watches his last plan dissolve is the story.**

Mew purified, it recognizes the player — the first new Heartwarden in decades, recognized mid-rescue rather than at a ceremony. Mew is never caught.

### Redemption — RESOLVED direction
Morimorty is not destroyed; he is *reached*. What breaks through is not defeat but the two bonds that never left him: **Marshadow**, who stayed through everything without judging — and **his three old friends**, the Wardens, who arrive and finally finish the sentence they could never finish. The man who spent decades proving bonds weren't enough is saved by the ones he never lost. Exact scene staging TBD (accountability, what becomes of him afterward — but the door to peace stays open, in keeping with the game's tone).

---

## The Rival Trio

Three rivals from the Catch Ceremony who reappear throughout the Trials.

### Rival 1 — The Skeptic
Analytical, methodical, sees Pokémon as tools — not cruelly, just practically. Partner chosen purely for stats; a genuine bond forms despite himself. Drawn toward Morimorty's "strength over bonds" narrative in Zone 2 before rejecting it. Battled most frequently; most tactically instructive.
**Partner:** TBD — something competitive that becomes unexpectedly loyal.

### Rival 2 — The Natural
Gifted; her Pokémon adore her effortlessly — but she chases the tournament spotlight rather than the bond. Her growth: the crowd's cheers mean less than she thought. Ahead early; plateaus as the player's bond deepens.
**Partner:** TBD — something naturally charismatic.

### Rival 3 — TBD
Reserved. Candidate: promote **Sanka & Riri** into a shared sibling rival slot (their arcs already interlock with the plot) — or keep them as challengers and design Rival 3 separately.

---

## Key NPCs

Full bios in **`CHARACTERS.md`**. Summary:

- **The Professor** (name/gender placeholder — likely a Discord friend; "Cypress" is the working name) — bond researcher; runs the Partnering Park and the Institute; discovers the synthetic signature; the Sanctuary and its rehabilitation work fall under her institute.
- **Morimorty** — see The Villain.
- **The Three Wardens** — Hesianor (Coexistence), Hippotes (Understanding, EV/IV service, the lab AI **Settopih**), Halthir (Protection, crisis command, Shadow protocols).
- **Mimi** — Elite Ranger and former **Trial Champion** whom Mew never came for; the Corps' lead field investigator, partner Dragapult. Unknowingly steered by Morimorty. Duo battle alongside the player late game; entrusts them with the final mission.
- **The Challenger Cast** — Q, Sanka, Riri, Arthur + more TBD. Sanka's first-responder dream points at Halthir's crisis response teams; Riri's rehabilitation dream points at the Sanctuary.

---

## The Sanctuary

A Pokémon conservation project in the **Verdant Basin**, encountered **early in the game**, run under the Professor's institute. It doubles as Laekon's rehabilitation grounds — where rescued Pokémon, and later purified Shadow Pokémon, recover. The Ranger managing it day-to-day becomes a recurring supporting character.

### What Contributions Unlock
- Real rewards: items, area access, lore entries
- The Sanctuary **visually grows** as contributions are made
- A side-story climax around the Sanctuary late in the game

### Narrative Role
- A Madkings target — the player's first close Shadow encounter involves a Sanctuary Pokémon deliberately triggered, faced alongside Halthir
- The Professor's institute is nearby — the Basin is the ecological heart of the region
- Riri's ending: she joins the Sanctuary's rehabilitation work

---

## Biomes & Outposts

Seven distinct biomes, each with a Ranger Outpost with its own specialty, culture, and ecosystem. Rangers from different outposts have genuine knowledge gaps about each other's territories.

| Biome | Name | Outpost Specialty | Key Feature |
|-------|------|-------------------|-------------|
| Coastal Wetlands | The Tidal Reach | Marine biology, water migration | **Zeegem** + Partnering Park; stilt towns, fishing-community tensions (Hesianor's home turf) |
| Ancient Forest | The Deepwood | Old-growth preservation, psychic/ghost phenomena | The Professor's research station |
| Alpine Mountains | The Highwatch | Search & rescue, weather monitoring | Oldest outpost; site of the ancient Shadow incident |
| Volcanic Plains | The Ashfields | Geological monitoring, disaster response | Sacred active volcano, restricted access |
| Tropical Rainforest | The Verdant Basin | Biodiversity research, rare habitats | The Sanctuary + the Professor's main institute |
| Northern Tundra | The Pale Expanse | Isolation survival, ice Pokémon behavior | Strange lights; oldest mythology about Mew |
| Central Plains | The Heartlands | Urban coexistence, tournament hosting | **Kroonveld**: Grand Final arena, Corps HQ, Circuit Council; near the Heart of Laekon |

Biomes bleed into each other at their edges — the Deepwood creeps into the Verdant Basin, the Highwatch feeds rivers into the Tidal Reach, the Ashfields border the Pale Expanse in a dramatic fire/ice collision.

---

## Open Questions

Resolved in v3: ~~hierarchy~~ (final ladder above), ~~Warden roles & personalities~~, ~~villain team name~~ (the Madkings), ~~terminology~~ (Shadow Pokémon), ~~Morimorty backstory~~ (Hero of Laekon, quartet generation), ~~Mew's withdrawal~~, ~~redemption direction~~.

Still open:

- [ ] **Rival 3** — promote Sanka & Riri, or design separately?
- [ ] **Rival 1 & 2 partner Pokémon**
- [ ] **Morimorty's full battle team** (Marshadow anchors it; shadow/grief motif)
- [ ] **The three Warden missions** (one per zone, reflecting each pillar; Hesianor's likely ties to Tidal Reach fishing tensions)
- [ ] **The old crisis** — what exactly happened in Morimorty's Trials year, and what it cost him
- [ ] **Redemption scene staging** — how the Wardens reach him; what becomes of him after
- [ ] **Settopih's vessel** — Rotom lab-possession vs Porygon-Z
- [ ] **The Professor** — final name, identity (Discord friend), personality
- [ ] **Tournament venues** — which cities/biomes host which tournaments
- [ ] **Travel between biomes**
- [ ] **The synthetic-signature discovery scene** — exact narrative moment
- [ ] **The Heart of Laekon** — visual design and location
- [ ] **Remaining town names** — generate with NAMING_GUIDE.md as maps are built
- [ ] **"Soul Squad"** — optional nickname (challenger friend group?) or drop

---

*This document is a living reference. Update it as design decisions are made.*
