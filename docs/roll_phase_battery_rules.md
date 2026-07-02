# Roll for the Galaxy: Phase Battery Variant

This variant replaces face-roll luck with deterministic phase capacity. Players
still build a tableau of Worlds and Developments, select phases secretly, pay
Galactic Credits, Produce Goods, Ship Goods, and score VP chips. The big change
is that dice colors become phase tracks instead of rolled workers.

Core rule:

> When a tile says to gain a die, pip up that color track.

There is no Roll Dice step, no Assign Dice step, no Dice Cup, and no Citizenry.

## Current Design Decision

The recommended minimal ruleset is:

- dice colors become deterministic phase batteries;
- each track has current pips and max pips;
- gaining a die increases that color's max and current pips by 1;
- Credits recharge spent pips during Manage Empire;
- White remains wild;
- Yellow is Alien-specific by default.

The goal is not to make a new Roll for the Galaxy game. It is to keep phase
selection, tile building, goods, shipping, credits, VP chips, and tableau
scoring intact while removing the roll-and-reassign luck layer.

For the first playtest, do not add free recharge, tile-specific retuning, or a
new dummy-player system. Those are tuning knobs after the core battery loop is
tested at the table.

## Components

Use all normal Roll for the Galaxy components except the Dice Cups.

Add one Phase Battery board per player. Each board has tracks from 0 to 6:

```text
Explore   Blue    0 1 2 3 4 5 6
Develop   Brown   0 1 2 3 4 5 6
Settle    Red     0 1 2 3 4 5 6
Produce   Green   0 1 2 3 4 5 6
Ship      Purple  0 1 2 3 4 5 6
Wild      White   0 1 2 3 4 5 6
Alien     Yellow  0 1 2 3 4 5 6
```

Each color has two values:

- Current pips: how many pips are available to spend now.
- Max pips: the highest that color can recharge to.

Recommended physical tracking:

- Put the colored die on the track to show current pips.
- Put a cube or marker on the track to show max pips.

Example:

```text
Red track: 0 1 2 3 4 5 6
              D   M
```

The red die is on 2 and the max marker is on 4, so Red is `2/4`.

## Color Map

Use these phase mappings:

```text
Blue    Explore
Brown   Develop
Red     Settle
Green   Produce
Purple  Ship
White   Wild
Yellow  Alien
```

Yellow is not a normal phase. It starts at `0/0` and is used only for Alien
work, explained under Yellow / Alien Pips.

## Setup

Set up the base game normally, with these changes:

1. Do not give players Dice Cups.
2. Do not put dice in the Cup or Citizenry.
3. Give each player a Phase Battery board.
4. Set starting tracks:

```text
Blue    2/2
Brown   2/2
Red     2/2
Green   2/2
Purple  2/2
White   2/2
Yellow  0/0
```

Then set up starting tiles normally:

1. Give each player one Faction tile.
2. Give each player one Home World tile.
3. Apply any starting die gains from those tiles as pips.
4. Draw starting Game Tiles into the Construction Zone as usual: one
   Development stack and one World stack.

Example:

```text
Starting Red is 2/2.
Your Home World grants one Military die.
Military maps to Red.
Red becomes 3/3.
```

If a starting tile places a die as a Good on that World, place a Good marker on
that World and pip up the granted color normally.

## Round Structure

Each round has four steps:

1. Select Phases
2. Reveal Phases
3. Do Selected Phases in Order
4. Manage Empire

There is no Roll Dice step and no Assign Dice step.

## 1. Select Phases

Each player secretly selects one phase on their Phase Strip:

```text
I   Explore
II  Develop
III Settle
IV  Produce
V   Ship
```

Players may not openly discuss which phase they will select, as in the base
game.

## 2. Reveal Phases

Reveal selected phases simultaneously.

Every phase selected by at least one player will occur this round. In a 2-player
game, use the base game's dummy phase rule if desired; for the first playtest,
skip the dummy phase unless the game feels too tight.

## 3. Do Selected Phases In Order

Resolve selected phases in normal Roll order:

```text
Explore -> Develop -> Settle -> Produce -> Ship
```

When a phase occurs, every player may spend pips for that phase, even if they
did not select it.

