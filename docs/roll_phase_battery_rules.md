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
- Credits can complete Develop/Settle builds or recharge spent pips during
  Manage Empire;
- White remains wild;
- Yellow is Alien-specific by default.

The goal is not to make a new Roll for the Galaxy game. It is to keep phase
selection, tile building, goods, shipping, credits, VP chips, and tableau
scoring intact while removing the roll-and-reassign luck layer.

For the first playtest, do not add free recharge, tile-specific retuning, or a
new dummy-player system. Those are tuning knobs after the core battery loop is
tested at the table.

There is also a parked mancala dice alternative in
`docs/roll_mancala_dice_design.md`. It uses the base game's physical dice as
mancala stones. That design is not part of this ruleset.

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
4. Use 16 VP chips per player for the shared VP pool.
5. Set starting tracks:

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

For Explore, Produce, and Ship, spend pips one at a time. Stop when you run out
of pips or cannot use more of that phase.

For Develop and Settle, pips are build currency. You must pay the full tile cost
at once with phase pips, Galactic Credits, or a mix of both. If you cannot pay
the full cost, you spend nothing and keep the tile in your Construction Zone.

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

- Develop only if you can pay the full Development cost with Brown, White,
  Yellow if eligible, Credits, or a mix of those.
- Settle only if you can pay the full World cost with Red, White, Yellow if
  eligible, Credits, or a mix of those.
- Ship with Purple, or White if Purple runs out.

After spending:

```text
Brown   0/2
Red     2/3
Purple  0/2
White   1/2
```

If your top Development costs 2 and you have Brown `0/2`, White `2/2`, and 0
Credits, you may spend 2 White to complete it. If you have only White `1/2` and
0 Credits, you spend nothing on that Development this round.

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

You may complete the top tile of your Development stack if you can pay its full
cost immediately.

Payment may be any mix of:

- Brown pips;
- White pips;
- Yellow pips, if the Development is Alien-tagged;
- Galactic Credits.

If you pay the full cost, complete the Development:

1. Move it to your tableau.
2. Apply any immediate converted effects.

Use normal Development costs. Six-cost Developments cost 6.

Example:

```text
Brown is 1/2.
Credits are 2.
Your top Development costs 3.
Spend 1 Brown and 2 Credits.
Complete the Development.
Brown becomes 0/2 and Credits become 0.
```

If Brown is 1/2, White is 0/2, Credits are 0, and the top Development costs 2,
you cannot partially build it. Spend nothing.

## Settle

When Settle occurs, spend Red or White pips.

You may complete the top tile of your World stack if you can pay its full cost
immediately.

Payment may be any mix of:

- Red pips;
- White pips;
- Yellow pips, if the World is Alien Technology;
- Galactic Credits.

If you pay the full cost, complete the World:

1. Move it to your tableau.
2. Gain any dice listed on the World by pipping up those colors.
3. Gain any listed Galactic Credits.
4. Place a starting Good if the tile's die placement says the die begins on the
   World.

Example:

```text
Red is 1/2.
White is 1/2.
Credits are 1.
Your top World costs 3 and grants one Novelty die.
Spend 1 Red, 1 White, and 1 Credit to complete it.
Novelty maps to Blue.
Blue 2/2 becomes 3/3.
Red becomes 0/2, White becomes 0/2, and Credits become 0.
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

## Military / Red Dice

In base Roll for the Galaxy, Military is a die color, not a separate conquest
discount as in Race for the Galaxy or New Frontiers. Military dice can roll or
be assigned as workers, and red dice are especially associated with Settle.

For this variant, Military maps to Red capacity:

- gaining a Military die pips up Red;
- losing a Military die pips Red down;
- Red pips help pay to Settle Worlds;
- end-game bonuses that count Military dice count Red max pips.

There is no separate military conquest rule by default. Worlds still use their
printed Settle costs unless a specific tile power reduces that cost.

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

During Develop or Settle, Credits may be spent as build currency. Each Credit
pays 1 cost toward the top Development or World. The full cost must be paid at
once; Credits cannot be left on a tile as progress.

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
- Developments and Worlds must be completed in one payment.
- Partial Develop/Settle progress is not tracked.
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
Reduce the combined pips/Credits required by that amount.

Gain Credits:
Gain Galactic Credits normally.
```

## End Of Game And Scoring

Use normal Roll for the Galaxy end conditions:

- the Phase Battery VP chip pool is exhausted; or
- any player has 12 or more tile squares in their tableau.

Finish the round, then score normally:

- VP chips;
- World and Development VP;
- 6-cost Development bonuses, converted as closely as possible.

For a 6-cost Development bonus that refers to dice you own, use the battery
track that matches what the bonus is counting.

Use this conversion:

- If a bonus counts dice of a specific color, count that color's max pips.
- If a bonus counts total dice owned, count total max pips across all tracks.
- If a bonus counts different colors of dice, count color presence instead:
  each color track with max above 0 counts once.
- Yellow counts as present only if you have gained at least one Alien Technology
  pip.

Examples:

```text
New Galactic Order counts Military dice.
Red max 4 = you own 4 Military dice for this bonus.

Galactic Exchange counts different colors of dice.
Blue, Brown, Red, Green, Purple, and White present = 6 colors.
Yellow max 0 = Yellow is not present.
Yellow max 2 = Yellow is present, for 7 colors total.
```

## Game Length Tuning

The tableau end condition remains the normal Roll for the Galaxy condition: 12
or more tile squares in one player's tableau. Do not raise this for the first
playtest.

The VP pool is the easier tuning knob. The base game uses 12 VP chips per
player. This variant currently uses 16 VP chips per player because the simulator
often ended by VP pool exhaustion before players approached 12 tableau squares.

What this changes:

- If games end by VP pool exhaustion, a larger VP pool makes them longer.
- If games end by a player reaching 12 tableau squares, a larger VP pool does
  little or nothing.

Recent simulation examples:

```text
Mixed 4-player strategies, 12 VP/player:
Average 12.8 rounds; 231/300 games ended by VP pool, 69/300 by tableau.

Mixed 4-player strategies, 16 VP/player:
Average 15.1 rounds; 204/300 games ended by VP pool, 96/300 by tableau.

All-builder 4-player strategies, 12 VP/player:
Average 13.6 rounds; 16/300 games ended by VP pool, 284/300 by tableau.

All-builder 4-player strategies, 16 VP/player:
Average 13.7 rounds; 12/300 games ended by VP pool, 288/300 by tableau.
```

So 16 VP/player is a playtest default, not a claim that every game will last
longer. Fast-building tables will still be governed by the 12-square tableau
end condition.

## Solo Mode: Win Conditions

Solo mode uses the normal Phase Battery rules with a fixed clock, dummy phase
cards, and win conditions. This follows the solo style of New Frontiers:
Starry Rift and Jump Drive: Terminal Velocity: you are not racing an automa
score. You are trying to build the right empire before time runs out.

Additional components:

- five Dummy phase cards: Explore, Develop, Settle, Produce, Ship;
- one Dummy claimed-tile row;
- one Dummy Goods marker;
- five solo campaign sheets.

Setup:

1. Set up one normal player area.
2. Use a 30 VP chip pool.
3. Set Dummy Goods to 0.
4. Shuffle the five Dummy phase cards into a face-down deck.
5. Choose one campaign sheet.

Each campaign sheet has a menu of scenario conditions. Play four games in a
row. At the end of each game, mark exactly one satisfied scenario on that
campaign sheet that you have not already marked. If you cannot mark a new
scenario, you lose the campaign. If you mark four different scenarios after
four successive games, you win the campaign.

Score-only win conditions:

```text
Great        Score 40+ VP.
Triumphant   Score 43+ VP.
Epic         Score 46+ VP.
```

Recommended named win conditions:

```text
Great       Score 40+ VP.
Triumphant  Score 43+ VP.
Epic        Score 46+ VP.
Builder     Score 31+ VP and complete 7+ tiles.
Developer   Score 31+ VP and have 4+ Developments.
Colonizer   Score 31+ VP and have 6+ Worlds.
Satisfied Populace
            Score 31+ VP and score 10+ VP chips.
Industrial  Score 31+ VP and have 16+ total max pips.
Production  Score 31+ VP and have 4+ production Worlds.
Diverse     Score 31+ VP and have 3+ different World colors.
Novelty     Score 31+ VP and have 2+ Novelty Worlds.
Rare Elements
            Score 31+ VP and have 2+ Rare Worlds.
Alien Contact
            Score 31+ VP and have 1+ Alien World.
Military    Score 31+ VP and have Red max 5.
Discovery   Score 31+ VP and have Blue max 5.
```

Campaign sheets:

```text
Outreach
Colonial Power, Production Web, Great Alien Contact, Great Production,
Great Colonizer, Great Builder, Great Industrial, Great Diversity.

Industrial Base
Grand Architect, Architect, Industrialist, Research League, Great Populace,
Great Developer, Great Industrial, Great Production.

Sector Survey
Discoverer, Pathfinder, Renaissance, Great Novelty, Great Rare Elements,
Great Alien Contact, Great Diversity, Great Colonizer.

Alien Contact
Warlord, Alien Empire, Great Military, Great Discovery, Fleet Command,
Great Alien Contact, Great Diversity, Commerce Ring.

Mastery
Grand Architect, Imperial Reach, Galactic Unifier, Golden Age, Empire Builder,
Industrialist, Commerce Ring, Great Builder, Great Industrial.
```

Scenario condition key:

```text
Great Builder        Score 40+ VP and complete 7+ tiles.
Great Developer      Score 40+ VP and have 4+ Developments.
Great Colonizer      Score 40+ VP and have 6+ Worlds.
Great Populace       Score 40+ VP and score 10+ VP chips.
Great Industrial     Score 40+ VP and have 16+ total max pips.
Great Production     Score 40+ VP and have 4+ production Worlds.
Great Diversity      Score 40+ VP and have 3+ different World colors.
Great Novelty        Score 40+ VP and have 2+ Novelty Worlds.
Great Rare Elements  Score 40+ VP and have 2+ Rare Worlds.
Great Alien Contact  Score 40+ VP and have 1+ Alien World.
Great Military       Score 40+ VP and have Red max 5.
Great Discovery      Score 40+ VP and have Blue max 5.
Architect            Score 40+ VP and have 6+ Developments.
Colonial Power       Score 40+ VP and have 7+ Worlds.
Production Web       Score 40+ VP and have 5+ production Worlds.
Pathfinder           Score 40+ VP and have Blue max 5.
Commerce Ring        Score 40+ VP and score 12+ VP chips.
Fleet Command        Score 40+ VP and have Red max 4.
Empire Builder       Score 43+ VP and complete 9+ tiles.
Industrialist        Score 43+ VP and have 18+ total max pips.
Renaissance          Score 43+ VP and have 7+ Worlds.
Warlord              Score 43+ VP and have Red max 5.
Discoverer           Score 43+ VP and have Blue max 5.
Research League      Score 43+ VP and have 5+ Developments.
Golden Age           Score 46+ VP and complete 8+ tiles.
Alien Empire         Score 46+ VP and have 1+ Alien World.
Grand Architect      Score 46+ VP and have 6+ Developments.
Imperial Reach       Score 46+ VP and have 7+ Worlds.
Galactic Unifier     Score 46+ VP and have 4+ different World colors.
```

For one-off practice, ignore the campaign sheet and simply note every broad
condition or scenario condition you satisfied. Campaign mode is intentionally
harder because each marked scenario requires at least a Great score.

Solo round structure:

1. Select your phase normally.
2. Reveal two Dummy phase cards. If the deck is empty, shuffle all five Dummy
   phase cards to form a new deck first.
3. The selected phases this round are your selected phase plus the Dummy phases.
4. Resolve selected phases in normal Roll order. You may spend pips and Credits
   in any selected phase.
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

Finish the round, then check your campaign sheet. Mark one satisfied unmarked
scenario. If you cannot mark one, the campaign is lost.

Solo example:

```text
Campaign: Outreach.
Unmarked scenarios include Colonial Power, Production Web, Great Alien Contact,
Great Production, Great Colonizer, Great Builder, Great Industrial, and Great
Diversity.
You finish with 41 VP, 7 completed tiles, 6 Worlds, and 4 production Worlds.
You may mark Great Builder, Great Colonizer, or Great Production. Mark exactly
one of them.

You select Settle.
Dummy reveals Produce and Develop.

Selected phases: Develop, Settle, Produce.

You may spend Brown pips and Credits during Develop.
You may spend Red pips and Credits during Settle.
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
Average Dummy churn: about 18 claimed tiles and 11 drained VP chips.
For one-off score-only win conditions with the balanced heuristic, Great is
about 58%, Triumphant about 37%, and Epic about 20%.
Scenario-menu campaign sheets are much harder. In 200-game balanced-heuristic
sweeps, the five campaign sheets each landed around 11-13% campaign wins.
```

Run:

```bash
python3 -m roll_galaxy.solo --games 100 --strategy balanced --campaign outreach
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
VP pool:              16 per player
Free recharge:        0
Yellow mode:          Alien
```

The current Python prototype uses the spreadsheet in this directory:

- `Roll_for_the_Galaxy_all_tiles.xls`
- first sheet: 110 non-start tiles
- second sheet: 9 faction pairs and 9 home worlds

Current simulation result with real start tiles and all tracks at `2/2`:

```text
Three players: average length about 16.0 rounds
Four players:  average length about 14.8 rounds
Five players:  average length about 14.6 rounds
Estimated table time: 45-60 minutes for experienced players
```

In a 1000-game four-player sweep with Balanced, Builder, Settler, and Shipper
strategies, Alien-mode Yellow with 16 VP/player averaged 14.8 rounds. Wins were
tightly grouped: Builder 270, Settler 258, Balanced 244, Shipper 228. In a
100-game comparison, Yellow-as-Ship averaged about the same length, so Alien-mode
remains the recommended default for theme and tile identity.

Solo challenge mode uses 12 rounds and two Dummy phase cards each round. In
simulation sweeps, the Dummy claimed about 18 tiles and drained about 11 VP
chips on average. After the one-shot Develop/Settle change, score-only win
conditions were retuned to 40, 43, and 46 VP. In a 1000-game balanced-heuristic
sweep, those landed around 58%, 37%, and 20% success for Great, Triumphant, and
Epic. Treat these as simulation guideposts, not final balance data.

Run:

```bash
python3 -m roll_galaxy.simulate --games 100 --players P1:balanced P2:builder P3:settler P4:shipper
```

Compare yellow modes:

```bash
python3 -m roll_galaxy.simulate --games 100 --yellow-mode alien --players P1:balanced P2:builder P3:settler P4:shipper
python3 -m roll_galaxy.simulate --games 100 --yellow-mode ship --players P1:balanced P2:builder P3:settler P4:shipper
```
