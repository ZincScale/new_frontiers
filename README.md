# Dice-Galaxy Prototypes

This repository contains a Python rules prototype for a small-box dice galaxy
game with a generic die-face upgrade system, plus a Roll for the Galaxy
phase-battery variant prototype.

## Roll For The Galaxy Phase Battery

The Roll prototype replaces face-roll luck with deterministic phase-capacity
tracks. Dice colors become rechargeable batteries for Explore, Develop, Settle,
Produce, Ship, Wild, and Alien work.

Rules draft:

- `docs/roll_phase_battery_rules.md`
- `docs/roll_phase_battery_rules.pdf`

Print-and-play files:

- `pnp/roll-phase-battery.html`
- `pnp/roll-phase-battery.pdf`

Run the multiplayer simulator:

```bash
python3 -m roll_galaxy.simulate --games 100 --players P1:balanced P2:builder P3:settler P4:shipper
```

The multiplayer default uses a 16 VP chip pool per player and the normal
12-square tableau end condition. Use `--vp-pool-per-player 12` to compare
against the base game's VP pool size.

Compare Alien Yellow with Yellow-as-Ship:

```bash
python3 -m roll_galaxy.simulate --games 100 --yellow-mode alien --players P1:balanced P2:builder P3:settler P4:shipper
python3 -m roll_galaxy.simulate --games 100 --yellow-mode ship --players P1:balanced P2:builder P3:settler P4:shipper
```

Run the solo campaign simulator:

```bash
python3 -m roll_galaxy.solo --games 100 --strategy balanced --campaign outreach
```

The Roll simulator uses `Roll_for_the_Galaxy_all_tiles.xls`:

- first sheet: 110 non-start tiles;
- second sheet: 9 faction pairs and 9 home worlds.

## Tiny Galaxies Upgrade Prototype

The Tiny Galaxies prototype explores a generic die-face upgrade system.

The design goal is to add federation identity without changing the base game's
component burden:

- keep the original dice;
- add a planet deck and shared planet market;
- add a generic market of upgrade cards;
- limit each player to three upgrades;
- tie each upgrade to one die face;
- use Rival Empire profiles and difficulty cards for solo variety.

The prototype is intentionally compact. It is meant to verify the full Python
game loop before pivoting the implementation to C# and Blazor for online play.

## Rules Draft

See `docs/tiny_galaxies_upgrade_rules.md`.

## Print And Play

Open `pnp/print-and-play.html` in a browser and print at 100% scale. The PnP
package includes upgrade cards, Rival Empire profiles, difficulty cards, and
reference cards.

## Current Content

- 40 base-game planet cards, sourced from `bgg161447.pdf`.
- 12 generic upgrade cards.
- 4 internal empire strategy profiles for simulation.
- 4 Rival Empire profiles.
- Planet market scales as players + 2, capped at 6.
- 3-card upgrade market.
- 3-upgrade limit.
- Empire level track with increasing dice, ships, and VP.
- Resource cap, planet surface landings, ships on orbit tracks, free reroll,
  and converter hooks.
- Seat-rotated simulator output with play-pattern metrics such as colonies,
  active presence, and zero-colony finish rate.

## Run a Simulation

```bash
python3 -m tiny_galaxies.simulate --games 20
```

Run the baseline model without the upgrade-card expansion:

```bash
python3 -m tiny_galaxies.simulate --games 20 --no-upgrades
```

Try four asymmetrical empires:

```bash
python3 -m tiny_galaxies.simulate --games 20 --players frontier_union:mobility star_cartel:economy archive_compact:culture settlement_charter:colonizer
```

The simulator rotates player order by default. Use `--fixed-seats` only when
debugging seat-order effects.

Run the Rival Empire solo simulator:

```bash
python3 -m tiny_galaxies.solo_simulate --games 100 --profile all --difficulty standard
```

The solo simulator uses the regular Galaxy mat side for the automated opponent
and explicit difficulty cards: `training`, `standard`, `advanced`, and
`expert`.

Override Rival starting values for tuning:

```bash
python3 -m tiny_galaxies.solo_simulate --games 100 --profile all --difficulty standard --rival-vp 2 --rival-energy 2 --rival-culture 1
```

Sweep multiple values:

```bash
python3 -m tiny_galaxies.solo_simulate --games 100 --profile all --difficulty standard --sweep-vp 0,2,4 --sweep-culture 1,2
```

## Run Tests

```bash
python3 -m pytest
```
