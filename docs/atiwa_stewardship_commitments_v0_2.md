# Living Landscape: Stewardship Commitments Prototype

> **Previous experiment:** This v0.2 benefit-plus-constraint prototype remains
> a comparison baseline. The active design experiment is the public,
> declining-reward Open Commitment race in
> `docs/atiwa_open_commitments_v0_3.md`. Do not combine the two modules during
> initial testing.

## Design Contract

- **Status:** Experimental rules prototype; synthetic-model testing only
- **Version:** 0.2-draft
- **Base game required:** *Atiwa*
- **Players:** 1-4
- **Scope:** Five benefit-plus-constraint Stewardship Commitments replacing
  the v0.1 scoring-only Commitments during this experiment

This document defines the first benefit-plus-constraint experiment for
*Living Landscape*. It does not overwrite the v0.1 scoring-only contract.
The experiment must be evaluated before the main contract, reference sheet,
or print-and-play files are revised.

The experiment tests one proposition: a personal Commitment can make a different
Atiwa engine competitive by granting a narrow benefit while closing the most
obvious normal use of the resources it improves.

## Design Benchmark: Fields of Arle

*Fields of Arle* and its *Tea & Trade* expansion are useful benchmarks for the
kind of strategic variety Living Landscape should create, but not for the
amount of machinery it should add.

*Fields of Arle* produces different strategies from a broad economic sandbox:
players begin symmetrically, then diverge through seasonal actions and their
investments in tools, land, animals, buildings, vehicles, goods, and travel.
*Tea & Trade* broadens that network with tea, ships, trade, fishing, ditches,
and additional buildings. It primarily adds routes and connections rather than
assigning players restrictive roles.

Atiwa has a much narrower and more strongly coupled ecological engine. Adding
general bonuses for trees, bats, goats, gold, or trained families would tend to
strengthen the same successful engine rather than produce Arle-like variety.
Living Landscape must therefore create variety more surgically:

- Each Commitment should alter a resource conversion or spatial rule, not add
  an end-game scoring target.
- Its benefit should affect at least two kinds of decisions, such as worker
  placement, token placement, feeding, or maintenance.
- Its restriction should create a recurring opportunity cost that cannot be
  ignored by following ordinary efficient play.
- A Commitment should enable a strategic lane without prescribing a complete
  victory script; players must remain able to combine adjacent systems and
  respond to the Terrain display.
- Landscape Priorities should later vary which lanes are attractive in a
  particular game, much as a variable building supply changes the value of
  investments in Fields of Arle.

Do not add an Atiwa equivalent of Tea as a universal action booster. In Atiwa's
tighter economy, a broadly useful accelerator would likely reinforce the
strongest base-game route and smooth away the distinctions between
Commitments.

The expansion target is therefore not a compressed version of Fields of Arle.
It is at least five genuinely different solutions to Atiwa's existing feeding,
capacity, and ecology problem, delivered with low component and rules overhead.

## Module Structure

The first balance tests use these Commitments without Landscape Priorities so
the effect of each benefit and restriction can be observed in isolation. After
the five Commitments pass isolated tests, combine them with only the
non-reinforcing Landscape Priorities. The five Commitments below replace the
twelve scoring-only Commitments from v0.1 during this experiment.

After completing normal setup, including revealing the initial Terrain cards
and action space tiles:

1. Shuffle the five Stewardship Commitments.
2. In solo or two-player play, deal two to each player. For a targeted test,
   assign the Commitment being tested instead.
3. Each player secretly chooses one Commitment.
4. Reveal all chosen Commitments simultaneously before the first worker
   placement.
5. Return unchosen Commitments to the box.

The five-card prototype does not support a normal deal-two setup at three or
four players. At those counts, assign Commitments for targeted testing. Expand
the set to at least eight cards before testing normal four-player selection.

A Commitment remains in effect for the entire game. It provides no end-game
points. Its ongoing benefit is the reward for accepting its restriction.

## General Commitment Rules

- A Commitment never grants an additional worker or worker placement.
- A Commitment cannot remove or move pollution.
- A Commitment cannot create a token if the player has none of that token left on
  their supply board or nowhere legal to place it.
- Normal placement, spending, feeding, maintenance, and pollution rules apply
  unless the Commitment explicitly changes one of them.
- If a benefit cannot be taken completely, it is lost unless the Commitment says
  "up to."
- Restrictions are mandatory, including when declining a Commitment's benefit would
  otherwise be preferable.
- Commitment cards are not Terrain cards, Location cards, or tableau cards.

## Prototype Commitments

### SC01 - Wildlife Warden

**Benefit:** During step 2, Wild Animals, Trees, and Fruit, if your wild
animals cause you to collect at least one tree, you may take one fruit from
your supply board and place it on one of those newly collected trees.

**Restriction:** You may not spend wild animals during Feeding.

**Intended route:** Preserve wildlife, establish orchards earlier, and solve
food demand through goats, fruit, gold, or a smaller and better-trained
population.

