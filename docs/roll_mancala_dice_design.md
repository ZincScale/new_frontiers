# Roll for the Galaxy: Mancala Dice Variant

This is the primary Roll prototype in this repository. It replaces the Dice Cup,
roll, and assign steps with a five-section mancala loop. The earlier
phase-battery rules remain in `docs/roll_phase_battery_rules.md` as an archived
tuning branch.

This variant uses the physical dice from the base box as mancala stones. Die
faces do not matter. Dice color remains the die's identity.

## Design Thesis

This version may be simpler than the phase-battery design because dice are no
longer abstract pips. Dice are workers.

Core economy:

- Gaining dice adds workers to the player's mancala.
- Losing dice removes workers from the player's mancala economy.
- Sowing controls where workers are available and which phase the player
  selects.
- Credits buy tempo by funding extra recovery sows from Spent.

This preserves the Roll feel of using dice as workers while Credits recall
spent dice back into circulation. It also makes card text that gains or loses
dice easier to interpret: those cards directly change the player's workforce.

Player board sections:

```text
Explore -> Develop -> Settle -> Produce -> Ship -> Explore
```

Dice colors:

```text
Blue    Explore identity
Brown   Develop identity
Red     Military / Settle identity
Green   Produce identity
Purple  Ship identity
White   Flexible identity
Yellow  Alien Technology identity
```

## Key Design Choice

The recommended mancala direction is:

- die color = identity for gains, losses, tile powers, goods, and end-game
  bonuses;
- board section = what action the die can currently perform.

This makes the mancala movement matter. A red die is still a Military die, but
it only acts as a Settle worker when it is in the Settle section.

Alternative not recommended for first test:

- die color always determines use, regardless of section.

That is simpler, but the mancala board matters much less.

## Ostia And Trajan Lessons

The attached Ostia and Trajan rules point to the same useful core:

- choose a source space that already contains pieces;
- pick up the pieces from that source;
- sow them clockwise around a personal rondel;
- let the final landing space matter.

Trajan uses the final tray as the action tray and checks marker colors there
for Trajan tiles. Ostia chooses a section, produces from that source section,
sows its ships, and performs the action where the final ship lands.

For Roll, the cleanest translation is:

- the final landing section selects the player's phase for the round;
- dice colors in matching sections create small planning bonuses;
- after reveal, selected phases are still shared, as in Roll for the Galaxy.

This keeps the Roll identity. Players still reveal selected phases
simultaneously, every selected phase occurs for everyone, and dice become
workers only when their section's phase occurs.

## Setup

Set up the base game normally, with these changes:

1. Do not give players Dice Cups.
2. Do not use the Roll Dice or Assign Dice rules.
3. Give each player a Mancala Phase board with five sections. Keep Spent dice
   off board as a separate storage area.
4. Use 8 VP chips per player for the shared VP pool.
5. Set starting dice:

```text
Explore   2 blue dice
Develop   2 brown dice
Settle    2 red dice
Produce   2 green dice
Ship      2 purple dice
Spent     2 white dice
Spent     0 yellow dice
```

Then set up starting tiles normally:

1. Give each player one Faction tile.
2. Give each player one Home World tile.
3. Apply any starting die gains from those tiles as physical dice.
4. Draw starting Game Tiles into the Construction Zone as usual: one
   Development stack and one World stack.

For the first prototype, mirror the phase-battery start rather than trying to
recreate base Roll's cup and Citizenry state. This gives every player a working
mancala puzzle immediately.

## Round Structure

Each round has four steps:

1. Mancala Phase Selection
2. Reveal Phases
3. Do Selected Phases in Order
4. Manage Empire

There is no Roll Dice step, no Assign Dice step, no Dice Cup, and no Citizenry.

## 1. Mancala Phase Selection

Each player secretly chooses one source:

- one board section containing at least one die; or
- one color group in Spent.

Use any simple marker, note, or covered phase card to lock the chosen source.
After all players have chosen, reveal sources and sow publicly. For table
clarity, resolve the physical sowing in player order, but players may not change
their chosen source after reveal.

If choosing a board section:

1. Pick up all dice from that section.
2. Choose their order.
3. Sow them clockwise, one die per section, starting with the next section.
4. The section where the final die lands is that player's phase-selection
   section.

