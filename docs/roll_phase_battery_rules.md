# Roll for the Galaxy: Phase Battery Variant

## Current Active Direction

The active direction has been backed up to **minimal no-roll Roll**:

- keep secret phase selection;
- in solo and 2p games, each player selects two eligible phases; at 3p+, each
  player selects one eligible phase;
- a phase is eligible only if the player has at least one ready pip for that
  phase;
- resolve only selected phases, in normal Roll order;
- restore the VP chip pool and VP-chip scoring;
- restore Ship as Trade-or-Consume;
- remove White tracks/dice entirely; Credits are unlimited chips like base
  Roll;
- do not use the larger all-phases/no-VP-pool/Development-reward branch.

The goal is to remove dice-roll swing while staying close to base Roll for the
Galaxy. Some older sections below still describe the larger Phase Battery
expansion branch and should be treated as parked until rewritten.

This variant replaces face-roll luck with deterministic phase capacity. Players
still build a tableau of Worlds and Developments, pay Galactic Credits, Produce
Goods, Ship Goods to Trade for Credits or Consume for VP chips, and score from
tableau VP, VP chips, and 6-cost Development bonuses. The big change is that
dice colors become phase tracks instead of rolled workers, and secret phase
selection is constrained by available pips.

Core rule:

> When a tile says to gain a die, pip up that color track.

There is no Roll Dice step, no Assign Dice step, no Dice Cup, and no Citizenry.

## Current Design Decision

The recommended minimal ruleset is:

- dice colors become deterministic phase batteries;
- each track has current pips and max pips;
- gaining a die increases that color's max and current pips by 1;
- Red max is persistent Military level, while current Red is Military
  readiness;
- White dice/tracks are not used; Credits are chips;
- Military Worlds require enough Red max and exhaust 1 current Red;
- normal Worlds use Credits;
- Credits can supplement Develop builds or recharge spent colored pips during
  Manage Empire;
- Credits are not wild workers for Explore, Produce, or Ship;
- Yellow is Alien-specific by default.

The goal is not to make a new Roll for the Galaxy game. It is to keep tile
building, goods, shipping, credits, and tableau scoring intact while removing
the roll-and-reassign luck layer.

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
Alien     Yellow  0 1 2 3 4 5 6
```

Blue, Brown, Red, Green, Purple, and Yellow have two values:

- Current pips: how many pips are available to spend now.
- Max pips: the highest that color can recharge to.

Red max is Military level. Red current is Military readiness. Settling a
Military World checks Red max against the World's cost, then exhausts 1 current
Red. Red current can be recharged during Manage Empire like other colored
tracks.

White tracks/dice are not used. Credits are unlimited chips, tracked as a
separate chip count instead of on a track.

Recommended physical tracking:

- For phase batteries, put the colored die on the track to show current pips.
- Put a cube or marker on the track to show max pips.
- For Red, the max marker shows Military level and the die shows current
  readiness.
- Keep Credit chips beside the board.

Example:

```text
Red track: 0 1 2 3 4 5 6
              D   M
