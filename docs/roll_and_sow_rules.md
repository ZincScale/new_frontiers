# Roll for the Galaxy: Roll & Sow Prototype

Status: experimental mechanism test for 1-4 players. This does not replace the
main Phase Battery rules unless a later playtest adopts it.

## What This Prototype Tests

Roll & Sow keeps Roll's dice, tiles, Credits, Goods, construction, and phase
powers. It changes what happens after dice are rolled:

1. rolled dice remain in five phase bowls;
2. players secretly select a nonempty bowl;
3. every selected phase activates that bowl for every player;
4. useful dice are spent as workers;
5. every unused die is sown clockwise into later bowls.

The intended tension is that another player can activate your bowl before you
want it activated. You may benefit from their phase, but your unused dice will
move and change your future choices.

## Components

Use the base Roll for the Galaxy components, plus one printed Roll & Sow board
per player. Each board has five bowls in this order:

```text
Explore -> Develop -> Settle -> Produce -> Ship -> Explore
```

Use the normal player screens and phase tiles. A player needs a way to select a
phase secretly without moving a die out of its bowl; place the matching phase
tile or a phase marker behind the screen.

Remove all six-cost Developments from the normal tile supply. They are delayed
end-game goals, not construction tiles. Keep their physical tiles near the
shared goal reference.

## Setup

1. Shuffle the 10 six-cost Developments and reveal `2 + player count` as the
   shared goal pool. Each player records or marks 2 candidate goals. Candidates
   are not exclusive: multiple players may choose the same revealed goal.
2. Use the normal starting Faction and Home World procedure. Choose starting
   tiles after goal candidates so players can draft toward a goal. Apply printed
   die gains using **Gaining Dice** below.
3. Give each player 5 White Home dice. Roll 3 and place each in the bowl shown
   by its face. Put the other 2 in Citizenry.
4. Give each player 1 Credit. Credits are unlimited chips; the dial cap is not
   used.
5. Give each player one Development and one World under construction. A player
   may later hold up to 3 Developments and 3 Worlds under construction.
6. Make a VP-chip pool of 7 chips per player.
7. Randomize the ordinary tiles. Keep a face-down discard pile beside the bag.
   Keep unrevealed six-cost goals separate from this bag.

Starting-tile dice are in addition to the 5 White dice. A printed Cup gain is
rolled immediately. A Citizenry gain begins in Citizenry. A World gain begins
as a Good on that World.

## Round Sequence

Each round has five steps.

### 1. Select

Each player secretly selects one nonempty bowl. Reassign powers may move dice
only after choosing that bowl and before selections are revealed. A Reassign
power does not change a die's color.

A player with no dice in any bowl selects nothing this round.

### 2. Reveal

Reveal simultaneously. Every phase selected by at least one player will occur.

In a two-player game, also roll one White die from the supply. Its face adds
that phase this round, following the normal two-player Roll rule.

### 3. Resolve Selected Phases

Resolve selected phases in normal order:

```text
Explore -> Develop -> Settle -> Produce -> Ship
```

When a phase begins, every player activates its matching bowl, even if another
player selected the phase. Pick up all dice currently in that bowl. Dice sown
into a later selected bowl can therefore activate later in the same round.

Choose how many dice to spend as described under **Phase Actions**, including
zero. After the action, sow all unused dice from the activated bowl. Printed
phase powers resolve normally when their phase occurs, even if their owner had
no die in that bowl.

### 4. Manage Empire

Recruit dice from Citizenry for 1 Credit each. As in Roll, recruit as many as
you can afford. Roll every recruited die immediately and put it in the bowl
shown by its face. Assign a Wild face to any bowl.

If a player has 0 Credits after recruiting, set their Credits to 1.

After recruiting, you may Recall dice from construction progress or Goods and
roll them immediately into their face bowls. At minimum, if all five bowls are
empty, you must Recall one such die if possible. Remove recalled construction
progress or the recalled Good normally. This prevents a player from becoming
locked out with every die committed off-board.

### 5. Check End Of Game

After Manage Empire, check the six-cost commitment trigger. Finish the round if
the VP pool is empty or any player has at least 12 tableau squares. Score normal
Roll VP plus committed six-cost goals.

