# Tiny Galaxy Upgrade Module Draft

This is a low-component upgrade module for a small-box dice galaxy game. It is
written to sit on top of the base game's planets, dice, ships, Galaxy mats,
energy, culture, and colony tracks. The digital prototype lives in
`tiny_galaxies`.

## Components

- 36 planet cards.
- 12 generic upgrade cards.
- 4 Rival Empire profile cards.
- 4 Rival difficulty cards.
- Reference cards for upgrade and Rival Empire procedures.
- 4 ships per player.
- Six-sided dice using the prototype faces: Move, Energy, Culture, Economy,
  Diplomacy, Colony.

## Setup

1. Shuffle the upgrade cards if playing with the upgrade module.
2. Reveal three upgrade cards as a shared upgrade market.
3. Shuffle the planet cards.
4. Reveal two more planets than the player count, capped at six planets.
5. For solo play, give the automated opponent one Rival Empire profile and one
   Rival difficulty card.

## Turn Loop

On your turn, roll dice based on your empire level and use each die once.

- Move a Ship: move one ship from your Galaxy mat to a planet card. The ship
  may land on the planet surface or move to the planet's orbit track. In the
  prototype, if none of your ships are on your Galaxy mat, a Move a Ship die may
  return one of your landed ships to your Galaxy mat.
- Acquire Energy: gain energy from your empire.
- Acquire Culture: gain culture from your empire.
- Advance Economy: advance one of your ships on an economy colony track.
- Advance Diplomacy: advance one of your ships on a diplomacy colony track.
- Utilize Colony: use your Galaxy mat action to upgrade your empire, activate a
  colonized planet, or trigger an upgrade tied to this die face.

Resources are capped at 7.

When your ship reaches the end of a planet's colony track, colonize that planet:
place it with your colonized planets, score its VP, resolve its ability, return
the ship to your Galaxy mat, and refill the planet market.

## Dice Control

The model includes two dice-control mechanisms:

- One free reroll of weak/unusable faces each turn.
- A converter hook that spends two dice to turn another die into Move a Ship
  when you have no useful way to place a ship onto a planet.

These are intentionally simple in Python so we can tune how much randomness
comes from setup and card markets rather than from helpless rolls.

If playing with upgrade cards, the converter is only available while you have
fewer than two upgrades. After that point, your colonized planets and upgrades
are expected to provide your dice control.

## Emergency Protocol

Fallback colony-track advancement is not part of the Utilize Colony die. It is
an explicit escape hatch:

- If none of your used dice can advance any of your ships on colony tracks, you
  may spend 1 culture to advance one of those ships 1 space.
- This keeps the die face focused on empire and planet abilities while still
  preventing helpless turns.

## Empire Growth

Empire level is part of the base model. Higher levels increase available dice,
unlock more ships, and add VP. This is separate from upgrade cards.

Empire VP is capped by colonies: each colonized planet supports up to 3 empire
VP. A max-level empire with no colonies scores 0 empire VP. This keeps empire
growth from replacing your colonized planets as the main expression of your
federation.

## Buying Upgrades

At the end of your turn, you may spend 3 energy or 3 culture to buy one face-up
upgrade card from the market. Refill the market immediately.

Each player may have at most three upgrades. Upgrade cards are first come, first
serve: when a player buys one, it leaves the shared market and no other player
can buy that copy.

## Upgrade Timing

Each upgrade is tied to one die face. The upgrade triggers only when you use a
die showing that face.

The default prototype pattern is:

> When you use this die face, also do one small extra thing.

This keeps the dice recognizable while letting each empire specialize.

The upgrade-card module can be disabled in the simulator with `--no-upgrades`.

## Upgrade Cards

Move a Ship upgrades:

- Warp Couriers: after you use a Move a Ship die, if the moved ship is on a
  planet's orbit track, gain 1 energy or 1 culture.
- Frontier Beacons: after you use a Move a Ship die, choose one of your ships on
  a planet's orbit track. Advance it 1 space if either it has already advanced
  at least 1 space, or you have no colonized planets and spend 1 energy.

Acquire Energy upgrades:

- Orbital Refineries: after you use an Acquire Energy die, gain 1 additional
  energy. If you were already at the energy cap, advance one of your ships on an
  economy colony track 1 space.
- Fusion Tithes: after you use an Acquire Energy die, gain 1 VP if you have at
  least two colonized planets.

Acquire Culture upgrades:

- Cultural Archives: after you use an Acquire Culture die, gain 1 additional
  culture if you have at least one colonized planet. If you were already at the
  culture cap, advance one of your ships on a diplomacy colony track 1 space.
- Soft Power Networks: the first time each turn you use an Acquire Culture die,
  advance one of your ships on a diplomacy colony track 1 space.

