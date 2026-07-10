# Roll for the Galaxy: Phase Battery Variant

## Current Active Direction

The active direction has been backed up to **minimal no-roll Roll**:

- keep secret phase selection;
- in solo, the player selects two eligible phases; in multiplayer, each player
  selects one eligible phase;
- a phase is eligible only if the player has at least one ready pip for that
  phase;
- selecting a phase does not consume pips; pips are workers spent only when a
  selected phase resolves;
- resolve only selected phases, in normal Roll order;
- restore the VP chip pool and VP-chip scoring;
- restore Ship as Trade-or-Consume;
- use Red as the single Settle track for all Worlds; there is no White track
  and Roll has no Military World type; Credits are unlimited chips like base
  Roll;
- remove 6-cost Developments from the normal bag and use them as delayed
  end-game goal cards;
- do not use the larger all-phases/no-VP-pool/Development-reward branch.

The goal is to remove dice-roll swing while staying close to base Roll for the
Galaxy. Some older sections below still describe the larger Phase Battery
expansion branch and should be treated as parked until rewritten.

This variant replaces face-roll luck with deterministic phase capacity. Players
still build a tableau of Worlds and Developments, pay Galactic Credits, Produce
Goods, Ship Goods to Trade for Credits or Consume for VP chips, and score from
tableau VP, VP chips, and chosen 6-cost Development goals. The big change is
that dice colors become phase tracks instead of rolled workers. Secret phase
selection is constrained by available pips, but selecting a phase does not
spend those pips.

Core rule:

> When a tile grants a die, increase that color's max. Its printed location
> determines when the new pip becomes ready.

There is no Roll Dice step, no Assign Dice step, no Dice Cup, and no Citizenry.

## Current Design Decision

The recommended minimal ruleset is:

- dice colors become deterministic phase batteries;
- each track has current pips and max pips;
- gaining a die increases that color's max; Cup, Citizenry, and World
  placement determine readiness;
- Red pips are Settle workers for every World;
- Credits are Trade income and can recharge spent colored pips during Manage
  Empire unless a specific tile conversion says otherwise;
- Credits are not wild workers by default;
- Yellow is Alien-specific by default.

The goal is not to make a new Roll for the Galaxy game. It is to keep tile
building, goods, shipping, credits, and tableau scoring intact while removing
the roll-and-reassign luck layer.

For the first playtest, do not add general free recharge beyond printed Cup
placement, tile-specific retuning, or a new dummy-player system. Those are
tuning knobs after the core battery loop is tested at the table.

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
Alien     Yellow  0 1 2 3 4 5 6
```

Blue, Brown, Red, Green, Purple, and Yellow have two values:

- Current pips: how many pips are available to spend now.
- Max pips: the highest that color can recharge to.

Red is the only Settle track. Every World spends Red pips as Settle workers and
may store progress. Red current can be recharged during Manage Empire like
other tracks.

There is no White track because the retained tile set has no White die grants.
Credits are unlimited chips, tracked as a separate chip count instead of on a
track.

Recommended physical tracking:

- For phase batteries, put the colored die on the track to show current pips.
- Put a cube or marker on the track to show max pips.
- Keep Credit chips beside the board.

Example:

```text
Red track: 0 1 2 3 4 5 6
              D   M