## Activating And Sowing

Dice are removed from a bowl before its action. Their destinations depend on
whether they are used.

| Die use | Destination |
|---|---|
| Explore | Citizenry after Scouting or Stocking |
| Develop | stays as progress; all progress dice go to Citizenry when the Development completes |
| Settle | stays as progress; all progress dice go to Citizenry when the World completes |
| Produce | becomes the Good on the chosen production World |
| Ship | the Shipper and shipped Good both go to Citizenry |
| Unused | sown clockwise into phase bowls |

To sow, place the first unused die in the next bowl clockwise, the second in the
following bowl, and so on. Continue around the loop as often as necessary. The
player chooses the order of different-colored dice being sown. Bowls have no
capacity limit.

Example: Develop is selected. Mira activates 3 dice in Develop but needs only 1
to complete a Development. That die goes to Citizenry with any older progress
dice. She sows the other 2 dice: one into Settle and one into Produce. If Settle
or Produce is also selected this round, the newly sown die will activate there.

## Phase Actions

### Explore

Choose Scout or Stock.

**Scout:** spend 1 or more Explorers together. The first die inspects 4 tiles;
each additional die inspects 1 more tile. Draw that many physical tiles and
inspect both sides. Keep 1 tile on either side and add it to the matching
construction row. Put rejected tiles in the face-down discard pile. When the
bag cannot supply the full draw, shuffle the discard pile into a new bag.

```text
tiles inspected = 3 + dice spent
```

Scout may be performed only once per Explore activation. You may spend fewer
dice than are present and sow the rest.

**Stock:** instead spend exactly 1 Explorer to gain 2 Credits. Sow all other
Explorers. Alien Archeology changes an Alien Stock to 4 Credits as printed.

**Claim Goal:** instead spend exactly 1 Explorer to take one unrevealed
six-cost Development from outside the shared setup pool. Before the commitment
trigger it becomes another candidate. After commitment it becomes an additional
committed goal and will score or suffer the penalty independently. Sow every
other Explorer.

An extra virtual Explorer from a tile power adds 1 candidate without requiring
or moving a physical die. Alien Research Ship adds 2 candidates. Alien Research
Team may keep the printed extra tile, subject to the construction-row limit.

### Develop

Spend Developers one at a time as permanent progress on any Development under
construction. A die pays 1 point of cost. You may split dice among several
Developments and may complete several in one phase.

When a Development is complete, move it to the tableau, resolve its immediate
effects, and move all dice on it to Citizenry. Cost reductions reduce the number
of dice required and never reduce a Development below cost 1.

### Settle

Settle works like Develop. Spend Settlers one at a time as permanent progress
on any World under construction. Red is not a separate military system in this
prototype: every World costs settlers equal to its printed cost. Multiple
Worlds may complete in one phase.

When a World is complete, move it to the tableau, resolve its immediate effects,
and move all dice on it to Citizenry. Printed World cost reductions apply and
never reduce a World below their printed minimum.

### Produce

Spend any number of Producers one at a time. Each places itself as a Good on a
chosen empty, non-gray production World. A World normally holds at most one
Good. Sow every unused die.

### Ship

Spend any number of Shippers one at a time. Each ships one Good. Choose either:

- **Trade:** gain Credits from the World color: Novelty 3, Rare Elements 4,
  Genes 5, Alien Technology 6.
- **Consume:** gain 1 VP chip from the shared pool.

After shipping, move both the Shipper and Good dice to Citizenry. There is no
Shipper-color or Good-color matching bonus in the basic action. Resolve printed
Trade and Consume powers normally.

## Gaining And Losing Dice

Printed die location is preserved.

- **Cup:** gain the die, roll it immediately, and place it in its face-matching
  bowl. A Wild may enter any bowl.
- **Citizenry:** gain the die in Citizenry. It costs 1 Credit to recruit later.
- **World:** gain the die as a Good on that World. It does not roll first.

To lose a die, remove an owned die using the printed restriction. Prefer
Citizenry, then bowls, Goods, and construction progress unless the power says
otherwise.

