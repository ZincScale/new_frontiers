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
- Red is a persistent Military level, not a spendable phase battery;
- White is the Credit track;
- Military Worlds use Red level and do not spend Red down;
- normal Worlds use White/Credits;
- Credits can supplement Develop builds or recharge spent non-Red phase pips
  during Manage Empire;
- Credits are not wild workers for Explore, Produce, or Ship;
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
Military  Red     0 1 2 3 4 5 6
Produce   Green   0 1 2 3 4 5 6
Ship      Purple  0 1 2 3 4 5 6
Credits   White   0 1 2 3 4 5 6
Alien     Yellow  0 1 2 3 4 5 6
```

Blue, Brown, Green, Purple, and Yellow have two values:

- Current pips: how many pips are available to spend now.
- Max pips: the highest that color can recharge to.

Red has one effective value: Military level. Its current marker should stay on
its max. Settling Military Worlds checks Red level but does not spend Red down.

White is Credits. Move the White marker as Credits are gained and spent.

Recommended physical tracking:

- For phase batteries, put the colored die on the track to show current pips.
- Put a cube or marker on the track to show max pips.
- For Red, keep the die and max marker together.
- For White, only the Credit marker matters.

Example:

```text
Red track: 0 1 2 3 4 5 6
                  D/M
```

The red die and marker are on 4, so Red Military level is 4.

## Color Map

Use these phase mappings:

```text
Blue    Explore
Brown   Develop
Red     Military level
Green   Produce
Purple  Ship
White   Credits
Yellow  Alien
```

Yellow is not a normal phase. It starts at `0/0` and is used only for Alien
work, explained under Yellow / Alien Pips.

## Setup

Set up the base game normally, with these changes:

1. Do not give players Dice Cups.
2. Do not put dice in the Cup or Citizenry.
3. Give each player a Phase Battery board.
4. Use 8 VP chips per player in a 2-player game, or 12 VP chips per player in
   a game with 3 or more players.
5. Set starting tracks:

```text
Blue    2/2
Brown   2/2
Red     2 Military
Green   2/2
Purple  2/2
White   1 Credit
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
Starting Red is 2 Military.
Your Home World grants one Military die.
Military maps to Red.
Red becomes 3 Military.
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
Spend 1 Green pip  = one Produce worker
Spend 1 Purple pip = one Ship worker
```

Red and White are not workers. Red is checked as Military level. White is spent
as Credits.

For Produce and Ship, spend native pips one at a time. Stop when you run out of
pips or cannot use more of that phase. For Explore, Scout may spend multiple
pips as search depth while still keeping only one tile; Stock spends pips one
at a time.

For Develop, Brown pips are build currency and Credits can cover the remaining
cost. For Settle, Military Worlds check Red level and normal Worlds spend
Credits. If you cannot pay the full cost or meet the Military level, you spend
nothing and keep the tile in your Construction Zone.

## Example Round

Your tracks:

```text
Blue    1/2
Brown   0/2
Red     3/3
Green   2/2
Purple  1/2
White   1 Credit
Yellow  0/0
```

You select Settle. Other players select Develop and Ship.

Selected phases:

```text
Develop, Settle, Ship
```

You may:

- Develop only if you can pay the full Development cost with Brown, Credits,
  or eligible Yellow.
- Settle a Military World only if your Red level is at least its cost.
- Settle a normal World only if you can pay its cost with Credits or eligible
  Yellow.
- Ship with Purple.

After spending:

```text
Brown   0/2
Purple  0/2
White   0 Credits
```

If your top Development costs 2 and you have Brown `1/2` and 1 Credit, you may
spend 1 Brown and 1 Credit to complete it. If you have Brown `0/2` and 2
Credits, you may spend 2 Credits to complete it.

## Explore

When Explore occurs, spend Blue pips.

Explore can Scout or Stock.

Scout is a single-tile action. Spend one or more Explore pips, then look through
that many candidate tiles of the needed type. Keep one tile and put it on the
bottom of that build stack. Return the other candidates to the tile supply.

If both build stacks are empty, choose whether you are Scouting for a
Development or a World. If exactly one build stack is empty, Scout for that
type.

If both build stacks already have tiles, each Explore pip may instead Stock for
2 Galactic Credits.

Explore is the tempo-cost escape hatch. It does not complete tableau cards by
itself, but it prevents a player from being hard-stopped by an empty queue or no
Credits.

Because Scout lets you spend pips as search depth, Explore also supports
strategic tile hunting. The prototype recognizes these broad lanes:

```text
Builder    Development cards, especially 6-cost end-game Developments.
Settler    Worlds and die grants.
Producer   Production Worlds, Green, Purple, and trade/consume Developments.
Shipper    Purple, production support, and Phase V Developments.
Mining     Rare Element Worlds, Brown, and Mining League.
Novelty    Novelty Worlds, Blue, and Free Trade Association.
Genes      Genes Worlds and Green.
Alien      Alien Technology Worlds and Yellow.
Military   Red grants, Rebel/gray Worlds, and New Galactic Order.
Diverse    Missing World colors, System Diversification, and Galactic Exchange.
```

Example:

```text
Blue is 2/2.
Your Development stack has one tile.
Your World stack is empty.
You spend 2 Blue to Scout for a World.
Look through 2 World candidates.
Keep 1 World and put it on the bottom of your World stack.
Blue becomes 0/2.
```

## Develop

When Develop occurs, spend Brown pips and/or Credits.

You may complete the top tile of your Development stack if you can pay its full
cost immediately. Credits may cover any part of the cost.

Payment may be any mix of:

- Brown pips;
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

If Brown is 0/2, Credits are 2, and the top Development costs 2, you may spend
2 Credits to complete it.

## Settle

When Settle occurs, use Red level for Military Worlds or spend Credits for
normal Worlds.

You may complete the top tile of your World stack if you can pay its full cost
immediately or meet its Military cost.

For normal Worlds, payment may be any mix of:

- Yellow pips, if the World is Alien Technology;
- Galactic Credits.

For Military Worlds, your Red level must be at least the World's cost. Red does
not spend down.

If you pay the full cost, complete the World:

1. Move it to your tableau.
2. Gain any dice listed on the World by pipping up those colors.
3. Gain any listed Galactic Credits.
4. Place a starting Good if the tile's die placement says the die begins on the
   World.

Example:

```text
White is 2 Credits.
Your top normal World costs 2 and grants one Novelty die.
Spend 2 Credits to complete it.
Novelty maps to Blue.
Blue 2/2 becomes 3/3.
White becomes 0 Credits.
```

Example:

```text
Red Military level is 3.
Your top Military World costs 3 and grants one Military die.
Settle it without spending Red.
Red becomes 4 Military.
```

## Produce

When Produce occurs, spend Green pips.

Each pip produces one Good on an eligible non-gray World in your tableau.

Instead of placing a worker die as the Good, place a Good marker, cube, or spare
die on the World.

The Good's color is the color of the pip spent:

```text
Green pip = Green Good
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