```

The red max marker is on 4 and the red die is on 3, so you have 3 current Red
Settle pips and can recharge as high as 4.

## Color Map

Use these phase mappings:

```text
Blue    Explore
Brown   Develop
Red     Settle
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
Red     3/3
Green   3/3
Purple  3/3
Credits 1 unlimited chip
Yellow  0/0
```

Older examples below may still use 2/2 as small numbers for illustration.

Then draft goals and starting tiles:

1. Remove six-cost Developments from the normal tile bag. Reveal or set aside
   `2 + player count` six-cost Developments as the end-game goal pool. Each
   player chooses 2 candidate goals from that pool. Choose goal candidates
   before drafting starting tiles so the starting tableau can support them.
2. Reveal `2 + player count` Faction tiles and `2 + player count` Home Worlds.
3. Beginning with the last player in turn order and proceeding counterclockwise,
   each player drafts one Faction tile and one Home World. Remove undrafted
   starting tiles from the game.
4. Apply starting die gains using their printed locations. Cup pips begin
   ready; Citizenry and World pips increase max only.
5. Choose a starting specialization: Blue Explore or Brown Develop. Increase
   the chosen track's max and current by 1. This is a ready starting pip. With
   no printed gain in that color, the chosen track begins round 1 at `4/4`.
6. Draw starting Game Tiles into the Construction Zone as usual: one
   Development and one World.

Unused six-cost goals are left out unless an Explore effect later adds them.

Example:

```text
Starting Red is 2 Military.
Your Home World grants one Military die to your Cup.
Military maps to Red.
Red 2/2 becomes 3/3.
```

If a starting tile places a die as a Good on that World, place a Good marker on
that World, increase the granted color's max, and do not increase current.

## Round Structure

Each round has four steps:

1. Select Phases
2. Reveal Phases
3. Resolve Selected Phases
4. Manage Empire

There is no Roll Dice step and no Assign Dice step.

During Select Phases, each player secretly selects eligible phases:

- Solo: select 2 eligible phases.
- All multiplayer games, including 2-player: each player selects 1 eligible
  phase.

A phase is eligible only if you have at least 1 ready pip for that phase. For
example, Explore requires at least 1 current Blue pip, Develop requires at least
1 usable Develop pip and a Development in your Construction Zone, Settle
requires at least 1 usable Red pip and a World in your Construction Zone, and
Ship requires at least 1 current Purple pip and at least 1 Good.
Selecting a phase does not spend or exhaust the pip that made the phase
eligible.

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
Spend 1 Red pip    = one normal-World Settle worker
Spend 1 Green pip  = one Produce worker
Spend 1 Purple pip = one Ship worker
```

Credits are not workers. Credits are chip resources for Trade income, recharge,
and tile effects unless a specific rule calls for Credit spending.

For Produce and Ship, spend native pips one at a time. Stop when you run out of
pips or cannot use more of that phase. For Explore, Scout may spend multiple
pips as search depth while still keeping only one tile; Stock spends pips one
at a time.

For Develop, Brown pips are build workers and can be saved as progress on any
Development in your Construction Zone. For Settle, every World spends Red pips
as Settle workers and may store progress. You may Settle any World in your
Construction Zone that you can legally pay for.

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

- Develop by spending Brown or eligible Yellow into Developments.
- Settle any World by spending Red or eligible Yellow pips.
- Ship with Purple.

Explore and Produce do not occur this round because no one selected them.

After spending:

```text
Brown   0/2
Red     2/3
Purple  0/2
```

If a Development costs 2 and you have Brown `1/2`, you may spend 1 Brown and
mark 1 progress. Later, when you spend another Develop pip into that card, it
completes.

## Explore

When Explore occurs, spend Blue pips.

Explore can Scout or Stock.

Scout is a single-tile action. Spend one or more Explore pips, then look through
one more candidate tile of the needed type than the number of pips spent. In
other words, spending `N` Blue searches `N + 1` candidates. Keep one tile and
put it on the matching construction area. Return the other candidates to the
tile supply. The bonus candidate makes Blue-grant tiles reachable from the
starting `3/3` Explore track without increasing every track's starting max.

Instead of Scouting or Stocking, spend 1 Blue pip to take one additional
six-cost Development goal from the goals left out during setup. Keep it in your
goal area, not a construction area. If taken before the commit trigger, add it
to your candidates and still commit only one when the trigger occurs. If taken
after you have committed, it becomes an additional committed goal and is scored
or penalized separately.

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
Builder    Development cards and end-game goal setup.
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
Look through 3 World candidates.
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

Payment may be any mix of pips:

- Brown pips;
- Yellow pips, if the Development is Alien-tagged.

If the Development's stored progress plus spent pips reaches the full cost,
complete it. Credits are not wild Develop workers by default.

If a Development's progress reaches the full cost, complete that Development:

1. Move it to your tableau.
2. Apply any immediate converted effects.