### SC02 - Pastoral Cooperative

**Benefit:** When calculating food demand, subtract 2 for each goat in your
tableau instead of 1.

**Restriction:** You may not spend goats to satisfy food demand after it has
been calculated.

**Intended route:** Build a stable recurring goat economy instead of treating
goats as emergency food.

### SC03 - Distributed Settlement Planner

**Benefit:** Each time you acquire a Location card, pay 1 less gold, to a
minimum cost of 0 gold. Tree costs are unchanged.

**Restriction:** No Location card in your tableau may contain more than two
families. This does not reduce the number of houses or the number of fruit bats
that can occupy otherwise legal spaces.

**Intended route:** Build a broader network of small communities instead of
concentrating families in the most efficient high-capacity Locations.

### SC04 - Bat Conservationist

**Benefit:** For your first fruit bat action each round, move 2 fruit bats to
your Night card instead of 3. The action still spends 1 fruit and collects 1
tree. Further fruit bat actions that round require 3 fruit bats normally.

**Restriction:** You may not spend fruit bats during Feeding.

**Intended route:** Use a protected bat population to establish trees more
reliably while solving food demand without consuming bats.

### SC05 - Forest Reserve Keeper

**Benefit:** The first Terrain card you acquire becomes your Reserve; place
this Commitment card beside it. A blank space on the Reserve may hold a wild animal,
tree, fruit, fruit bat, or goat without another token of that type already
being present on the card. Families still require houses. Normal rules for
placing fruit on trees continue to apply, but fruit may also occupy a blank
Reserve space by itself.

**Restriction:** You may not voluntarily spend or move any token from the
Reserve. In particular, fruit bats on the Reserve cannot be selected for a
fruit bat action. Pollution and other mandatory effects can still remove its
tokens.

**Intended route:** Gain one exceptionally flexible habitat while accepting
that everything placed there is committed to conservation rather than feeding,
building, or the fruit bat action.

## Initial Balance Questions

The first tests must answer:

1. Does each Commitment change at least three meaningful decisions over seven
   rounds?
2. Does the restriction matter in ordinary play, or can the player ignore it?
3. Does the benefit produce more value than the restriction costs?
4. Can the Commitment generate a compounding advantage that becomes impossible to
   contest through worker placement?
5. Does the Commitment still permit a credible base-game score?
6. Does any Commitment reinforce the trained-family, gold, and fruit-bat default
   without opening a genuinely different route?

## Synthetic Terrain Model

Automated prototype tests may use generated Terrain-card records with the
normal eight-space structure. A generated card records:

- a unique synthetic ID;
- one of several habitat archetypes;
- eight printed spaces;
- zero or more nature icons;
- a provisional printed VP value.

Synthetic cards must be clearly labeled and must not reproduce official card
names, artwork, layouts, or the exact commercial deck. Results from this model
are suitable for legality, capacity-pressure, and extreme-value testing only.
They are not evidence that a Commitment is balanced against Atiwa's actual Terrain
distribution.

Exact-deck balance testing requires a separately supplied transcription of all
36 official Terrain cards.

## Gates Before Expanding the Set

Do not design the remaining Commitments until:

- all five Commitments have executable rules tests;
- synthetic Terrain generation is deterministic from a recorded seed;
- upper-bound tests show no Commitment creates unlimited or action-multiplying value;
- at least one human game has been recorded for each Commitment;
- the five restrictions have been observed to affect actual decisions.

## First Synthetic Findings

The initial bounded checks are not balance results, but they identify the
first pressure points for human testing:

- Wildlife Warden can provide at most seven bonus fruit over seven rounds, but
  actual output is also limited by wildlife production, the eight-fruit supply,
  tree placement, and the inability to feed with wild animals.
- Pastoral Cooperative gains one additional recurring food-demand reduction
  per goat. The restriction matters only in games where goats would otherwise
  be sacrificed, so this Commitment may be too efficient for players who
  already preserve goats. It fails the benchmark if it merely improves the
  ordinary goat strategy without creating a consequential tradeoff.
- Distributed Settlement Planner saves only one gold per Location while the
  two-family cap can require several additional Location purchases. The
  benefit may be too small; test a one-tree discount only if the gold version
  consistently traps its player. Its broad-settlement concept is sound, but
  the enabling benefit must support the extra Location actions and costs.
- Bat Conservationist saves one bat on the first fruit bat action of each
  round, at most seven bat movements over the game. Its main value is earlier
  access to the action, not token production. Because efficient base-game play
  already tends to preserve bats, both its benefit and restriction may support
  the normal bat engine instead of opening a different route.
- Forest Reserve Keeper affects exactly one Terrain card. Its value depends
  heavily on the number of blank spaces in the actual Terrain deck, which is
  not available in the current references. It is the strongest current example
  of the benchmark because it changes capacity, sequencing, and resource
  liquidity at the same time.