If choosing Spent:

1. Choose one color in Spent.
2. Pick up any number of Spent dice of that color.
3. If the color has a matching normal phase, the first die enters at that
   section.
4. If the color is White or Yellow, choose any normal phase section as the entry
   section.
5. Continue clockwise, one die per section.
6. The section where the final die lands is that player's phase-selection
   section.

Spent entry sections:

```text
Blue    enters Explore
Brown   enters Develop
Red     enters Settle
Green   enters Produce
Purple  enters Ship
White   chooses any normal phase section
Yellow  chooses any normal phase section
```

Dice sown during Mancala Phase Selection are available during the same round.
This is important: the sow does both jobs, selecting a phase and positioning
workers.

If the final die lands in a normal phase section, the player selects that phase:

```text
Explore, Develop, Settle, Produce, Ship
```

If a player has no dice in board sections and no dice in Spent, they select no
phase this round. They may still act in phases selected by other players.

## 2. Reveal Phases

Reveal selected phases simultaneously.

Every normal phase selected by at least one player will occur this round. As in
Roll, a player may use workers in any selected phase, even if they did not
personally select that phase.

## 3. Do Selected Phases In Order

Resolve selected phases in normal Roll order:

```text
Explore -> Develop -> Settle -> Produce -> Ship
```

The player who selected a phase receives that phase's normal selected-phase
benefit, if using the base Roll phase-strip bonuses. If multiple players select
the same phase, each of those players receives the selected-phase benefit once.

For an early table test, the selected-phase benefits can be omitted. The mancala
positioning puzzle may already provide enough reward.

## 4. Manage Empire

Manage Empire keeps the normal Roll jobs:

- discard tiles from hand if required;
- collect Credits from completed effects;
- check end conditions;
- prepare for the next round.

There is no automatic recharge. The next round's Mancala Phase Selection is the
free sow that can bring one board section or one Spent color group back into
motion.

During Manage Empire, a player may spend Credits for extra recovery sows from
Spent:

1. Spend 2 Credits.
2. Choose one color group in Spent.
3. Sow it from that color's entry section. Blue, Brown, Red, Green, and Purple
   use their matching phase sections; White and Yellow choose any normal phase
   section.
4. These dice are not used immediately; they are positioned for the next round.

This makes Credits a tempo tool without letting Credits become permanent
workers.

## Gaining Dice

When a tile says to gain a die:

1. Take a die of that color from the shared supply.
2. If the color has a matching normal phase section, add it to that section.
3. If the color is White or Yellow, or if the matching section is at the section
   cap, place the die in Spent instead. It can enter the board through a later
   sow action.

Examples:

- Gain a Military die: add a red die to Settle.
- Gain a Novelty die: add a blue die to Explore.
- Gain an Alien Technology die: add a yellow die to Spent.

This is the mancala replacement for increasing max pips. There is no separate
capacity track. The number of physical dice a player owns is their capacity.

If a tile grants a die and immediately asks the player to use that die, the die
still enters through the normal gain procedure first. It is available only if it
is in a selected phase section or another power explicitly moves or uses it.

## Losing Dice

When a tile says to lose a die:

1. Remove one die of that color from the player's board, Spent area, goods, or
   unresolved workers.
2. Return it to the shared supply.
3. If there are multiple choices, the player chooses unless the tile specifies a
   location or type.

Loss priority for the first prototype:

1. Remove from Spent if possible.
2. Otherwise remove from a board section.
3. Otherwise remove a good.
4. Otherwise remove an unresolved worker.

The priority protects already-committed phase work. A harsher variant could let
losses hit goods first, but that creates more feel-bad turns and more rules
exceptions.

If a player must lose a die color they do not own, nothing happens unless the
tile explicitly says to lose any die instead.

## Tile Verbiage Guide

Use the tile's normal Roll meaning, then translate dice and work into physical
mancala movement. A tile should not create a Wild phase, Alien phase, Dice Cup,
or Citizenry state.

### Die Gain Text

Tile text like "gain a die," "gain a Novelty die," "gain a Military die," or
"recruit a die" adds a physical die to the player's workforce.