Use normal Development costs. Six-cost Developments are removed from the normal
bag and handled as end-game goals.

Example:

```text
Brown is 1/2.
One Development costs 3.
Spend 1 Brown.
Mark 1 progress on the Development.
Brown becomes 0/2.
```

Example:

```text
Brown is 2/2.
One Development costs 4.
Spend 2 Brown.
Mark 2 progress on the Development.
Brown becomes 0/2.
```

Later:

```text
Brown is 1/2.
The Development has 2 progress and needs 2 more.
Spend 1 Brown now, then spend another Develop pip in a later Develop phase.
Complete the Development.
```

## Settle

When Settle occurs, use Red for every World.

You may spend Settle pips into any World in your Construction Zone.
World progress is persistent, just like Development progress. You may complete
multiple Worlds in the same Settle phase.

Each World's payment may be any mix of pips:

- Red pips;
- Yellow pips, if the World is Alien Technology.

If a World's stored progress plus spent Settle pips reaches its full cost,
complete the World:

1. Move it to your tableau.
2. Gain any dice listed on the World by pipping up those colors.
3. Gain any listed Galactic Credits.
4. Place a starting Good if the tile's die placement says the die begins on the
   World.

Example:

```text
Red is 2/2.
One normal World costs 2 and grants one Novelty die.
Spend 2 Red to complete it.
Novelty maps to Blue.
Blue 2/2 becomes 3/3.
Red becomes 0/2.
```

## Produce

When Produce occurs, spend Green pips one at a time.

For each Green pip spent, choose one empty non-gray World in your tableau and
place one Good marker on it.

The Green pip is the Produce worker; the Good is represented by a marker, cube,
or spare die. Do not derive a separate Good color from the Green pip.

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

Trade removes the Good and gains Galactic Credits based only on the World's
color:

- Blue/Novelty World: 3 Credits.
- Brown/Rare Elements World: 4 Credits.
- Green/Genes World: 5 Credits.
- Yellow/Alien Technology World: 6 Credits.
- Credits are unlimited chips.

Consume removes the Good and claims exactly 1 VP chip from the pool. There are
no Good-color or Shipper-color matching bonuses in this variant.

Example:

```text
Purple is 2/2.
You have two Goods.
Spend 1 Purple to Trade a Good from a Novelty World for 3 Credits.
Spend 1 Purple to Consume the other Good for 1 VP chip.
Purple becomes 0/2.
```

## Gaining Dice

Whenever a tile says to gain a die, increase that die color's max. The printed
die location determines readiness:

```text
Cup during setup:  increase max and current immediately.
Cup during play:   increase max; free-recharge that pip during Manage Empire.
Citizenry:         increase max only; recharge normally with Credits.
World as a Good:   increase max only and place a Good marker.
```

Procedure:

1. Increase that color's max by 1.
2. Apply the printed Cup, Citizenry, or World placement.
3. The max cannot exceed 6.
4. Any gain beyond 6 is lost and creates no readiness or Good.

Color conversion:

```text
Novelty           Blue
Rare Elements     Brown
Genes             Green
Alien Technology  Yellow
Military          Red
Consumption       Purple
```

Examples:

```text
Blue is 0/2.
You gain one Novelty die to your Cup during play.
Blue becomes 0/3.
During Manage Empire, it free-recharges to 1/3.
```

```text
Green is 0/2.
You gain one Genes die to your Citizenry.
Green becomes 0/3 until recharged with a Credit.
```

```text
Brown is 0/2.
You gain one Rare Elements die on its World.
Brown becomes 0/3 and that World gains a Good marker.
```

```text
Blue is 6/6.
You gain one Novelty die.
Blue stays 6/6. The excess is lost.
```

If a tile grants two dice, increase both max tracks and apply each printed
location. If both dice are the same color, increase that max twice, still
capped at 6.

## Red Dice

In this variant, Military dice map to Red Settle pips.

- gaining a Military die follows its printed location like any other die;
- losing a Military die reduces Red max by 1 and caps current Red to the new
  max;
- every World spends Red pips equal to its cost and may store progress;
- there is no Military-World threshold or exhaustion rule;
- end-game goals that count Military dice count Red max.