Spend one current pip for one worker use.

```text
Spend 1 Blue pip   = one Explore worker
Spend 1 Brown pip  = one Develop worker
Spend 1 Red pip    = one Settle worker
Spend 1 Green pip  = one Produce worker
Spend 1 Purple pip = one Ship worker
Spend 1 White pip  = one worker in any selected phase
```

Spend pips one at a time. Stop when you run out of pips or cannot use more of
that phase.

## Example Round

Your tracks:

```text
Blue    1/2
Brown   0/2
Red     3/3
Green   2/2
Purple  1/2
White   2/2
Yellow  0/0
```

You select Settle. Other players select Develop and Ship.

Selected phases:

```text
Develop, Settle, Ship
```

You may:

- Develop with Brown. Brown is empty, so you may spend White instead.
- Settle with Red.
- Ship with Purple, or White if Purple runs out.

After spending:

```text
Brown   0/2
Red     2/3
Purple  0/2
White   1/2
```

## Explore

When Explore occurs, spend Blue or White pips.

Each pip may be used for one normal Explore worker:

- Scout
- Stock

Example:

```text
Blue is 2/2.
You spend 1 Blue to Scout.
You spend 1 Blue to Stock.
Blue becomes 0/2.
```

## Develop

When Develop occurs, spend Brown or White pips.

Each pip adds one Developer to the top tile of your Development stack.

If the number of Developers on that tile equals its cost, complete the
Development:

1. Move it to your tableau.
2. Apply any immediate converted effects.
3. Continue spending remaining Develop pips on the next Development if able.

Use normal Development costs. Six-cost Developments cost 6.

Example:

```text
Brown is 2/2.
Your top Development costs 2.
Spend 2 Brown.
Complete the Development.
Brown becomes 0/2.
```

## Settle

When Settle occurs, spend Red or White pips.

Each pip adds one Settler to the top tile of your World stack.

If the number of Settlers on that tile equals its cost, complete the World:

1. Move it to your tableau.
2. Gain any dice listed on the World by pipping up those colors.
3. Gain any listed Galactic Credits.
4. Place a starting Good if the tile's die placement says the die begins on the
   World.
5. Continue spending remaining Settle pips on the next World if able.

Example:

```text
Red is 2/2.
Your top World costs 2 and grants one Novelty die.
Spend 2 Red to complete it.
Novelty maps to Blue.
Blue 2/2 becomes 3/3.
Red becomes 0/2.
```

## Produce

When Produce occurs, spend Green or White pips.

Each pip produces one Good on an eligible non-gray World in your tableau.

Instead of placing a worker die as the Good, place a Good marker, cube, or spare
die on the World.

The Good's color is the color of the pip spent:

```text
Green pip = Green Good
White pip = Wild Good
Yellow pip = Yellow Good, only if using Yellow for Alien Produce
```

Each World can hold one Good unless a tile power says otherwise.

Example:

```text
Green is 2/2.
You have two empty colored Worlds.
Spend 2 Green.
Place two Goods.
Green becomes 0/2.
```

## Ship

When Ship occurs, spend Purple or White pips.

Each pip Ships one Good. For each Good, choose Trade or Consume as in the base
game.

For matching, use the Good marker's color:

- A Good always gives at least 1 VP when Consumed.
- +1 VP if the Good color matches the World color.
- White Goods count as matching.

Purple is the normal Ship color. White is wild.

Example:

```text
Purple is 2/2.
You have two Goods.
Spend 1 Purple to Trade one Good for Credits.
Spend 1 Purple to Consume one Good for VP.
Purple becomes 0/2.
```

## Gaining Dice

Whenever a tile says to gain a die, pip up that die color instead.

Procedure:

1. Increase that color's max by 1.
2. Increase that color's current pips by 1.
3. The max cannot exceed 6.
4. Any gain beyond 6 is lost.

Color conversion:

```text
Home              White
Novelty           Blue
Rare Elements     Brown
Genes             Green
Alien Technology  Yellow
Military          Red
Consumption       Purple
```

Examples:

```text
Red is 2/2.
You gain one Military die.
Red becomes 3/3.
```