When Ship occurs, spend Purple pips.

Each pip Ships one Good. For each Good, choose Trade or Consume as in the base
game.

For matching, use the Good marker's color:

- A Good always gives at least 1 VP when Consumed.
- +1 VP if the Good color matches the World color.

Purple is the normal Ship color.

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
Home              No track; represented by starting capacity
Novelty           Blue
Rare Elements     Brown
Genes             Green
Alien Technology  Yellow
Military          Red
Consumption       Purple
```

Examples:

```text
Red is 2 Military.
You gain one Military die.
Red becomes 3 Military.
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

In this variant, Military maps to persistent Red level.

- gaining a Military die increases Red level;
- losing a Military die reduces Red level;
- Red level is checked to settle Military Worlds;
- Red does not spend down when a Military World is settled;
- end-game bonuses that count Military dice count Red level.

For the prototype, a World is Military if it grants a Red die or has Rebel
identity. Normal Worlds, including non-military gray Worlds, use the White
Credit track instead.

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
Red is 4 Military.
You must lose one Military die.
Red becomes 3 Military.
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
Ship spending order: Purple -> Yellow
```

The simulator supports both versions. The current default is Alien mode.

## Galactic Credits And Recharge

Galactic Credits no longer recruit dice from Citizenry.

The main renewable Credit source is tempo: Stock through Explore after both
build stacks have tiles, or Trade through Ship. Immediate tile effects can also
grant Credits.

During Develop or normal Settle, Credits may be spent as build currency. Each
Credit pays 1 cost toward the top Development or World. The full cost must be
paid at once; Credits cannot be left on a tile as progress.

During Manage Empire:

1. Spend Galactic Credits to recharge non-Red, non-White phase tracks.
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
Green is 1/3.
Purple is 2/2.

Spend 2 Credits: Brown 0/2 -> 2/2.
Spend 1 Credit: Green 1/3 -> 2/3.
Purple is already full, so you cannot recharge it.
```

