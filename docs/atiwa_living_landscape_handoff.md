# Living Landscape Handoff

## Current Direction

Living Landscape is an unofficial Atiwa variety expansion. The current design
goal is to create genuinely different but viable strategies, not to award
extra points for the base game's existing trained-family, gold, nature-icon,
or fruit-bat engines.

The v0.1 scoring-only design remains in
`docs/atiwa_living_landscape_design.md` as a baseline. The active experiment is
the v0.2 draft in `docs/atiwa_stewardship_commitments_v0_2.md`.

The v0.2 structure is:

- public Landscape Priorities eventually provide non-reinforcing spatial
  conditions shared by all players;
- personal Stewardship Commitments are chosen after normal setup and revealed
  before the first worker placement;
- each Commitment has one ongoing benefit and one connected mandatory
  restriction;
- Commitments currently provide no end-game VP;
- the first tests isolate Commitments without Landscape Priorities.

## Five Prototype Commitments

1. Wildlife Warden: fruit on a newly gained wildlife-produced tree; wild
   animals cannot be spent during Feeding.
2. Pastoral Cooperative: each goat reduces food demand by 2; goats cannot be
   spent after demand is calculated.
3. Distributed Settlement Planner: Locations cost 1 less gold; no Location may
   contain more than two families.
4. Bat Conservationist: the first fruit bat action each round moves 2 bats
   instead of 3; bats cannot be spent during Feeding.
5. Forest Reserve Keeper: the first acquired Terrain becomes a flexible
   Reserve; its tokens cannot be voluntarily spent or moved.

The exact wording and setup rules are authoritative in
`docs/atiwa_stewardship_commitments_v0_2.md`.

## Implemented Test Support

The `atiwa_living_landscape/` package contains:

- `commitments.py`: executable helpers for the five rules;
- `terrain.py`: deterministic synthetic eight-space Terrain generation;
- `generate_terrain.py`: JSON and printable HTML output;
- `simulate.py`: bounded Commitment and Terrain pressure report;
- `test_commitments.py`: executable rule and generator tests.

Validated commands:

```bash
python3 -m unittest discover -s atiwa_living_landscape -p 'test_*.py' -v
python3 -m atiwa_living_landscape.simulate --seed 20260722 --decks 1000
python3 -m atiwa_living_landscape.generate_terrain --seed 20260722 --format json
python3 -m atiwa_living_landscape.generate_terrain --seed 20260722 --format html
```

Current validation result: 8 tests pass under the checkout's Python 3.9, the
package compiles, and `git diff --check` is clean.

## Initial Findings

- Pastoral Cooperative may be too efficient when a player already preserves
  goats.
- Distributed Settlement Planner may provide too little benefit for its
  two-family cap; a one-tree rather than one-gold discount is the first
  fallback to test.
- Wildlife Warden and Bat Conservationist each have a seven-round maximum
  trigger.
- Forest Reserve Keeper is sensitive to the official deck's blank-space
  distribution.
- Synthetic Terrain is suitable for legality, capacity, and extreme-value
  checks only; it is not an exact Atiwa balance model.

## Next Required Input

Exact-deck simulation needs a transcription of all 36 official Terrain cards.
Use one CSV row per distinct card with this header:

```csv
id,name,copies,printed_vp,nature_icons,top_middle,top_right,middle_left,middle_center,middle_right,bottom_left,bottom_center,bottom_right,notes
```

Space codes:

```text
B      blank
X      blocked/non-space
W      wild animal
T      tree
F      fruit
BAT    fruit bat
G      goat
H      normal house
HU     uninhabitable house
T+W    tree that can hold a wild animal
T+BAT  tree that can hold a fruit bat
```

Preserve card orientation and exact space position because pollution fills
spaces in positional order. Use `?` plus a note rather than guessing an
unclear symbol. After the CSV is supplied, validate its IDs, total physical
card count, codes, positions, copies, and known special spaces before replacing
the synthetic deck in balance simulations.

## Workspace State

The uploaded `atiwa/` reference folder and
`New_Frontiers_Tile_List_ver_1_2.xlsx` are untracked user files and were not
modified or included in the Living Landscape implementation commit.
