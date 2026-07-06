# Roll for the Galaxy: Mancala Dice Variant

This is the primary Roll prototype in this repository. It replaces the Dice Cup,
roll, and assignment steps with a five-section mancala loop. The archived
phase-battery rules remain in `docs/roll_phase_battery_rules.md`.

Use the physical dice from the base box as mancala stones. Die faces do not
matter. Die color is still identity for gained dice, lost dice, color bonuses,
and end-game scoring.

## Design Thesis

Dice stay in the mancala economy. They do not become workers, construction
progress, or Goods.

The loop has five sections:

```text
Explore -> Develop -> Settle -> Produce -> Ship -> Explore
```

Core economy:

- Sowing moves stones and selects a phase.
- Stones in a phase section set that phase's strength.
- Credits pay for Develop and Settle.
- Good markers track produced Goods on Worlds.
- Spent is off-board and holds overflow, lost dice, and newly gained dice that
  cannot fit in their matching section.

This keeps the table state readable: the mancala board shows phase pressure,
Credits show construction power, and Good markers show shipping inventory.

## Components

Each player needs:

- one five-section mancala board;
- one off-board Spent area;
- Credits;
- VP chips;
- Good markers;
- their normal tableau, Development queue, and World queue.

Solo mode also needs:

- five Dummy Phase cards: Explore, Develop, Settle, Produce, Ship;
- one Dummy Goods marker;
- a shared VP pool.

## Dice Colors

```text
Blue    Explore identity
Brown   Develop identity
Red     Military / Settle identity
Green   Produce identity
Purple  Ship identity
White   Wild identity
Yellow  Alien identity
```

White and Yellow have no native entry section. When recovered from Spent, choose
which section they enter.

## Setup

For each player:

1. Place 2 Blue stones in Explore.
2. Place 2 Brown stones in Develop.
3. Place 2 Red stones in Settle.
4. Place 2 Green stones in Produce.
5. Place 2 Purple stones in Ship.
6. Place 2 White stones in Spent.
7. Start with 1 Credit.
8. Set up starting Worlds, starting Developments, and queued tiles normally for
   this prototype.

Each section has a capacity of 6 stones. If no section can receive a stone
during sowing, place that stone in Spent.

## Round Structure

Each round:

1. Each player chooses one source: a board section, or one color group in Spent.
2. Each player sows those stones.
3. The final section sown selects that player's phase.
4. All selected phases occur for all players, in normal Roll phase order.
5. Resolve Manage Empire.

There is no Citizenry and no dice assignment area.

## Sowing

When sowing from a board section, pick up every stone in that section and sow
clockwise into later sections, one stone per section.

When sowing from Spent, choose one color group and sow any number of those
stones. Native colors enter their matching section:

```text
Blue -> Explore
Brown -> Develop
Red -> Settle
Green -> Produce
Purple -> Ship
```

White and Yellow may enter any section.

Skip full sections. If every section is full, overflow stones go to Spent.

## Match Bonuses

If the final stone lands in its matching section, mark one phase bonus for that
section this round.

```text
Blue in Explore      +1 Explore action
Brown in Develop     -1 Credit cost this Develop
Red in Settle        -1 Credit cost this Settle
Green in Produce     +1 Produce action
Purple in Ship       +1 VP on the first shipped Good this Ship
```

White and Yellow do not create match bonuses.

## Phase Resolution

Stones stay on the mancala board when phases resolve.

### Explore

Explore actions equal stones in Explore plus the Explore match bonus.

For each action:

1. If your Development queue is empty, scout one Development.
2. Else if your World queue is empty, scout one World.
3. Else gain 2 Credits.

### Develop

Develop completes the top queued Development if you can pay its effective cost.

```text
effective cost =
Development cost
- matching Brown stones in Develop
- White/Yellow stones in Develop
- Develop match bonus
```

Pay the remaining cost in Credits. If you cannot pay, nothing happens to that
Development this phase. No partial progress is kept.

### Settle

Settle works like Develop, but for the top queued World.

```text
effective cost =
World cost
- matching Red stones in Settle
- White/Yellow stones in Settle
- Settle match bonus
```

Pay the remaining cost in Credits. If you cannot pay, nothing happens to that
World this phase. No partial progress is kept.

### Produce

Produce actions equal stones in Produce plus the Produce match bonus.

Each action places one Good marker on an eligible empty production World in your
tableau. The stone remains in Produce. The Good marker is not a die.

### Ship

Ship actions equal stones in Ship.

Each action ships one Good marker. If you have 2 or fewer Credits, trade the
Good for Credits. Otherwise, consume it for VP chips. The Ship match bonus adds
+1 VP to the first Good consumed during this Ship phase.

The shipped Good marker is removed. The Ship stone remains in Ship.

## Manage Empire

During Manage Empire, spend 2 Credits to make one recovery sow from Spent. Repeat
while you can pay and still have stones in Spent.

Credits do not become dice. Credits do not enter the mancala board. Credits pay
construction costs and recover Spent stones.

## Gaining And Losing Dice

When a tile grants a die:

1. Put it in its matching section if there is room.
2. Otherwise put it in Spent.

When a tile removes a die:

1. Remove from Spent first, avoiding colors the tile grants if possible.
2. If needed, remove from a board section.