Red-grant and Rebel Worlds are ordinary Worlds for construction. Their identity
matters only to printed powers, tags, or goals that explicitly reference it.

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

Yellow starts at `0/0`. When you gain an Alien Technology die, increase Yellow
max and apply its printed location.

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

Credits are not wild workers by default. Develop uses Brown pips. Settle uses
Red workers for every World. A specific tile conversion may still grant or
spend Credits if that is the closest translation of its printed effect.

Credits are unlimited chips. They are not assigned to phases. Each round,
choose how many Credits to spend on Manage Empire recharge and any specific
tile effects that call for Credits.

During Manage Empire:

1. Apply queued Cup-placement free recharges to their original tracks.
2. Spend Galactic Credits to recharge colored tracks.
3. Each Credit recharges 1 current pip on one track.
4. A track cannot recharge above its max.
5. You may distribute Credits among tracks however you choose.
6. If your Credit count is at 0 after Manage Empire, set it to 1 as in the
   base game.

There is no general free recharge in the recommended version. A die placed in
the Cup during play receives its one location-based free recharge during Manage
Empire.

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

Each player has three separate places for tiles:

- Tableau: completed tiles. Starting Faction and Home World tiles begin here.
- Development construction area: unbuilt non-6-cost Development tiles.
- World construction area: unsettled World tiles.

The two construction areas are parallel queues, not stacks. You may build any
tile in the matching construction area; it does not have to be the top, newest,
oldest, leftmost, or rightmost tile.

Construction area limits:

- Development construction area limit: 3 tiles.
- World construction area limit: 3 tiles.
- Six-cost Development goals are not in either construction area and do not
  count against either limit.

Explore adds tiles to construction areas:

- Scout for a Development: put the chosen non-6-cost Development into your
  Development construction area.
- Scout for a World: put the chosen World into your World construction area.
- Take Goal: spend 1 Blue to put an additional six-cost Development in your
  goal area; it never enters a construction area.
- If the matching construction area is full, you cannot add that kind of tile
  unless a rule first frees space.

Develop construction:

- Develop pips are spent into Development tiles in your Development
  construction area.
- Development progress is persistent. Mark stored progress on each
  Development separately.
- You may split Develop pips among multiple Development tiles.
- When a Development's stored progress reaches its cost, complete it
  immediately: move it from the Development construction area to your tableau
  and apply converted effects.
- Multiple Developments can complete in one Develop phase.
- Credits are not wild Develop workers by default.

Settle construction:

- Worlds are paid with Red Settle pips, plus eligible Yellow pips for
  Alien Technology Worlds.
- World progress is persistent. Mark stored progress on each World
  separately.
- You may split Settle pips among multiple Worlds.
- You may settle or progress any World in your World construction area.
- Multiple Worlds can complete in one Settle phase.
- When a World completes, move it from the World construction area to your
  tableau and apply converted effects.

Six-cost Development goals:

- Six-cost Developments are removed from the normal tile bag during setup.
- They are goal cards, not construction tiles.
- Candidate and committed goal cards are kept beside the player area.
- They do not count as tableau tiles, Development construction tiles, completed
  Developments, or 12-square end-condition tiles.
- They score only through the goal system at game end.

The tableau end condition checks only tiles in your tableau. Starting Faction
and Home World tiles count normally for tableau size and scoring, as in the
base game.

## Reassign Powers

Reassign powers temporarily route ready pips; they never move max capacity
between tracks.

When a selected destination phase resolves:

1. Choose a current pip allowed by the printed reassign power.
2. Spend it from its original color track.
3. Use it as one worker in the printed destination phase.
4. When recharged later, it returns to its original color track.

Each reassign power may be used at most once per round unless its text says
otherwise. A routed pip does not make a phase eligible for secret selection;
the phase still needs its native ready pip or must be selected by another
player. Reassigning Blue to an occurring Develop phase, for example, reduces
current Blue by 1 and performs one Develop worker action; Brown current and max
do not change.

For Produce and Ship, Reassign substitutes only the pip being spent:

- routing an allowed pip to Produce performs one normal Produce action and
  places one Good marker on a chosen empty non-gray World;