Examples:

- "Gain a Novelty die" means take a blue die and place it in Explore. If Explore
  is full, place it in Spent.
- "Gain a Rare Elements die" means take a brown die and place it in Develop. If
  Develop is full, place it in Spent.
- "Gain a Military die" means take a red die and place it in Settle. If Settle
  is full, place it in Spent.
- "Gain a Genes die" means take a green die and place it in Produce. If Produce
  is full, place it in Spent.
- "Gain a Consumption die" means take a purple die and place it in Ship. If Ship
  is full, place it in Spent.
- "Gain an Alien Technology die" means take a yellow die and place it in Spent.
  Yellow has no Alien phase; when recovered, it chooses any normal phase entry
  section.
- "Gain a white die" means take a white die and place it in Spent. White has no
  Wild phase; when recovered, it chooses any normal phase entry section.

### Die Loss Text

Tile text like "lose a die," "lose a Military die," or "lose one of your dice"
removes a physical die from the player's economy.

Examples:

- "Lose a Military die" removes one red die from Spent if possible, otherwise
  from a board section, Good, or construction progress.
- "Lose a Novelty die" removes one blue die from the same set of places.
- "Lose any die" lets the player choose a physical die they own, using the loss
  priority unless the tile specifies otherwise.
- If a tile asks for a color the player does not own, ignore the loss unless the
  tile says to lose any die instead.

### Extra Worker Text

Tile text that gives an extra worker, temporary die, or phase-specific help does
not add a permanent die. Treat it as a one-time worker effect in the named
phase.

Examples:

- "Use one extra Develop die this phase" counts as one temporary Develop worker
  during that Develop phase. It does not enter a mancala section and does not go
  to Spent afterward.
- "Place a die on a Development" may place a worker from the Develop section if
  one is available. If the text clearly grants a temporary die, place a temporary
  marker instead.
- "Reassign a die" may move one unused worker from one normal phase section to
  another normal phase section before that worker is spent. It cannot move dice
  out of Spent, Goods, or construction progress unless the tile explicitly says
  so.

### Cost And Credit Text

Cost reduction keeps its normal meaning but applies at the moment a tile
completes.

Examples:

- "Developments cost 1 less" reduces the completion threshold for one
  Development this round by 1. Existing workers still remain on the tile.
- "Worlds cost 1 less" reduces the completion threshold for one World this
  round by 1.
- "Gain 2 Credits" adds Credits normally, up to the Credit cap.
- "Spend Credits to refresh dice" means spend Credits during Manage Empire to
  recover one Spent color group into the mancala loop.
- If a tile implies Credits can pay a build cost, ignore that payment mode in
  this variant. Developments and Worlds require workers, not Credits.

### Produce And Ship Text

Goods are physical dice on Worlds. They are outside the mancala loop until
Shipped.

Examples:

- "Produce on a Novelty World" places an eligible Produce worker as a Good on
  that World. If the worker is blue, the Good is blue. If the worker is white or
  yellow, the Good keeps that die color.
- "Produce one extra Good" places an extra Good on an eligible empty production
  World. Use an available Produce worker if the tile requires a die; otherwise
  use a temporary marker and convert it to Spent after Ship.
- "Trade a Good" or "Consume a Good" requires a Ship worker in the Ship section
  unless the tile explicitly provides the worker. The shipped Good moves to
  Spent after scoring or trading.
- "Consume for +1 VP" changes the VP payout of that Consume. It does not move
  extra dice by itself.

### Alien And White Text

Alien Technology and white dice are identities, not mancala phases.

Examples:

- An Alien World is still an Alien World for tile tags, scoring, and solo goals.
- A yellow die gained from Alien Technology starts in Spent, then enters any
  normal phase section when recovered.
- If a yellow die is in Settle, it may be used as a Settle worker. If it is in
  Ship, it may be used as a Ship worker.
- A white die is flexible in the same way: it can work only in the normal phase
  section it currently occupies.
- Tile text that refers to "Alien" should be read as an Alien Technology color
  identity, tile tag, or world type. It never creates an Alien phase.

### End-Game Dice Text

Tile text that scores dice or capacity counts owned physical dice.

Examples:

- "Score for Military dice" counts red dice in sections, Spent, Goods, and
  construction progress.
- "Score for Novelty dice" counts blue dice everywhere the player owns them.
- "Score for Alien Technology dice" counts yellow dice everywhere the player
  owns them.
- There is no max-pip track. The number of physical dice owned is the capacity.

## Using Dice

When a phase occurs, dice in that phase's section may be spent as workers for
that phase.

Examples:

- Dice in Explore can Scout or Stock.
- Dice in Develop can be placed on Developments.
- Dice in Settle can be placed on Worlds.
- Dice in Produce can become Goods.
- Dice in Ship can Trade or Consume Goods.

White and Yellow dice do not have their own sections. They can sit in any normal
phase section and work when that phase occurs.

Use Roll-style physical placement:

- Explore: place the worker in the Explore work area, resolve Scout/Stock, then
  move it to Spent.
- Develop: place workers on one Development under construction. Worker progress
  stays on the tile between rounds. During a later Develop phase, add more
  workers to complete it.
- Settle: place workers on one World under settlement. Worker progress stays on
  the tile between rounds. During a later Settle phase, add more workers to
  complete it.
- Produce: place the worker die on an eligible empty World as a Good. It stays
  on that World until Shipped. It does not go to Spent at the end of Produce.
- Ship: place the worker in the Ship work area, Trade or Consume Goods, then
  move the worker to Spent. Shipped Goods also move to Spent after scoring or
  trading.

This keeps the table feel close to Roll: workers are physically assigned to the
thing they are doing, construction progress is visible on tiles, and Goods are
dice sitting on Worlds.

When a die leaves a section to work, that section now has fewer dice for future
sowing. When a die becomes a Good, it is temporarily outside the mancala loop
until it is Shipped.

## Partial Builds

The mancala branch should use partial Develop and Settle progress. It has fewer
available workers than the older pip/credit phase-battery design, so one-shot
builds would make high-cost tiles too brittle.

Construction rules:

- A player may have at most one active Development and one active World under
  construction.
- Workers placed on an active Development or World stay there as progress.
- Credits are not stored as progress and cannot be paid toward construction.
- During Develop, complete a Development if workers on it meet or exceed its
  cost.
- During Settle, complete a World if workers on it meet or exceed its cost.
- When a tile completes, move all workers from that tile to Spent.
- A player may abandon one active construction tile during Manage Empire. Discard
  that tile and move its workers to Spent.

Example:

- A cost-3 Development has 2 brown workers on it from an earlier round.
- During a later Develop phase, the player adds 1 more Develop worker.
- The Development completes, and all 3 workers move to Spent.

This means Develop and Settle are no longer one-shot in the mancala branch. They
remain one-shot only in the archived phase-battery rules.

## Credits And Workers

Credits behave like the base Roll refresh economy. They do not buy build
progress. A Credit never becomes a die, never enters a section, and never gets
placed on a tile.

Credits have one job in the baseline mancala rules:

- During Manage Empire, spend Credits to buy extra recovery sows from Spent.
  This is how multiple Spent color groups can be positioned before the next
  round.

Example:

- Spent contains 2 red dice and 1 green die.
- During Manage Empire, the player spends 2 Credits to recover the red group.
- The red dice sow into the mancala loop from Settle and are available next
  round.
- The green die remains in Spent unless the player spends another 2 Credits or
  uses a later Mancala Phase Selection to recover it.

This keeps dice as the real workforce. Credits help cycle Spent dice back onto
the board, but they do not create new dice and do not finish projects.

## Worker Economy Brake

Nothing prevents a player from using every available worker. That should be a
legal move. The brake is tempo:

- Workers used for Explore, Ship, or completed builds go to Spent.
- Workers used for partial Develop/Settle stay on those tiles and cannot be
  sown until the tile completes or is abandoned.
- Workers used as Goods stay on Worlds and cannot be sown until Shipped.
- A player with an empty board can recover by using the next round's Mancala
  Phase Selection from Spent, but usually returns only one color group before
  needing Credits for more.

Using all workers creates a strong turn now, but the next turn starts with fewer
dice in the mancala loop. Keeping some workers on the board gives better control
over future phase selection and color-match bonuses.

