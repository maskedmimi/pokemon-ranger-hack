#ifndef GUARD_CONSTANTS_RANGER_RANK_H
#define GUARD_CONSTANTS_RANGER_RANK_H

// Laekon Ranger Corps hierarchy (docs/DESIGN_DOCUMENT.md, "The Ranger Corps & Hierarchy").
// Stored in VAR_RANGER_RANK (constants/vars.h). This is the ONLY progression gate --
// never badge flags. Values 0-3 map 1:1 onto the design doc's star ranks.
#define RANGER_RANK_CHALLENGER      0 // No stars. Entered the Trials via the Catch Ceremony.
#define RANGER_RANK_SECOND_CLASS    1 // 1 star. Defeated Warden Hesianor (Zone 1).
#define RANGER_RANK_FIRST_CLASS     2 // 2 stars. Defeated Warden Hippotes (Zone 2).
#define RANGER_RANK_ELITE           3 // 3 stars. Defeated Warden Halthir (Zone 3).

#define RANGER_RANK_MIN RANGER_RANK_CHALLENGER
#define RANGER_RANK_MAX RANGER_RANK_ELITE

#endif // GUARD_CONSTANTS_RANGER_RANK_H
