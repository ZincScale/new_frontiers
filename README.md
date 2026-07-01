# Dice-Galaxy Full Game Prototype

This repository contains a Python rules prototype for a small-box dice galaxy
game with a generic die-face upgrade system.

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

- 36 planet cards.
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