## Construction Zone And Tableau

Use the normal Construction Zone rules:

- Game Tiles in the Development stack are built by Develop pips.
- Game Tiles in the World stack are settled by Red Military level or Credits.
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
- If a bonus counts total dice owned, count total max pips across non-White
  die tracks.
- If a bonus counts different colors of dice, count color presence instead:
  each color track with max above 0 counts once.
- White is Credits, not owned dice, unless the bonus explicitly counts Credits.
- Yellow counts as present only if you have gained at least one Alien Technology
  pip.

For the prototype, score the 6-cost Developments this way:

```text
Free Trade Association   +1 VP per Novelty World.
Galactic Bankers         +Purple max plus remaining Credits.
Galactic Exchange        +different World colors plus color tracks present.
Galactic Federation      +1 VP per Development.
Galactic Renaissance     +completed tiles / 2, rounded down, plus World colors.
Galactic Reserves        +current non-White pips / 3, rounded down.
Mining League            +Rare Worlds plus Brown max.
New Economy              +production Worlds plus VP chips / 5, rounded down.
New Galactic Order       +Red level.
System Diversification   +2 VP per different World color.
```

Examples:

```text
New Galactic Order counts Military dice.
Red level 4 = you own 4 Military dice for this bonus.

Galactic Exchange counts different colors of dice.
Blue, Brown, Red, Green, and Purple present = 5 colors.
Yellow max 0 = Yellow is not present.
Yellow max 2 = Yellow is present, for 6 colors total.
```

## Game Length Tuning

The tableau end condition remains the normal Roll for the Galaxy condition: 12
or more tile squares in one player's tableau. Do not raise this for the first
playtest.

The VP pool is the easier tuning knob. The base game uses 12 VP chips per
player. This variant currently uses a lower 2-player pool because fewer players
select fewer phases and a 2-player game otherwise runs long.

What this changes:

- If games end by VP pool exhaustion, a larger VP pool makes them longer.
- If games end by a player reaching 12 tableau squares, a larger VP pool does
  little or nothing.

Recommended default:

```text
2 players:   8 VP/player
3+ players: 12 VP/player
```

Fast-building tables can still be governed by the 12-square tableau end
condition. Producer/shipper-heavy 2-player tables are the main case where the
lower VP pool matters.

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

Each campaign sheet has four win conditions. Play four games in a row. At the
end of each game, mark exactly one satisfied condition on that campaign sheet
that you have not already marked. If you cannot mark a new condition, you lose
the campaign. If you mark all four conditions after four successive games, you
win the campaign.

Choose a solo difficulty before the first game:

```text
Difficulty  Great  Triumphant  Epic  Named  Industrial
Easy        23+    30+         36+   24+    12+ max pips
Normal      31+    36+         42+   32+    14+ max pips
Advanced    36+    42+         48+   36+    15+ max pips
Very Hard   42+    48+         54+   40+    16+ max pips
```

Named win conditions:

```text
Great       Score the difficulty's Great VP.
Triumphant  Score the difficulty's Triumphant VP.
Epic        Score the difficulty's Epic VP.
Builder     Score the difficulty's Named VP and complete 8+ tiles.
Developer   Score the difficulty's Named VP and have 5+ Developments.
Colonizer   Score the difficulty's Named VP and have 6+ Worlds.
Satisfied Populace
            Score the difficulty's Named VP and score 11+ VP chips.
Industrial  Score the difficulty's Named VP and have the difficulty's
            Industrial max pips.
Production  Score the difficulty's Named VP and have 4+ production Worlds.
Diverse     Score the difficulty's Named VP and have 4+ different World colors.
Novelty     Score the difficulty's Named VP and have 2+ Novelty Worlds.
Rare Elements
            Score the difficulty's Named VP and have 2+ Rare Worlds.
Alien Contact
            Score the difficulty's Named VP and have 1+ Alien World.
Military    Score the difficulty's Named VP and have Red level 4.
Discovery   Score the difficulty's Named VP and have Blue max 4.
```

Campaign sheets:

```text
Outreach
Great, Colonizer, Builder, Industrial.

Industrial Base
Triumphant, Developer, Industrial, Production.

Sector Survey
Triumphant, Diverse, Novelty, Rare Elements.

Alien Contact
Triumphant, Alien Contact, Diverse, Discovery.

Mastery
Epic, Novelty, Rare Elements, Military.
```

