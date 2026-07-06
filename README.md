# Dice-Galaxy Prototypes

This repository contains a Python rules prototype for a small-box dice galaxy
game with a generic die-face upgrade system, plus Roll for the Galaxy variant
prototypes.

## Roll For The Galaxy Mancala Dice Variant

The main Roll prototype replaces the Dice Cup, roll, and assign steps with a
five-section mancala loop:

```text
Explore -> Develop -> Settle -> Produce -> Ship -> Explore
```

Dice colors remain identities. Blue, brown, red, green, and purple have matching
phase sections; white and yellow are flexible dice that enter a normal phase
section from Spent.

Rules draft:

- `docs/roll_mancala_dice_design.md`
- `docs/roll_mancala_dice_design.pdf`
- `docs/roll_phase_battery_rules.md` for the archived phase-battery branch.

Print-and-play files:

- `pnp/roll-mancala.html`
- `pnp/roll-mancala.pdf`
- `pnp/roll-phase-battery.html` for the archived phase-battery branch.

Run the mancala multiplayer simulator:

```bash
python3 -m roll_mancala.simulate --games 100 --players P1:balanced P2:builder P3:settler P4:shipper
```

The mancala multiplayer default uses an 8 VP chip pool per player and the
normal 12-square tableau end condition. Current tuning targets roughly 14-16
rounds with the five-section loop.

Run the mancala solo campaign simulator:

```bash
python3 -m roll_mancala.solo --games 100 --strategy balanced --campaign outreach
```

Run the archived phase-battery multiplayer simulator:

```bash
python3 -m roll_galaxy.simulate --games 100 --players P1:balanced P2:builder P3:settler P4:shipper
```

Run the archived phase-battery solo campaign simulator:

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