Advance Economy upgrades:

- Trade League: after you use an Advance Economy die, gain 1 culture.
- Merchant Convoys: after you use an Advance Economy die, gain energy equal to
  your colonized planets, max 2. If you were already at the energy cap and
  gained at least 1 energy this way, advance one of your ships on an economy
  colony track 1 space.

Advance Diplomacy upgrades:

- Envoy Corps: after you use an Advance Diplomacy die, advance one of your ships
  on a diplomacy colony track 1 additional space.
- Charter Worlds: when an Advance Diplomacy die causes you to colonize a planet,
  gain 1 VP.

Utilize Colony upgrades:

- Colony Prefabs: after you use a Utilize Colony die, advance one of your ships
  on a colony track 1 space. If you have no ships on colony tracks, you may
  spend 2 energy to move one ship from your Galaxy mat to a planet's orbit
  track. If you have no colonized planets, you may spend 2 culture for this
  effect.
- Settler Mandate: when a Utilize Colony die causes you to colonize a planet,
  gain 1 culture and 1 VP.

## Deferred: Player Empire Cards

Player Empire cards are not part of the current PnP package. The current PnP
focus is the upgrade market plus Rival Empire solo mode. Player asymmetry can be
tested later if the upgrade module needs more multiplayer identity.

## Rival Empire Solo Mode

For solo play, skip the official Rogue Galaxy side and use the regular Galaxy
mat side for the automated opponent. At setup, give the automated opponent one
Rival Empire profile and one difficulty card. The profile changes what the
rival prioritizes and adds one pressure rule.

The digital prototype currently uses these Rival difficulty cards:

- Training: empire level 1, 1 energy, 1 culture, 0 VP.
- Standard: empire level 1, 2 energy, 1 culture, 2 VP.
- Advanced: empire level 1, 3 energy, 1 culture, 4 VP.
- Expert: empire level 1, 3 energy, 1 culture, 6 VP.

These difficulty assumptions are deliberately explicit so Rival Empire behavior
can be tested separately from difficulty tuning.

Rival turn procedure:

1. Roll dice based on the Rival's empire level.
2. Resolve dice in the order shown on the Rival Empire card's Dice Priority.
3. Skip a die only if it cannot do anything useful.
4. Move a Ship places a ship on the best planet for that Rival profile. If the
   Rival is low on resources, it may land on the surface; otherwise it goes to
   the orbit track.
5. Advance Economy and Advance Diplomacy advance an orbiting ship on a matching
   colony track.
6. Utilize Colony upgrades empire if affordable. If not, it uses a colonized
   planet ability if useful.
7. At end of turn, the Rival buys the best affordable upgrade from the shared
   market if it has fewer than three upgrades.
8. When the Rival colonizes, score the planet and resolve its pressure rule.

- Devourer Swarm: races for short colony tracks. When it colonizes, move one of
  your orbiting ships 1 space backward if able.
- Iron Directorate: prioritizes empire growth and infrastructure. When it
  colonizes, you lose 1 of your highest resource.
- Void Corsairs: contests rich resource planets. When it colonizes, you lose 1
  of your highest resource and the Rival gains that resource.
- Oracle Singularity: prioritizes culture and diplomacy. When it colonizes, you
  cannot use Follow for the rest of the round.

In the digital prototype, each Rival profile also has a once-per-turn momentum
rule: if the Rival used its signature die face that turn, it gains one small
extra push matching its identity.

## Digital Prototype

Run a sample simulation:

```bash
python3 -m tiny_galaxies.simulate --games 20
```

Run without the upgrade module:

```bash
python3 -m tiny_galaxies.simulate --games 20 --no-upgrades
```

Try four asymmetrical empires:

```bash
python3 -m tiny_galaxies.simulate --games 20 --players frontier_union:mobility star_cartel:economy archive_compact:culture settlement_charter:colonizer
```

Try the Rival Empire solo mode:

```bash
python3 -m tiny_galaxies.solo_simulate --games 100 --profile all
```

Choose a Rival difficulty:

```bash
python3 -m tiny_galaxies.solo_simulate --games 100 --profile all --difficulty standard
```

Tune a difficulty card without editing source:

```bash
python3 -m tiny_galaxies.solo_simulate --games 100 --profile all --difficulty standard --rival-vp 2 --rival-energy 2 --rival-culture 1
```

Sweep multiple candidate settings:

```bash
python3 -m tiny_galaxies.solo_simulate --games 100 --profile all --difficulty standard --sweep-vp 0,2,4 --sweep-culture 1,2
```

The current digital prototype abstracts the base game. It is intended to test
whether colonized planets plus a three-card generic upgrade market create
distinct empire identities without adding many components.