For one-off practice, ignore the campaign sheet and simply note every condition
you satisfied.

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
condition. If you cannot mark one, the campaign is lost.

Solo example:

```text
Campaign: Outreach.
Unmarked conditions: Great, Colonizer, Builder, Industrial.
On Normal difficulty, you finish with 35 VP, 8 completed tiles, and 15 total
max pips. You may mark Builder or Industrial, but not Triumphant. Mark exactly
one condition.

You select Settle.
Dummy reveals Produce and Develop.

Selected phases: Develop, Settle, Produce.

You may spend Brown pips and Credits during Develop.
You may check Red level for Military Worlds or spend Credits for normal Worlds
during Settle.
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
about 45%, Triumphant about 25%, and Epic about 12%.
Four-condition campaign sheets are stricter than one-off practice because each
game must mark a different condition from that sheet.
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
Red     2 Military
Green   2/2
Purple  2/2
White   1 Credit
Yellow  0/0
```

Your Home World grants one Military die:

```text
Red 2 Military -> 3 Military
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
Spend 2 Blue to Scout for a World.
Look through 2 World candidates.
Keep 1 World.
Blue 2/2 -> 0/2.
```

Develop:

```text
Spend 2 Brown on a cost-2 Development.
Brown 2/2 -> 0/2.
Complete the Development.
```

Settle:

```text
Your top World is a cost-3 Military World.
Red Military level is 3.
Settle it without spending Red.
Complete the World.
The World grants one Genes die.
Green 2/2 -> 3/3.
```

Manage Empire:

```text
White 1 Credit.
Recharge Brown 0/2 -> 1/2.
Credits would become 0, so reset to 1.
```

End of round tracks:

```text
Blue    1/2
Brown   1/2
Red     3 Military
Green   3/3
Purple  2/2
White   1 Credit
Yellow  0/0
```

## Playtest Defaults

Use these defaults:

```text
Starting main tracks: 2/2
Starting White:       1 Credit
Starting Yellow:      0/0
Track max:            6
Credit max:           6
VP pool:              8/player at 2p, 12/player at 3p+
Free recharge:        0
Yellow mode:          Alien
```

The current Python prototype uses the spreadsheet in this directory:

- `Roll_for_the_Galaxy_all_tiles.xls`
- first sheet: 110 non-start tiles
- second sheet: 9 faction pairs and 9 home worlds

Current simulation result with real start tiles and all tracks at `2/2`:

```text
Two players:   average length about 18-20 rounds
Three players: average length about 19.7 rounds
Four players:  average length about 18.5 rounds
Five players:  average length about 17.0 rounds
Estimated table time: 50-70 minutes for experienced players
```

In a 1000-game two-player sweep with Balanced and Builder, the 8 VP/player pool
averaged 20.1 rounds. A producer/shipper two-player stress sweep averaged 17.9
rounds, with wins nearly even: Producer 527, Shipper 473.

In a 1000-game four-player sweep with Balanced, Builder, Settler, and Shipper
strategies, the 12 VP/player pool averaged 18.5 rounds. Wins were tightly
grouped: Builder 274, Settler 267, Balanced 230, Shipper 229.

A 1000-game five-archetype sweep with Mining, Producer, Military, Alien, and
Builder averaged 17.0 rounds. Wins were spread across the lanes: Military 221,
Alien 219, Producer 211, Mining 184, Builder 165. Average final scores were all
within about 2 VP, which suggests the tile-search and 6-cost scoring rules are
supporting multiple viable plans rather than one dominant build path.

Solo challenge mode uses 12 rounds and two Dummy phase cards each round. In
simulation sweeps, the Dummy claimed about 19 tiles and drained about 12 VP
chips on average. After the Red/White retune, solo difficulty tiers target about
90% success on Easy, 50-60% on Normal, and less than 50% on Advanced and Very
Hard. In a 1000-game balanced-heuristic sweep against the Great target, those
landed at 91.6%, 53.5%, 28.0%, and 10.1%. Treat these as simulation guideposts,
not final balance data.

Run:

```bash
python3 -m roll_galaxy.simulate --games 100 --players P1:balanced P2:builder P3:settler P4:shipper
```

Compare yellow modes:

```bash
python3 -m roll_galaxy.simulate --games 100 --yellow-mode alien --players P1:balanced P2:builder P3:settler P4:shipper
python3 -m roll_galaxy.simulate --games 100 --yellow-mode ship --players P1:balanced P2:builder P3:settler P4:shipper
```