```

The red max marker is on 4, so Red Military level is 4. The red die is on 3, so
you have 3 current Red readiness pips.

## Color Map

Use these phase mappings:

```text
Blue    Explore
Brown   Develop
Red     Military level/readiness
Green   Produce
Purple  Ship
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
Blue    3/3
Brown   3/3
Red     3/3 Military readiness/level
Green   3/3
Purple  3/3
Credits 1 unlimited chip
Yellow  0/0
```

Older examples below may still use 2/2 as small numbers for illustration.

Then set up starting tiles normally:

1. Give each player one Faction tile.
2. Give each player one Home World tile.
3. Apply any starting die gains from those tiles as pips.
4. Draw starting Game Tiles into the Construction Zone as usual: one
   Development and one World.

Example:

```text
Starting Red is 2 Military.
Your Home World grants one Military die.
Military maps to Red.
Red 2/2 becomes 3/3.
```

If a starting tile places a die as a Good on that World, place a Good marker on
that World and pip up the granted color normally.

## Round Structure

Each round has four steps:

1. Select Phases
2. Reveal Phases
3. Resolve Selected Phases
4. Manage Empire

There is no Roll Dice step and no Assign Dice step.

During Select Phases, each player secretly selects eligible phases:

- Solo and 2-player games: each player selects 2 eligible phases.
- Games with 3 or more players: each player selects 1 eligible phase.

A phase is eligible only if you have at least 1 ready pip for that phase. For
example, Explore requires at least 1 current Blue pip, Develop requires at least
1 usable Develop pip and a Development in your Construction Zone, and Ship
requires at least 1 current Purple pip and at least 1 Good.

Reveal selected phases simultaneously. Resolve only phases selected by at least
one player, in normal Roll order:

```text
Explore -> Develop -> Settle -> Produce -> Ship
```

Unselected phases do not occur. During each selected phase, players act in turn
order, starting with the start player and proceeding clockwise. A player may use
a selected phase even if they did not select it, as long as they have usable
current pips or resources for that phase.

After all selected phases resolve, each player resolves Manage Empire in turn
order.

## Phase Use

Spend one current pip for one worker use.

```text
Spend 1 Blue pip   = one Explore worker
Spend 1 Brown pip  = one Develop worker
Spend 1 Green pip  = one Produce worker
Spend 1 Purple pip = one Ship worker
```

Credits are not workers. Credits are chip resources spent for Develop, normal
Settle, and recharge. Red is not normal build currency:
Military Worlds check Red max as level, then spend 1 current Red as readiness.

For Produce and Ship, spend native pips one at a time. Stop when you run out of
pips or cannot use more of that phase. For Explore, Scout may spend multiple
pips as search depth while still keeping only one tile; Stock spends pips one
at a time.

For Develop, Brown pips are build currency and can be saved as progress on any
Development in your Construction Zone. Credits can cover the remaining cost
when a Development completes. For Settle, Military Worlds check Red max and
exhaust current Red; normal Worlds spend Credits. You may Settle any World in
your Construction Zone that you can legally pay for.

## Example Round

Your tracks:

```text
Blue    1/2
Brown   0/2
Red     3/3
Green   2/2
Purple  1/2
Credits 1
Yellow  0/0
```

You select Settle. Other players select Develop and Ship.

Only selected phases resolve, in normal order:

```text
Develop, Settle, Ship
```

You may:

- Develop by spending Brown or eligible Yellow into Developments. If
  total progress reaches its cost, spend any needed Credits and complete it.
- Settle a Military World only if your Red max is at least its cost and you can
  exhaust 1 current Red.
- Settle a normal World only if you can pay its cost with Credits or eligible
  Yellow.
- Ship with Purple.

Explore and Produce do not occur this round because no one selected them.

After spending:

```text
Brown   0/2
Purple  0/2
Credits 0
```

If a Development costs 2 and you have Brown `1/2` and 1 Credit, you may
spend 1 Brown and 1 Credit to complete it. If you have Brown `0/2` and 2
Credits, you may spend 2 Credits to complete it.

## Explore

When Explore occurs, spend Blue pips.

Explore can Scout or Stock.

Scout is a single-tile action. Spend one or more Explore pips, then look through
that many candidate tiles of the needed type. Keep one tile and put it on the
matching construction area. Return the other candidates to the tile supply.

For the prototype, each construction area can hold up to three Developments or
three Worlds. Scout into the construction area with fewer cards. If both are
tied, choose whether you are Scouting for a Development or a World.

If both construction areas are full, each Explore pip may instead Stock for 2
Galactic Credits.

Explore is the tempo-cost escape hatch. It does not complete tableau cards by
itself, but it prevents a player from being hard-stopped by an empty
Construction Zone or no Credits.

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
Your Development area has one tile.
Your World area is empty.
You spend 2 Blue to Scout for a World.
Look through 2 World candidates.
Keep 1 World and put it in your World construction area.
Blue becomes 0/2.
```

## Develop

When Develop occurs, spend Brown pips into Developments in your Construction
Zone.

Developments can hold progress. Brown pips, and eligible Yellow pips for Alien
Developments, may be spent even if the Development cannot be completed this
round. Mark that progress on the Development. You may split Develop pips among
multiple Developments, and you may complete multiple Developments in the same
Develop phase.

Payment may be any mix of:

- Brown pips;
- Yellow pips, if the Development is Alien-tagged;
- Galactic Credits.

Spend pips first. If the Development's stored progress plus spent pips reaches
or can reach the full cost with available Credits, you may spend Credits to
cover the remainder and complete it. Credits are not placed as unfinished
progress; spend Credits only when they finish the Development.

If a Development's progress reaches the full cost, complete that Development:

1. Move it to your tableau.
2. Apply any immediate converted effects.

Use normal Development costs. Six-cost Developments cost 6.

Example:

```text
Brown is 1/2.
Credits are 2.
One Development costs 3.
Spend 1 Brown and 2 Credits.
Complete the Development.
Brown becomes 0/2 and Credits become 0.
```

