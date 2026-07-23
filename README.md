# Roll for the Galaxy: Phase Battery

This repository contains Phase Battery, the main deterministic way to play
Roll for the Galaxy.

## Roll For The Galaxy Phase Battery Variant

Phase Battery is the main Roll for the Galaxy variant. It keeps secret phase
selection but replaces rolled dice with deterministic phase batteries.
Selected phases resolve in normal order:

```text
Explore -> Develop -> Settle -> Produce -> Ship
```

Players may only select a phase if they have at least one ready pip for that
phase. Solo selects two eligible phases; every multiplayer game, including 2p,
has each player select one. During selected phases, players act in turn order,
spending usable pips or passing. Selecting a phase does not spend pips.

Blue, Brown, Red, Green, and Purple begin at `1/1`; Yellow begins at `0/0`.
There is no White track. Red pays the full construction cost of every World.
Credits are unlimited chips like base Roll, and the VP pool contains `7` chips
per player. Scout spends N Blue to inspect N + 3 candidates and keep one.
Six-cost Developments are delayed end-game goals. Printed Cup, Citizenry, and
World placement determines whether new capacity begins ready, waits for Credit
recharge, or begins as a Good.

Rules draft:

- `docs/roll_phase_battery_rules.md`
- `docs/roll_phase_battery_rules.pdf`

Print-and-play files:

- `pnp/roll-phase-battery.html`
- `pnp/roll-phase-battery.pdf`

Run the active multiplayer simulator:

```bash
python3 -m phase_battery.simulate --games 100 --players P1:balanced P2:builder P3:settler P4:producer P5:shipper
```

Run the active solo simulator:

```bash
python3 -m phase_battery.solo --games 100 --strategy balanced --difficulty normal
```

The Roll simulator uses `Roll_for_the_Galaxy_all_tiles.xls`:

- first sheet: 110 non-start tiles;
- second sheet: 9 faction pairs and 9 home worlds.

## Run Tests

```bash
python3 -m pytest
```