- routing an allowed pip to Ship performs one normal Ship action: Trade using
  the World color or Consume for exactly 1 VP;
- the routed pip's source color does not change the Good, Trade value, or
  Consume value.

Use the source, quantity, destination, and Dictate restrictions printed on the
Development. The simulator's retained tile data records which Developments
have reassign powers but not their detailed restrictions, so it approximates
each non-goal reassign Development as one any-source, any-destination route per
round.

## Other Tile Power Conversion

Use these conversions until each tile is individually tuned:

```text
Gain/recruit a die:
Increase max; if no location is given, treat it as Citizenry.

Place a die in your Cup:
Increase max and free-recharge it during Manage Empire.

Place a die in your Citizenry:
Increase max only.

Place a die on a World as a Good:
Increase max only and place a Good marker on that World.

Return a used worker to your Cup instead of Citizenry:
Queue one free recharge of that worker's original color for Manage Empire.

Act as if you have an extra worker:
Gain 1 temporary pip in that phase this round.

Reduce a Develop or Settle cost:
Reduce the pips required by that amount.

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
- chosen six-cost Development goal results.

Six-cost Developments are not built from the normal bag. They are delayed
end-game goals.

Setup:

1. Remove six-cost Developments from the normal bag.
2. Set aside `2 + player count` six-cost Developments as the goal pool.
3. Each player chooses 2 six-cost Development goal candidates before the
   starting-tile draft.

Commit trigger:

- once half of the VP chips are gone; or
- once any player has 6 completed Developments/Worlds.

When either trigger occurs, each player chooses one of their two candidate
goals as their committed end-game goal. The other candidate goes back into the
Development market row, or its reverse side may be used as a World.

Explore option:

- instead of Scout or Stock, spend 1 Blue to take another six-cost Development
  goal from those left out at setup;
- before the commit trigger, it is another candidate; after the trigger, it is
  another committed goal and is scored or penalized separately.

Scoring:

- score committed six-cost Development goals only if their minimum condition is
  met;
- lose 6 VP for each chosen Development goal whose minimum condition is not
  fulfilled.

In solo, each six-cost Development goal is tied to a named solo condition. To
fulfill the goal, meet that named condition's non-score requirement. Then score
the six-cost Development's converted bonus. If you miss the named condition,
score `-6 VP` for that committed goal.

```text
Free Trade Association   Novelty: 2+ Novelty Worlds.
Galactic Bankers         Satisfied Populace: ship 4+ Goods.
Galactic Exchange        Alien Contact: 1+ Alien World.
Galactic Federation      Developer: 4+ Developments.
Galactic Renaissance     Builder: 8+ completed tiles.
Galactic Reserves        Industrial: difficulty's Industrial max-pip target.
Mining League            Rare Elements: 2+ Rare Worlds.
New Economy              Production: 3+ production Worlds.
New Galactic Order       Military: Red max 5+.
System Diversification   Diverse: 4+ World colors.
```

Open playtest wording:

- clarify whether multiple players may choose the same goal from the
  `2 + player count` pool, since that pool is smaller than two unique goals per
  player at 3p+.

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
that you have not already marked.

Some named conditions are tied to a specific six-cost Development goal. To mark
one of those conditions, you must:

1. meet the condition's VP threshold;
2. have committed the matching six-cost Development goal this game;
3. fulfill that goal's named-condition requirement.

For a campaign game, select the six-cost goal that matches the campaign
condition being attempted. Random goal availability does not determine whether
that campaign condition can be attempted. The selected goal still follows the
normal commitment timing and scoring rules.

The committed six-cost goal also scores normally: if fulfilled, score its
converted bonus; if missed, lose 6 VP. Score-only conditions do not require a
six-cost Development. Colonizer and Discovery are not currently tied to a
six-cost Development and use only their printed condition.

If you cannot mark a new condition, you lose the campaign. If you mark all four
conditions after four successive games, you win the campaign.

Choose a solo difficulty before the first game. These thresholds are calibrated
for the 15-round solo cap, two player phase selections, two Dummy phase cards,
starting colored tracks at 3/3, a 24-chip solo VP pool, and fixed 1-VP Consume:

```text
Difficulty  Great  Triumphant  Epic  Named  Industrial
Easy        22+    26+         30+   24+    17+ max pips
Normal      32+    36+         40+   32+    19+ max pips
Advanced    38+    42+         46+   38+    21+ max pips
Very Hard   44+    48+         52+   44+    23+ max pips
```

Named win conditions:

```text
Great       Score the difficulty's Great VP. No six-cost goal required.
Triumphant  Score the difficulty's Triumphant VP. No six-cost goal required.
Epic        Score the difficulty's Epic VP. No six-cost goal required.
Builder     Named VP, Galactic Renaissance, and complete 8+ tiles.
Developer   Named VP, Galactic Federation, and have 4+ Developments.
Colonizer   Named VP and have 5+ Worlds. No six-cost goal required.
Satisfied Populace
            Named VP, Galactic Bankers, and ship 4+ Goods this game.
