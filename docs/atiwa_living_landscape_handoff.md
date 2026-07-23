# Living Landscape Handoff

## Current Direction

Living Landscape is an unofficial Atiwa variety expansion. The current design
goal is to create genuinely different but viable strategies, not to award
extra points for the base game's existing trained-family, gold, nature-icon,
or fruit-bat engines.

The v0.1 scoring-only design remains in
`docs/atiwa_living_landscape_design.md` as a baseline. The v0.2
benefit-plus-constraint experiment remains in
`docs/atiwa_stewardship_commitments_v0_2.md`.

The active design experiment is the v0.3 Open Commitment race in
`docs/atiwa_open_commitments_v0_3.md`:

- reveal player count plus 1 public Open Commitments after normal setup;
- every player may race to complete any of them but may claim at most 2;
- the provisional claim ladder is 7/4/2 VP for first, second, and third;
- in a two-player game, skip the middle reward so first scores 7 VP and second
  scores 2 VP;
- claims are permanent and use action-timed, objectively verifiable
  conditions;
- fourth place scores nothing;
- solo replaces claim order with a provisional round III/V/VII timing race;
- test this module without v0.1 Landscape Priorities or v0.2 personal powers.

The extra public goal preserves a pivot lane after a player loses a race, while
the 2-claim cap keeps the module from overwhelming normal Atiwa scoring.

The purpose of Open Commitments is not simply to distribute expansion points.
The visible races should stretch players into different playstyles by changing
which Terrain cards, Locations, token arrangements, and worker actions they
value. Claim order should create interaction, goal chasing, denial, and pivot
decisions without adding direct resource theft.

The earlier v0.2 structure was:

- public Landscape Priorities eventually provide non-reinforcing spatial
  conditions shared by all players;
- personal Stewardship Commitments are chosen after normal setup and revealed
  before the first worker placement;
- each Commitment has one ongoing benefit and one connected mandatory
  restriction;
- Commitments currently provide no end-game VP;
- the first tests isolate Commitments without Landscape Priorities.

## Fields of Arle Benchmark

*Fields of Arle* and *Tea & Trade* are benchmarks for strategic variety, not
for expansion size or complexity. Arle creates divergent play through a broad
shared sandbox of seasonal actions, tools, land, animals, buildings, vehicles,
goods, and travel. *Tea & Trade* adds further connected routes rather than
strongly constrained player roles.

Atiwa's ecological economy is much narrower, so Living Landscape must create
variety by altering conversions and spatial rules instead of adding general
bonuses to the normal tree, bat, goat, gold, and trained-family engine. The
durable target is at least five genuinely different solutions to Atiwa's
feeding, capacity, and ecology problem with low rules and component overhead.

Commitments should affect multiple kinds of decisions, impose a recurring
opportunity cost, and enable a strategic lane without dictating a complete
victory script. Later Landscape Priorities should vary which lanes are
attractive in each game. Do not add a universal Tea-like action accelerator;
in Atiwa it would likely reinforce the strongest base-game route and reduce
the distinctions between Commitments.

## Black Forest and Tea Garden: Puerh Benchmarks

*Black Forest* strengthens the public-engine lesson from Fields of Arle:
strategies should emerge in response to visible, variable opportunities that
change conversions, timing, space, and competition. Living Landscape should
borrow that setup-responsive divergence without adding another production
subsystem.

The Imperial Decrees in *Tea Garden: Puerh* are the direct structural benchmark
for v0.3. Open achievements create a race because later claimants receive fewer
points. The Atiwa experiment uses that declining-reward interaction to make
players monitor opponents and chase different goals through the existing
worker-placement and tableau systems.

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
  goats; its restriction may fail to create a real opportunity cost.
- Distributed Settlement Planner may provide too little benefit for its
  two-family cap; a one-tree rather than one-gold discount is the first
  fallback to test.
- Wildlife Warden is a strong example because it redirects wildlife into
  orchard infrastructure while removing its emergency-food use.
- Bat Conservationist has a seven-round maximum trigger, but may simply
  accelerate the normal bat engine because efficient players already preserve
  bats.
- Forest Reserve Keeper is sensitive to the official deck's blank-space
  distribution. It is the strongest current benchmark because it changes
  capacity, sequencing, and resource liquidity together.
- Synthetic Terrain is suitable for legality, capacity, and extreme-value
  checks only; it is not an exact Atiwa balance model.

## Next Required Input

The next design task is to outline at least eight Open Commitments with
distinct playstyle lanes and action-timed claim conditions. Do not convert the
five v0.2 powers mechanically; their intended routes may inspire race goals,
but every v0.3 card must stand on its own as a public achievement.

The official component input needed for that work is specified in
`docs/atiwa_component_transcription_requirements.md`. Transcribe the action
board, all player-count extensions, and the six action-space tiles first so
the initial Commitment conditions can reflect real worker-space competition.
The complete Terrain and Location listings are required before exact-deck
simulation or representative balance claims.

## Workspace State

The uploaded `atiwa/` reference folder and
`New_Frontiers_Tile_List_ver_1_2.xlsx` are untracked user files and were not
modified or included in the Living Landscape implementation commit.