## Section Stone Match Bonuses

Section stone match bonuses are the main reward for planning the mancala
movement. A match happens when one of the five normal phase colors lands in its
matching section during a sow:

```text
Blue in Explore
Brown in Develop
Red in Settle
Green in Produce
Purple in Ship
```

White and Yellow never create section matches because they do not have mancala
sections. They are flexible die identities that can sit in any normal phase
section.

For the main table test, use this rule:

> During each sow action, if the final die lands in its matching section, gain
> that section's match bonus.

Main match bonuses:

```text
Blue in Explore     Draw +1 tile before choosing what to keep.
Brown in Develop    Reduce one Development cost by 1 this round.
Red in Settle       Reduce one World cost by 1 this round.
Green in Produce    Produce one extra Good on an eligible empty World.
Purple in Ship      Gain +1 VP the first time you Consume this round.
```

Only one match bonus can trigger per sow action. If several dice land in
matching sections while sowing, ignore the earlier matches and check only the
final die. The selected phase still comes from the final landing section.

### Faster Economy Variant

Do not use this for the first table test. It is a useful faster-economy variant
if the board feels too tight:

> During each sow action, the first die that lands in its matching section gives
> +1 Credit, max 10.

This is easy to remember and does not change phase math, but simulations showed
that it accelerates the game too much for a 14-16 round target.

### Worker Bonus

Use this only if the mancala board needs a stronger payoff:

> One die in its matching section counts as 2 workers when used in its matching
> phase.

Limits:

- Max one double-worker bonus per phase.
- The double worker must be spent from the matching section.
- The bonus does not apply while the die is a Good.

This makes matching positions exciting, but it can make Develop and Settle much
faster. It should be tested only after the main match bonuses are stable.

## Sowing Limits

A section may hold at most 6 dice.

If a sow would place a die into a full section:

1. Skip that section.
2. Continue clockwise to the next section with space.
3. If every section is full, place the remaining dice in Spent.

Do not return overflow dice to the shared supply. Ownership should change only
through tile effects that gain or lose dice.

This cap is mostly a physical usability rule. It prevents one section from
becoming unreadable without creating a punishment loop.

## Spent Recovery

Spent dice have no board position, so a sow from Spent uses the color's entry
section. Blue, Brown, Red, Green, and Purple enter at their matching phase
sections. White and Yellow choose any normal phase section.

This means each Spent sow returns one color group. To return multiple colors
from Spent before the next round, the player must spend Credits for extra
recovery sows during Manage Empire.

Example:

- Spent contains 1 brown, 1 red, and 1 green die.
- During Mancala Phase Selection, the player can choose the brown die, entering
  at Develop. If it is the only die sown, Develop becomes that player's selected
  phase.
- During Manage Empire, the player spends 2 Credits for an extra recovery sow to
  return the red die, entering at Settle.
- The green die stays in Spent unless the player spends another 2 Credits or uses a
  later Mancala Phase Selection to return it.

Dice sown from Spent during Mancala Phase Selection can be used in the same
round. Dice sown from Spent during Manage Empire are not used immediately; they
are available next round.

## Solo Mode

Solo mode uses the same five-section mancala board, off-board Spent storage, and
a fixed Dummy phase deck.

Setup:

1. Set up one player normally for the mancala variant.
2. Use a 30 VP chip pool.
3. Set Dummy Goods to 0.
4. Shuffle one Dummy phase card for each normal phase:
   Explore, Develop, Settle, Produce, and Ship.
5. Choose one campaign sheet or one win condition set.
6. Play up to 16 rounds.

Each solo round:

1. Choose and sow one source as usual.
2. Reveal two Dummy phase cards.
3. Your final landing phase and both Dummy phases are selected this round.
4. Resolve all selected phases in normal phase order.
5. Resolve the Dummy effects.
6. Manage Empire normally, including recovery sows from Spent.

Dummy effects:

```text
Explore   Dummy claims 1 Development and 1 World.
Develop   Dummy claims 1 Development.
Settle    Dummy claims 1 World.
Produce   Dummy Goods +1, max 4.
Ship      Drain 2 VP chips per Dummy Good, minimum 2, then Dummy Goods = 0.
```