Industrial  Named VP, Galactic Reserves, and have the difficulty's Industrial
            max pips.
Production  Named VP, New Economy, and have 3+ production Worlds.
Diverse     Named VP, System Diversification, and have 4+ different World
            colors.
Novelty     Named VP, Free Trade Association, and have 2+ Novelty Worlds.
Rare Elements
            Named VP, Mining League, and have 2+ Rare Worlds.
Alien Contact
            Named VP, Galactic Exchange, and have 1+ Alien World.
Military    Named VP, New Galactic Order, and have Red 5.
Discovery   Named VP and have Blue max 5. No six-cost goal required.
```

Campaign sheets:

```text
Outreach
Great, Colonizer, Builder / Galactic Renaissance, Discovery.

Industrial Base
Triumphant, Developer / Galactic Federation, Industrial / Galactic Reserves,
Production / New Economy.

Sector Survey
Great, Diverse / System Diversification, Novelty / Free Trade Association,
Rare Elements / Mining League.

Alien Contact
Triumphant, Alien Contact / Galactic Exchange,
Diverse / System Diversification, Discovery.

Mastery
Epic, Military / New Galactic Order, Industrial / Galactic Reserves,
Satisfied Populace / Galactic Bankers.
```

For one-off practice, ignore the campaign sheet and simply note every condition
you satisfied.

Solo round structure:

1. Select two player phases. You may select a phase only if you have at least 1
   ready pip for that phase. Selecting a phase does not spend that pip.
2. Reveal two Dummy phase cards. If the deck is empty, shuffle all five Dummy
   phase cards to form a new deck first.
3. The selected phase set is your phases plus the Dummy phases.
4. Resolve selected phases in normal order: Explore, Develop, Settle, Produce,
   Ship.
5. During each selected phase, you may spend usable pips for that phase. If the
   Dummy selected that phase, also resolve that Dummy effect.
6. Manage Empire normally, then check whether the six-cost goal commit trigger
   has been reached.

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

During Develop, you may spend Brown pips. Because the Dummy also selected
Develop, draw one Development tile from the bag and place it face down in the
Dummy row.

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
Look through 3 World candidates.
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
One gray World costs 3.
Red is 3/3.
Spend 3 Red to complete it.
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
Credits 1
Yellow  0/0
```

## Playtest Defaults

Use these defaults:

```text
Starting main tracks: Blue, Brown, Red, Green, and Purple at 3/3
Starting Credits:     1 unlimited chip
Starting Yellow:      0/0
Track max:            6
Credits:              unlimited chips
VP pool:              7 per player
Solo VP pool:         24 total chips
Scoring:              tableau VP + VP chips + chosen 6-cost goals
Free recharge:        0
Yellow mode:          Alien
```

Current playtest note:

Red is a single Settle-worker economy. Gray, Rebel, and Red-grant Worlds have no
special construction shortcut; they pay their full cost in Red like every other
World.

Watch these table metrics:

- Worlds completed per player.
- Stored World progress at game end.
- Credits spent on Red recharge.
- Red at game end.
- Whether Red-grant Worlds create a healthy Settle-capacity ramp.