```text
Green is 0/2.
You gain one Genes die.
Green becomes 1/3.
```

```text
Blue is 6/6.
You gain one Novelty die.
Blue stays 6/6. The excess is lost.
```

If a tile grants two dice, pip up both colors. If both dice are the same color,
pip that color twice, still capped at 6.

## Losing Dice

Whenever a tile says to lose or remove a die, reduce one track by 1 max.

If the track's current pips are now above its max, lower current pips to the new
max.

For the first playtest, choose the lost color this way:

1. If the tile specifies a die color, reduce that color.
2. If it does not specify a color, the player chooses one color with max above
   0.

Example:

```text
Red is 3/4.
You must lose one Military die.
Red becomes 3/3.
```

```text
Blue is 5/5.
You lose one Novelty die.
Blue becomes 4/4.
```

## Yellow / Alien Pips

Yellow represents Alien Technology.

Yellow starts at `0/0`. When you gain an Alien Technology die, pip up Yellow.

Current recommended rule:

Yellow may be spent only when the work involves an Alien tile or Alien Good.

Yellow can pay for:

- Develop, if the top Development is Alien-tagged.
- Settle, if the top World is Alien Technology.
- Produce, if producing on an Alien Technology World.
- Ship, if Shipping a Good from an Alien Technology World.

Yellow cannot pay for unrelated non-Alien work.

Example:

```text
Yellow is 1/1.
Your top World is Deserted Alien Colony.
Settle is selected.
You may spend 1 Yellow as a Settler for that World.
Yellow becomes 0/1.
```

Example:

```text
Yellow is 1/1.
Your top World is Gem World.
Settle is selected.
You may not spend Yellow, because Gem World is not Alien.
```

Simple alternative:

If the Alien rule is too fiddly, treat Yellow as extra Ship capacity:

```text
Ship spending order: Purple -> Yellow -> White
```

The simulator supports both versions. The current default is Alien mode.

## Galactic Credits And Recharge

Galactic Credits no longer recruit dice from Citizenry.

During Manage Empire:

1. Spend Galactic Credits to recharge tracks.
2. Each Credit recharges 1 current pip on one track.
3. A track cannot recharge above its max.
4. You may distribute Credits among tracks however you choose.
5. If your Credit marker is at 0 after Manage Empire, set it to 1 as in the
   base game.

There is no free recharge in the recommended version.

Example:

```text
You have 3 Galactic Credits.

Brown is 0/2.
Red is 1/3.
Purple is 2/2.

Spend 2 Credits: Brown 0/2 -> 2/2.
Spend 1 Credit: Red 1/3 -> 2/3.
Purple is already full, so you cannot recharge it.
```

## Construction Zone And Tableau

Use the normal Construction Zone rules:

- Game Tiles in the Development stack are built by Develop pips.
- Game Tiles in the World stack are built by Settle pips.
- Completed tiles move to your tableau.
- The game end condition still checks tableau size as normal.

For this variant, starting Faction and Home World tiles count normally for game
end and scoring, as in the base game.

## Reassign Powers

Ignore reassign powers.

There is no Assign Dice step, so these powers have no timing window. They mostly
exist in the base game to repair bad faces, and this variant removes bad faces.
Development tiles with only reassign text still count for cost, VP, tableau
size, tags, and end-game bonuses.

## Other Tile Power Conversion

Use these conversions until each tile is individually tuned:

```text
Gain/recruit a die:
Pip up the listed color.

Place a die in your Cup:
Pip up that color.

Place a die in your Citizenry:
Pip up that color.

Place a die on a World as a Good:
Pip up that color and place a matching Good on that World.

Act as if you have an extra worker:
Gain 1 temporary pip in that phase this round.

Reduce a Develop or Settle cost:
Reduce the number of pips required by that amount.

Gain Credits:
Gain Galactic Credits normally.
```

## End Of Game And Scoring

Use normal Roll for the Galaxy end conditions:

- the initial VP chip pool is exhausted; or
- any player has 12 or more tile squares in their tableau.

Finish the round, then score normally:

- VP chips;
- World and Development VP;
- 6-cost Development bonuses, converted as closely as possible.