Example:

```text
Brown is 2/2.
Credits are 0.
One Development costs 4.
Spend 2 Brown.
Mark 2 progress on the Development.
Brown becomes 0/2.
```

Later:

```text
Brown is 1/2.
Credits are 1.
The Development has 2 progress and needs 2 more.
Spend 1 Brown and 1 Credit.
Complete the Development.
```

## Settle

When Settle occurs, use Red level and readiness for Military Worlds or spend
Credits for normal Worlds.

You may complete any World in your Construction Zone if you can pay its full
cost immediately, or if it is Military and you can meet its Military cost and
exhaust 1 current Red. You may complete multiple Worlds in the same Settle
phase.

For normal Worlds, each World's payment may be any mix of:

- Yellow pips, if the World is Alien Technology;
- Galactic Credits.

For each Military World, your Red max must be at least the World's cost. Then
exhaust 1 current Red. Red max does not spend down.

If you pay the full cost, complete the World:

1. Move it to your tableau.
2. Gain any dice listed on the World by pipping up those colors.
3. Gain any listed Galactic Credits.
4. Place a starting Good if the tile's die placement says the die begins on the
   World.

Example:

```text
Credits are 2.
One normal World costs 2 and grants one Novelty die.
Spend 2 Credits to complete it.
Novelty maps to Blue.
Blue 2/2 becomes 3/3.
Credits become 0.
```

Example:

```text
Red is 3/3.
One Military World costs 3 and grants one Military die.
Settle it by exhausting 1 current Red.
Red 3/3 becomes 2/3.
The World grants one Military die.
Red becomes 3/4.
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

Each pip Ships one Good. For each shipped Good, choose Trade or Consume.

Trade removes the Good and gains Galactic Credits by World/good type:

- Regular Good: 1 Credit.
- Novelty Good: 2 Credits.
- Rare Elements or Genes Good: 3 Credits.
- Alien Technology Good: 4 Credits.
- Credits are unlimited chips.

Consume removes the Good and claims VP chips from the pool. The current
prototype uses the base Consume value plus converted matching bonuses:

- 1 VP chip for consuming a Good.
- +1 VP chip if the Good color matches the World color, or the Good is wild.
- +1 VP chip if the Ship pip color matches the World color, or the Ship pip is
  Purple.

Purple is the normal Ship color.

Example:

```text
Purple is 2/2.
You have two Goods.
Spend 1 Purple to Trade one Novelty Good for 2 Credits.
Spend 1 Purple to Consume the other Good for VP chips.
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

In this variant, Military maps to Red max and Red readiness.

- gaining a Military die increases Red max and current Red by 1;
- losing a Military die reduces Red max by 1 and caps current Red to the new
  max;
- Red max is checked to settle Military Worlds;
- settling a Military World exhausts 1 current Red;
- end-game bonuses that count Military dice count Red max.

For the prototype, a World is Military if it grants a Red die or has Rebel
identity. Normal Worlds, including non-military gray Worlds, use Credit chips instead.

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
Red is 4/4.
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

- Develop, if the Development is Alien-tagged.
- Settle, if the World is Alien Technology.
- Produce, if producing on an Alien Technology World.
- Ship, if Shipping a Good from an Alien Technology World.

Yellow cannot pay for unrelated non-Alien work.

Example:

```text
Yellow is 1/1.
One World is Deserted Alien Colony.
During Settle.
You may spend 1 Yellow as a Settler for that World.
Yellow becomes 0/1.
```

Example:

```text
Yellow is 1/1.
One World is Gem World.
During Settle.
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
construction areas are full, or Trade through Ship. Immediate tile effects can
also grant Credits.

During Develop or normal Settle, Credits may be spent as build currency. Each
Credit pays 1 cost. Developments may keep pip progress, but Credits are spent
only to finish the Development. Worlds must still be paid in one shot; Credits
cannot be left on a World as progress.

Credits are unlimited chips. They are not assigned to phases. Each round,
choose how to distribute available Credits among Develop payments, normal
Settle payments, and Manage Empire recharge.

During Manage Empire:

1. Spend Galactic Credits to recharge colored tracks.
2. Each Credit recharges 1 current pip on one track.
3. A track cannot recharge above its max.
4. You may distribute Credits among tracks however you choose.
5. If your Credit count is at 0 after Manage Empire, set it to 1 as in the
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

- Game Tiles in the Development area are built by Develop pips and may keep pip
  progress.
- Game Tiles in the World area are settled by Red Military level/readiness or
  Credits.
- Developments complete when stored progress plus current payment reaches cost.
- Worlds must be completed in one payment.
- Partial Settle progress is not tracked.
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

- any player has 12 or more tile squares in their tableau.
- the VP chip pool is empty.

Finish the round, then score normally:

- World and Development VP;
- VP chips;
- 6-cost Development bonuses, converted as closely as possible.

For a 6-cost Development bonus that refers to dice you own, use the battery
track that matches what the bonus is counting.

Use this conversion:

- If a bonus counts dice of a specific color, count that color's max pips.
- If a bonus counts total dice owned, count total max pips across colored die
  tracks.
- If a bonus counts different colors of dice, count color presence instead:
  each color track with max above 0 counts once.
- Credits are not owned dice, unless the bonus explicitly counts Credits.
- Yellow counts as present only if you have gained at least one Alien Technology
  pip.

For the prototype, score the 6-cost Developments this way:

```text
Free Trade Association   +1 VP per Novelty World.
Galactic Bankers         +Purple max plus remaining Credits.
Galactic Exchange        +different World colors plus color tracks present.
Galactic Federation      +1 VP per Development.
Galactic Renaissance     +completed tiles / 2, rounded down, plus World colors.
Galactic Reserves        +current colored pips / 3, rounded down.
Mining League            +Rare Worlds plus Brown max.
New Economy              +production Worlds.
New Galactic Order       +Red max.
System Diversification   +2 VP per different World color.
```

Examples:

```text
New Galactic Order counts Military dice.
Red max 4 = you own 4 Military dice for this bonus.

Galactic Exchange counts different colors of dice.
Blue, Brown, Red, Green, and Purple present = 5 colors.
Yellow max 0 = Yellow is not present.
Yellow max 2 = Yellow is present, for 6 colors total.
```

## Game Length Tuning

The tableau end condition remains the normal Roll for the Galaxy condition: 12
or more tile squares in one player's tableau. Do not raise this for the first
playtest.

The current active version uses a VP chip pool. Produce creates Goods, and Ship
can Trade for Credits or Consume for VP chips. Game length is governed by the
12-square tableau end condition, VP pool pressure, the recharge economy, and any
solo round limit.

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
2. Set Dummy Goods to 0.
3. Shuffle the five Dummy phase cards into a face-down deck.
4. Choose one campaign sheet.
5. Use a 24 VP-chip pool: 12 for you and 12 for the Dummy seat.
6. Play exactly 15 rounds, unless your tableau reaches 12 or more tile squares
   first.

Each campaign sheet has four win conditions. Play four games in a row. At the
end of each game, mark exactly one satisfied condition on that campaign sheet
that you have not already marked. If you cannot mark a new condition, you lose
the campaign. If you mark all four conditions after four successive games, you
win the campaign.

Choose a solo difficulty before the first game. These first-pass thresholds are
calibrated for the 15-round solo cap, two player phase selections, two Dummy
phase cards, starting colored tracks at 3/3, and a 24-chip solo VP pool:

```text
Difficulty  Great  Triumphant  Epic  Named  Industrial
Easy        24+    30+         36+   26+    17+ max pips
Normal      30+    36+         42+   32+    19+ max pips
Advanced    36+    42+         48+   38+    21+ max pips
Very Hard   42+    48+         54+   44+    23+ max pips
```

Named win conditions:

```text
Great       Score the difficulty's Great VP.
Triumphant  Score the difficulty's Triumphant VP.
Epic        Score the difficulty's Epic VP.
Builder     Score the difficulty's Named VP and complete 8+ tiles.
Developer   Score the difficulty's Named VP and have 4+ Developments.
Colonizer   Score the difficulty's Named VP and have 5+ Worlds.
Satisfied Populace
            Score the difficulty's Named VP and have 4+ shipped Goods this game.
Industrial  Score the difficulty's Named VP and have the difficulty's
            Industrial max pips.
Production  Score the difficulty's Named VP and have 4+ production Worlds.
Diverse     Score the difficulty's Named VP and have 4+ different World colors.
Novelty     Score the difficulty's Named VP and have 2+ Novelty Worlds.
Rare Elements
            Score the difficulty's Named VP and have 2+ Rare Worlds.
Alien Contact
            Score the difficulty's Named VP and have 1+ Alien World.
Military    Score the difficulty's Named VP and have Red max 5.
Discovery   Score the difficulty's Named VP and have Blue max 5.
```

Campaign sheets:

```text
Outreach
Great, Colonizer, Builder, Discovery.

Industrial Base
Triumphant, Developer, Industrial, Production.