## Printed Powers

Use the spreadsheet/base-game text wherever its concept still exists.

- Reassign powers temporarily move a legal source die to their printed
  destination during Select. They do not alter die color.
- A routed Producer or Shipper performs the ordinary destination action; source
  color does not change the Good, Trade value, or Consume value.
- Extra phase workers are virtual workers for that phase. They do not become
  owned dice and are not sown.
- Development and World cost reductions reduce required progress dice.
- Cup/Citizenry/World die placement follows **Gaining And Losing Dice**.
- Phase-end Credit and VP powers trigger whenever that phase occurs.

Advanced Logistics and Improved Reconnaissance have no additional effect
because construction is already parallel and a Scout may already choose either
side. Backup Planning should be read as one unrestricted Reassign for this
prototype because Dictate is not separately modeled.

## Six-Cost End-Game Goals

Goal cards remain outside the tableau and construction rows. They do not grant
their printed ongoing phase powers, do not add their printed 6 VP, and do not
count toward the 12-square end condition. Only their converted minimum and
printed end-game bonus apply.

### Commitment

Commit goals after Manage Empire when either condition first occurs:

- half of the starting VP chips are gone; or
- any player has completed 6 Developments/Worlds.

Each player commits 1 of their candidates. Unchosen shared candidates remain in
the central pool because another player may have marked them. If the game ends
before either trigger, commit immediately before final scoring.

Each goal claimed through Explore after this trigger is immediately committed.
A player may have several committed goals; score each independently.

### Minimums And Bonuses

A fulfilled goal scores its converted version of the spreadsheet's printed
end-game bonus. An unfulfilled goal scores **-6 VP** instead. The goal itself is
included where its original formula would normally count the built six-cost
Development.

| Goal | Minimum to avoid -6 VP | Fulfilled bonus |
|---|---|---|
| Free Trade Association | 2+ Novelty Worlds | Half total Novelty World cost, rounded up |
| Galactic Bankers | Ship 4+ Goods | 1 VP per Development, including this goal |
| Galactic Exchange | 1+ Alien Technology World | 1 VP per different die color owned |
| Galactic Federation | 4+ Developments | One third total Development cost including this goal, rounded up |
| Galactic Renaissance | 8+ completed tiles | 1/2/3/4... VP for 1/3/6/10... VP chips |
| Galactic Reserves | 10+ owned dice | 1 VP per Good remaining |
| Mining League | 2+ Rare Elements Worlds | 2 VP per Rare Elements World |
| New Economy | 3+ production Worlds | 1 VP per non-Reassign Development, including this goal |
| New Galactic Order | 5+ Military dice | 2 VP per 3 Military dice owned, rounded up |
| System Diversification | 4+ World colors | Half total Reassign-Development cost including this goal, rounded up |

The 10-die Industrial minimum is the Roll & Sow conversion of Phase Battery's
max-pip requirement. It is a playtest value, not printed Roll text.

## Provisional Solo Test

Solo is included only as a loop test; its difficulty has not been tuned.

1. Set up one player, a 24-chip VP pool, and the normal 3-card shared goal pool.
2. Shuffle one card for each of the five phases.
3. Each round, select one nonempty bowl and reveal one phase card. Both phases
   occur; if they match, the phase occurs once.
4. Discard the phase card. Reshuffle all five after the deck is exhausted.
5. End after 20 rounds, 12 tableau squares, or an empty VP pool.

Record final VP, completed tiles, dice owned, and unused dice sown. Do not use
existing campaign thresholds for this untuned mode.

## First Playtest Questions

After playing, answer these before changing numbers:

1. Did an opponent ever activate a bowl earlier than you wanted?
2. Did sowing create a plan for a later phase, or was it only handling?
3. Were Credits scarce enough to make Citizenry recruitment painful?
4. Did seeing 4+ tiles make Explore satisfying without making tile choice easy?
5. Did construction dice feel trapped compared with Produce and Ship dice?
6. How many distinct phases occurred per round?
7. Did the goal candidates guide tile choices, or merely add end scoring?
8. Was any committed goal an automatic success or unavoidable -6 VP?