Solo ends when the round limit is reached, the VP pool is exhausted, or the
player reaches 12 tableau squares. Capacity-based solo goals count owned
physical dice across sections, Spent, Goods, and construction progress.

Solo win conditions:

```text
Great              Score 32+ VP.
Triumphant         Score 34+ VP.
Epic               Score 35+ VP.
Builder            Score 28+ VP and complete 7+ tiles.
Developer          Score 28+ VP and have 4+ Developments.
Colonizer          Score 28+ VP and have 6+ Worlds.
Satisfied Populace Score 28+ VP and score 8+ VP chips.
Industrial         Score 28+ VP and own 17+ physical dice.
Production         Score 28+ VP and have 4+ production Worlds.
Diverse            Score 28+ VP and have 3+ different World colors.
Novelty            Score 28+ VP and have 2+ Novelty Worlds.
Rare Elements      Score 28+ VP and have 2+ Rare Worlds.
Alien Contact      Score 28+ VP and have 1+ Alien World.
Military           Score 28+ VP and own 4+ red dice.
Discovery          Score 28+ VP and own 4+ blue dice.
```

Campaign mode:

Choose one campaign sheet. Play four games in a row. At the end of each game,
mark exactly one satisfied condition on that campaign sheet that you have not
already marked. If you cannot mark a new condition, you lose the campaign. If
you mark all four conditions after four successive games, you win the campaign.

Campaign sheets:

```text
Outreach
Great, Colonizer, Builder, Industrial.

Industrial Base
Triumphant, Developer, Industrial, Production.

Sector Survey
Triumphant, Diverse, Novelty, Rare Elements.

Alien Contact
Epic, Alien Contact, Military, Discovery.

Mastery
Epic, Novelty, Rare Elements, Military.
```

For one-off solo practice, ignore the campaign sheet and record every solo win
condition you satisfied.

Prototype validation:

```text
Automated tests cover:
- multiplayer setup, sowing, shared selected phases, partial builds, goods,
  losses, recovery sows, and shipping;
- solo Dummy phase selection and physical-dice capacity summaries.
- final-die match bonuses for phase selection, Develop cost reduction, Produce
  bonus Goods, and Ship bonus VP.

Smoke simulations run:
- 100 four-player multiplayer games with balanced, builder, producer, and
  shipper strategies;
- 100 one-off solo games with the balanced strategy;
- 100 campaign attempts each for Outreach, Industrial Base, Sector Survey,
  Alien Contact, and Mastery after the match-bonus implementation.

Current status:
- The rules execute without runtime failures in both multiplayer and solo.
- Multiplayer produces normal endgame scoring and tableau completion.
- One-off balanced solo averaged about 30.5 VP over 300 games. Score-only
  condition rates were about Great 41%, Triumphant 32%, and Epic 26%.
- Four-game campaign sweeps over 100 attempts each landed at about Outreach
  16%, Industrial Base 16%, Sector Survey 8%, Alien Contact 8%, and Mastery 6%.
  Treat these as simulator-tuned table-test targets, not final published
  balance.
```

## Open Questions

- Is one color group per Spent sow too restrictive, or should a recovery sow be
  allowed to move any three Spent dice?
- Is the gentle loss priority correct, or should lost dice be chosen freely by
  the player?
- How should White and Yellow choose entry sections when recovered from Spent:
  freely, or by a stricter rule?
- Does phase selection by sowing cause too many unwanted phase selections, or is
  that pressure the point of the system?
- Is the no-bonus baseline too flat at the table even though the simulator pace
  is better?

## Recommended Prototype Path

First full mancala table test:

1. Use physical dice as workers and mancala stones.
2. Use partial Develop and Settle builds.
3. Use Mancala Phase Selection: sow first, final landing section selects the
   player's phase.
4. Let phases remain shared after simultaneous reveal, as in base Roll.
5. Spend Credits during Manage Empire for extra recovery sows from Spent.
6. Let card effects that gain or lose dice add or remove physical workers.
7. Use the main final-die section stone match bonuses.
8. Do not use the faster-economy +1 Credit bonus in the baseline test.

Test the Worker Bonus only after the economy is stable.