Goods and construction queues are not dice.

## Card Text Conversion

Use the following translation rules:

- Extra phase worker: add one temporary action or discount for that phase.
- Cost reduction: reduce the Credit cost of the matching Develop or Settle.
- Gain Credits: gain Credits normally, up to the Credit cap.
- Produce a Good: place a Good marker on an eligible World.
- Trade or Consume: use Ship actions and Good markers.
- Reassign a die: move an unused stone between board sections only if the text
  clearly supports moving a die.
- Dice-count scoring: count physical dice in board sections and Spent only.

Ignore text that would place a die as lasting construction progress. This
variant does not track partial builds.

## Multiplayer Notes

All selected phases are shared. If one player selects Develop, every player may
resolve Develop. A player can benefit from a phase even if they did not select
it, as long as they have the relevant stones, Credits, queued tile, or Goods.

The current prototype settings are:

```text
Section capacity:       6
Starting stones:        2 per normal phase section
Starting white stones:  2 in Spent
Starting yellow stones: 0
Starting Credits:       1
Recovery sow cost:      2 Credits
VP pool:                8 per player
Tableau end trigger:    12 cards
```

Recent smoke simulation with four strategies averaged about 10 rounds and
showed no recurring dead-round jam.

## Solo Mode

Solo mode uses the same player rules and adds a simple dummy phase deck.

Setup:

1. Build a five-card Dummy Phase deck: Explore, Develop, Settle, Produce, Ship.
2. Shuffle it.
3. Set the VP pool to 30.
4. Play up to 16 rounds.

Each round:

1. You sow and select one phase.
2. Draw 2 Dummy Phase cards.
3. Resolve your selected phase plus the dummy phases, in normal phase order.
4. Resolve the dummy effects.
5. Resolve Manage Empire.
6. If the Dummy deck cannot supply 2 cards, reshuffle all five Dummy Phase cards.

Dummy effects:

```text
Explore   Dummy claims one Development and one World from the tile bag.
Develop   Dummy claims one Development.
Settle    Dummy claims one World.
Produce   Dummy Goods +1, max 4.
Ship      Drain 2 VP per Dummy Good, minimum 2, then Dummy Goods = 0.
```

Solo ends when any of these happen:

- you reach 12 tableau cards;
- the VP pool is empty;
- round 16 ends.

## Solo Scenarios

Score scenarios:

```text
Great       38+ VP
Triumphant  42+ VP
Epic        46+ VP
```

Named scenarios require at least 34 VP plus the listed mark:

```text
Builder             7+ completed tiles
Developer           4+ Developments
Colonizer           6+ Worlds
Shipper             8+ VP chips
Expanded Workforce  17+ owned dice
Producer            4+ production Worlds
Diversified Economy 3+ distinct World colors
Phase Specialist    3+ color match bonuses
Credit Economy      18+ Credits spent
Logistics           2+ recovery sows
Phase Momentum      65+ phase actions
```

Owned dice means physical dice in your mancala sections plus Spent. Good markers
and queued tiles do not count. Phase actions are actions produced by stones in
resolved phase sections, including bonus actions from match bonuses.

## Solo Campaigns

A campaign is four consecutive games. Each game must mark one campaign scenario
not already marked. Win the campaign by marking all four scenarios.

```text
Frontier Survey
  Great, Colonizer, Diversified Economy, Phase Specialist

Core Worlds Renaissance
  Triumphant, Developer, Builder, Credit Economy

Trade League
  Triumphant, Producer, Shipper, Diversified Economy

Supply Lines
  Great, Expanded Workforce, Logistics, Phase Momentum

Colonial Boom
  Great, Colonizer, Producer, Logistics

Industrial Mobilization
  Epic, Expanded Workforce, Credit Economy, Phase Momentum

Imperial Prestige
  Epic, Builder, Shipper, Phase Specialist

Galactic Mastery
  Epic, Credit Economy, Logistics, Phase Momentum
```

Campaign story hooks:

- Frontier Survey: chart a scattered sector and turn discoveries into a working
  colony network.
- Core Worlds Renaissance: rebuild the home cluster through Developments,
  infrastructure, and Credit discipline.
- Trade League: make production and shipping the center of galactic influence.
- Supply Lines: keep a wide empire supplied through workforce growth and
  repeated recovery.
- Colonial Boom: expand fast, then make the new Worlds produce.
- Industrial Mobilization: push a large workforce and Credit economy into an
  Epic-scale engine.
- Imperial Prestige: convert visible accomplishments into prestige before the
  Dummy drains the sector.
- Galactic Mastery: a hard economy-control arc for strong solo play.

Current balanced-strategy tuning target:

```text
Frontier Survey / Trade League / Colonial Boom: approachable campaign wins
Core Worlds / Supply Lines / Industrial Mobilization / Imperial Prestige / Mastery:
  harder economy and prestige campaigns
```

## Current Test Coverage

The automated tests cover:

- five-section setup and Spent;
- board sowing and Spent recovery;
- phase sharing;
- Develop/Settle Credit costs and section discounts;
- match bonuses;
- Produce Good markers without moving stones;
- Ship Good markers without moving stones;
- solo dummy phase selection;
- solo capacity counting and campaign definitions.