Sector Survey
Great, Diverse, Novelty, Rare Elements.

Alien Contact
Triumphant, Alien Contact, Diverse, Discovery.

Mastery
Epic, Military, Industrial, Satisfied Populace.
```

For one-off practice, ignore the campaign sheet and simply note every condition
you satisfied.

Solo round structure:

1. Select two player phases. You may select a phase only if you have at least 1
   ready pip for that phase.
2. Reveal two Dummy phase cards. If the deck is empty, shuffle all five Dummy
   phase cards to form a new deck first.
3. The selected phase set is your phases plus the Dummy phases.
4. Resolve selected phases in normal order: Explore, Develop, Settle, Produce,
   Ship.
5. During each selected phase, you may spend usable pips or resources for that
   phase. If the Dummy selected that phase, also resolve that Dummy effect.
6. Manage Empire normally.

The Dummy never spends pips, never has Credits, never builds an empire, never
scores, and never uses tile powers. It exists to add phase uncertainty, create
piggyback opportunities, and churn the tile bag.

Dummy card effects:

```text
Explore:  Claim 1 Development tile and 1 World tile from the bag.
Develop:  Claim 1 Development tile from the bag.
Settle:   Claim 1 World tile from the bag.
Produce:  Dummy Goods +1, max 4.
Ship:     Set Dummy Goods to 0.
```

When the Dummy claims a tile, draw the first matching tile from the bag and
place it face down in the Dummy row. Do not read or resolve the tile. If no
matching tile remains in the bag, skip that claim.

The Dummy's claimed tiles do not trigger the 12-tile tableau end condition. They
exist only to keep the bag moving at a multiplayer-like pace.

Solo end conditions:

- the 15-round limit is reached;
- your tableau reaches 12 or more tile squares.

Finish the round, then check your campaign sheet. Mark one satisfied unmarked
condition. If you cannot mark one, the campaign is lost.

Solo example:

```text
Campaign: Outreach.
Unmarked conditions: Great, Colonizer, Builder, Discovery.
On Normal difficulty, you finish with 35 VP, 8 completed tiles, and Blue max 5.
You may mark Great, Builder, or Discovery, but not Colonizer unless you also
have 5+ Worlds. Mark exactly one condition.

You select Develop. Then reveal two Dummy cards: Produce and Develop.

Selected phases are Develop and Produce.

During Develop, you may spend Brown pips and Credits. Because the Dummy also
selected Develop, draw one Development tile from the bag and place it face down
in the Dummy row.

During Produce, you may spend Green pips. Because the Dummy selected Produce,
Dummy Goods 0 -> 1.
```

Later:

```text
Dummy reveals Explore and Ship.

Explore: draw one Development and one World from the bag into the Dummy row.
Ship: Dummy has 1 Good, so set Dummy Goods to 0.
```

## Full Round Example

Initial tracks:

```text
Blue    2/2
Brown   2/2
Red     2/2
Green   2/2
Purple  2/2
Credits 1
Yellow  0/0
```

Your Home World grants one Military die:

```text
Red 2/2 -> 3/3
```

Round 1 phase order:

```text
Explore, Develop, Settle, Produce, Ship
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
One World is a cost-3 Military World.
Red is 3/3.
Settle it by exhausting 1 current Red.
Red 3/3 -> 2/3.
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
Red     2/3
Green   3/3
Purple  2/2
Credits 1
Yellow  0/0
```

## Playtest Defaults

Use these defaults:

```text
Starting main tracks: 3/3
Starting Credits:     1 unlimited chip
Starting Yellow:      0/0
Track max:            6
Credits:              unlimited chips
VP pool:              7 per player
Solo VP pool:         24 total chips
Scoring:              tableau VP + VP chips + 6-cost bonuses
Free recharge:        0
Yellow mode:          Alien
```

Current playtest note:

Red readiness is a soft Military brake, not a hard cooldown. In a focused
stress pass, a Military player with enough Red max could still settle a Military
World every round by preserving or generating enough Credit to recharge current
Red during Manage Empire. That is acceptable for the first table test because
it makes Military compete with other recharge and build spending instead of
making Military Worlds free forever.

Watch these table metrics:

- Military Worlds completed per player.
- Rounds where Military settled while spending 0 Credits.
- Credits spent on Red recharge.
- Red max at game end.
- Whether normal Worlds' Produce/Ship payoff keeps up with Military tempo.

If Military still runs away, the next clean tuning knob is to make Military
Worlds that grant Red increase Red max only; their current Red gain would wait
until a later recharge.