For a 6-cost Development bonus that refers to dice you own, count color
presence, not max pips.

Max pips are phase capacity. They are not extra physical dice for scoring.

Use this conversion:

- A color track with max above 0 counts as one die of that color.
- A color track never counts as more than one die, no matter how high its max
  is.
- Blue, Brown, Red, Green, Purple, and White usually count as present from
  setup.
- Yellow counts only if you have gained at least one Alien Technology pip.
- If a bonus counts total dice owned, count present color tracks, maximum 7.
- If a bonus counts dice of a specific color, that color contributes either 0
  or 1.

Examples:

```text
Red max 4 = you own 1 Military die for bonus scoring.
Blue max 3 = you own 1 Novelty die for bonus scoring.
Yellow max 0 = you own 0 Alien Technology dice for bonus scoring.
Yellow max 2 = you own 1 Alien Technology die for bonus scoring.
```

This keeps color-identity bonuses meaningful without letting battery capacity
double as an end-game scoring multiplier.

## Solo Mode: Challenge Deck

Solo mode uses the normal Phase Battery rules with a fixed clock, dummy phase
cards, challenge cards, and graded result tiers. This follows the solo style of New Frontiers:
Starry Rift and Jump Drive: Terminal Velocity: you are not racing an automa
score. You are trying to build the right empire before time runs out.

Additional components:

- five Dummy phase cards: Explore, Develop, Settle, Produce, Ship;
- one Dummy claimed-tile row;
- one Dummy Goods marker;
- one solo challenge card.

Setup:

1. Set up one normal player area.
2. Use a 30 VP chip pool.
3. Set Dummy Goods to 0.
4. Shuffle the five Dummy phase cards into a face-down deck.
5. Choose one challenge card.

Result tiers:

```text
Success      Score 31+ VP.
Great        Score 37+ VP.
Triumphant   Score 38+ VP.
Epic         Score 41+ VP.
```

Recommended challenge cards:

```text
Score Challenge     Meet the score threshold.
Builder Challenge   Meet the score threshold and complete 7+ tiles.
Settler Challenge   Meet the score threshold and have 10+ tableau tiles.
Merchant Challenge  Meet the score threshold and score 10+ VP chips.
Engine Challenge    Meet the score threshold and have 16+ total max pips.
```

For a non-score challenge, the extra requirement is the same for every result
tier. The tier is determined by your final score.

Solo round structure:

1. Select your phase normally.
2. Reveal two Dummy phase cards. If the deck is empty, shuffle all five Dummy
   phase cards to form a new deck first.
3. The selected phases this round are your selected phase plus the Dummy phases.
4. Resolve selected phases in normal Roll order. You may spend pips in any
   selected phase.
5. Resolve both Dummy phase effects.
6. Manage Empire normally.

The Dummy never spends pips, never has Credits, never builds an empire, never
scores, and never uses tile powers. It exists to add phase uncertainty, drain
some VP chips, and churn the tile bag.

Dummy card effects:

```text
Explore:  Claim 1 Development tile and 1 World tile from the bag.
Develop:  Claim 1 Development tile from the bag.
Settle:   Claim 1 World tile from the bag.
Produce:  Dummy Goods +1, max 4.
Ship:     Drain 2 VP chips per Dummy Good, then set Dummy Goods to 0.
           If Dummy Goods is 0, drain 2 VP chips anyway.
```

When the Dummy claims a tile, draw the first matching tile from the bag and
place it face down in the Dummy row. Do not read or resolve the tile. If no
matching tile remains in the bag, skip that claim.

The Dummy's claimed tiles do not trigger the 12-tile tableau end condition. They
exist only to keep the bag moving at a multiplayer-like pace.

Solo end conditions:

- the round limit is reached;
- the VP chip pool is exhausted;
- your tableau reaches 12 or more tile squares.

Finish the round, then check your challenge card. Your result is the highest
tier whose score threshold you reached while also meeting that challenge's
extra requirement, if any.

Solo example:

```text
Challenge: Builder.
To get any listed result, complete 7+ tiles.
Your final score determines the tier: Success 31, Great 37, Triumphant 38,
or Epic 41.

You select Settle.
Dummy reveals Produce and Develop.

Selected phases: Develop, Settle, Produce.

You may spend Brown pips during Develop.
You may spend Red pips during Settle.
You may spend Green pips during Produce.

Dummy resolves Produce: Dummy Goods 0 -> 1.
Dummy resolves Develop: draw one Development tile from the bag and place it
face down in the Dummy row.
```

Later:

```text
Dummy reveals Explore and Ship.

Explore: draw one Development and one World from the bag into the Dummy row.
Ship: Dummy has 1 Good, so drain 2 VP chips and set Dummy Goods to 0.
```

Current solo simulation with the recommended defaults:

```text
All difficulties use 12 rounds and two Dummy phase cards per round.
Average Dummy churn: about 19 claimed tiles and 12 drained VP chips.
For the Score Challenge with the balanced heuristic, Success is about 90%,
Great about 60%, Triumphant about 50%, and Epic about 30%.
```

Run:

```bash
python3 -m roll_galaxy.solo --games 100 --strategy balanced --challenge score
```

## Full Round Example

Initial tracks:

```text
Blue    2/2
Brown   2/2
Red     2/2
Green   2/2
Purple  2/2
White   2/2
Yellow  0/0
Credits 1
```

Your Home World grants one Military die:

```text
Red 2/2 -> 3/3
```

Round 1 phase selection:

```text
You choose Settle.
Opponent A chooses Explore.
Opponent B chooses Develop.
Opponent C chooses Settle.
```

Selected phases:

```text
Explore, Develop, Settle
```

Explore:

```text
Spend 1 Blue to Scout.
Blue 2/2 -> 1/2.
```

Develop:

```text
Spend 2 Brown on a cost-2 Development.
Brown 2/2 -> 0/2.
Complete the Development.
```

Settle:

```text
Spend 3 Red on a cost-3 World.
Red 3/3 -> 0/3.
Complete the World.
The World grants one Genes die.
Green 2/2 -> 3/3.
```

Manage Empire:

```text
Credits 1.
Recharge Brown 0/2 -> 1/2.
Credits would become 0, so reset to 1.
```

End of round tracks:

```text
Blue    1/2
Brown   1/2
Red     0/3
Green   3/3
Purple  2/2
White   2/2
Yellow  0/0
Credits 1
```

## Playtest Defaults

Use these defaults:

```text
Starting main tracks: 2/2
Starting White:       2/2
Starting Yellow:      0/0
Track max:            6
Free recharge:        0
Yellow mode:          Alien
```

The current Python prototype uses the spreadsheet in this directory:

- `Roll_for_the_Galaxy_all_tiles.xls`
- first sheet: 110 non-start tiles
- second sheet: 9 faction pairs and 9 home worlds

Current simulation result with real start tiles and all tracks at `2/2`:

```text
Four players: average length about 13 rounds
Two players: average length about 19 rounds
Estimated table time: 45-60 minutes for experienced players
```

In a 200-game four-player sweep with Balanced, Builder, Settler, and Shipper
strategies, Alien-mode Yellow averaged 13.1 rounds. Wins were close among
Balanced, Builder, and Settler; Shipper lagged in the current heuristic
simulator. Yellow-as-Ship averaged 13.2 rounds with nearly identical strategy
results, so Alien-mode remains the recommended default for theme and tile
identity.

Solo challenge mode uses 12 rounds and two Dummy phase cards each round. In
simulation sweeps, the Dummy claimed about 19 tiles and drained about 12 VP
chips on average. Score Challenge tiers are tuned around 90%, 60%, 50%, and
30% success for Success, Great, Triumphant, and Epic with the balanced
heuristic. Treat those as simulation guideposts, not final balance data.

Run:

```bash
python3 -m roll_galaxy.simulate --games 100 --players P1:balanced P2:builder P3:settler P4:shipper
```

Compare yellow modes:

```bash
python3 -m roll_galaxy.simulate --games 100 --yellow-mode alien --players P1:balanced P2:builder P3:settler P4:shipper
python3 -m roll_galaxy.simulate --games 100 --yellow-mode ship --players P1:balanced P2:builder P3:settler P4:shipper
```
