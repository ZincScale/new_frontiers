# Living Landscape: Open Commitments Race

## Design Contract

- **Status:** Experimental rules design; not yet implemented or playtested
- **Version:** 0.3-draft
- **Base game required:** *Atiwa*
- **Players:** 1-4
- **Scope:** Public achievements with declining rewards for first, second, and
  third claimants

This document defines the next *Living Landscape* experiment. It does not
overwrite the v0.1 scoring-only design or the v0.2 benefit-plus-constraint
prototype. Test Open Commitments by themselves before deciding whether they
replace either earlier module.

The experiment tests one proposition:

> Public goals with a declining reward can stretch players into different
> Atiwa playstyles while also creating interaction through visible races for
> Terrain cards, worker spaces, and claim order.

An Open Commitment is not assigned to one player. Every revealed Commitment is
available to everyone. Players may pursue the same goal, watch one another's
progress, accelerate their own plans, block access to useful actions, or pivot
when the best reward has already been claimed.

## Design Benchmarks

### Atiwa

Atiwa's wildlife, trees, fruit, fruit bats, families, feeding, pollution, and
tableau capacity form a tightly connected engine. Different tactical openings
can still converge on the same trained-family and fruit-bat plan.

Open Commitments must redirect that engine rather than merely reward its normal
output. Their purpose is to make players value different Terrain cards,
Location cards, token arrangements, and worker actions in different games.

### Fields of Arle and Black Forest

*Fields of Arle* creates strategic variety through a broad public sandbox.
*Black Forest* creates different engines through public buildings, spatial
development, conversion timing, and competition over access. Living Landscape
should borrow their setup-responsive divergence without adding their subsystem
weight to Atiwa.

### Tea Garden: Puerh

The Imperial Decree race in *Tea Garden: Puerh* is the direct interaction
benchmark: public achievements remain available to multiple players, but the
reward declines with claim order. Living Landscape uses that race structure as
inspiration without reproducing any commercial card text, artwork, graphic
design, or component layout.

## Main Design Goals

Open Commitments must:

1. Stretch players toward materially different Atiwa playstyles.
2. Create visible races and additional player interaction without direct
   resource theft or take-that effects.
3. Change what players acquire, when they act, and how they arrange their
   tableau.
4. Make contested Terrain cards and worker spaces matter differently from game
   to game.
5. Reward an unusual but viable route rather than incidental progress along
   Atiwa's normal efficient engine.
6. Preserve the seven rounds, three workers, normal maintenance sequence,
   pollution rules, feeding, breeding, and fruit bat action.
7. Require only cards and simple claim markers or a claim sheet.
8. Work at all player counts, including a solo timing race.
9. Preserve Atiwa's environmental message. No Commitment may remove pollution
   or turn pollution into a profitable resource engine.

The desired result is not merely a different final score. A successful
Commitment causes a player to take several actions, select cards, preserve or
spend resources, or arrange their tableau differently than they normally
would.

## Components

The complete target module contains:

- at least 8 double-sided or single-sided Open Commitment cards;
- 2 small claim markers per player, enforcing a maximum of 2 claims per player,
  or a reusable claim sheet that records
  player color and claim order;
- 1 reference card explaining claim timing and player-count scaling.

For a paper prototype, write player initials and the round number in the rank
boxes on a separate claim sheet. Do not remove workers, families, or other
functional pieces from a player's normal supply to mark claims.

## Setup

After completing normal Atiwa setup, including revealing the initial Terrain
cards and placing the action space tiles:

1. Shuffle the Open Commitment deck.
2. Reveal a number of Open Commitments equal to the number of players plus 1
   face up beside the action board.
3. Return the remaining cards to the box without looking at them.
4. Place or display the available claim rewards for the player count.

Use this many Open Commitments:

```text
Players              1   2   3   4
Open Commitments     2   3   4   5
```

All revealed Open Commitments remain visible for the entire game. The extra
goal gives players somewhere to pivot after losing a race and keeps one more
strategic lane available than there are players. There is no private deal,
draft, or ownership decision during setup.

## Claim Rewards

The first prototype uses this provisional reward ladder:

```text
Claim order     3-4 players     2 players
First                7 VP          7 VP
Second               4 VP          —
Third                2 VP          2 VP
Fourth               0 VP          n/a
```

In a two-player game, cover or ignore the middle reward before play. The first
claimant receives the maximum reward, and the second claimant receives the
third-place reward. This keeps the race meaningful instead of guaranteeing
both players a substantial award.

In a four-player game, the fourth player cannot score that Open Commitment.
Once all three scoring ranks have been claimed, the race on that card is over.

The `7/4/2` values are tuning numbers, not final balance. The size of the gaps
must be large enough to make claim order matter but small enough that abandoning
Atiwa's base economy for an early claim is not automatically correct.

## Claim Timing

After completing a worker action and any optional fruit bat action, check all
revealed Open Commitments.

If the active player satisfies an unclaimed rank on an Open Commitment:

1. They announce the claim.
2. They place or record their player marker in the highest available scoring
   rank on that card.
3. They immediately record the printed VP award.

A player may claim each revealed Open Commitment at most once and may claim no
more than 2 Open Commitments during the game. When a player makes their second
claim, return their remaining claim marker or mark them as ineligible for
further claims. At the provisional values, this caps a player's Open Commitment
score at 14 VP.

A player may claim multiple revealed Commitments after one turn if they satisfy
them and still have enough unused claim markers. If more races are available
than they can claim, they choose which claims to take. Card design should avoid
letting one ordinary action incidentally complete multiple races.

A claim is permanent. The player does not need to maintain the claimed
condition until the end of the game unless the card explicitly says otherwise.
Conditions involving resources that can later be spent must be written so that
reaching and then liquidating the threshold is either an intentional strategic
choice or is prevented by the condition.

### Avoiding Simultaneous Claims

Atiwa's maintenance steps are largely simultaneous. The first prototype must
therefore use conditions tied to an identifiable player turn or voluntary
action, such as acquiring a card, placing a token, taking a fruit bat action,
or completing a particular tableau arrangement during an action.

Do not use a condition that several players can satisfy simultaneously during
automatic maintenance unless that card also provides an explicit and fair
tie rule. Avoiding simultaneous triggers is preferable to adding a general
tie-resolution procedure.

## Solo Rules

In solo play, the player-count-plus-one rule reveals 2 Open Commitments. Claim
order becomes a race against the seven-round clock:

```text
Claimed by the end of     Award
Round III                  7 VP
Round V                    4 VP
Round VII                  2 VP
```

Resolve claims after the player's turns as normal. Record the round in which
each Commitment was claimed.

The `III/V/VII` deadlines are provisional. Every Open Commitment must be
capable of earning the first reward through a deliberate but credible opening.
If a goal cannot reasonably be reached by round III, revise the goal rather
than silently giving it an easier race. Card-specific timing exceptions should
be used only if later playtests show that a common clock cannot support varied
goal types.

Solo Open Commitments are successful only if they redirect worker placement
despite Atiwa's normal multi-round worker blocking. They should not become free
points for following the standard solo engine.

## Card Design Requirements

Each Open Commitment should record:

- an ID and title;
- one observable claim condition;
- the `7/4/2` claim ladder;
- the intended alternative playstyle;
- the public cards or worker actions likely to become more contested;
- a note identifying how the condition differs from ordinary efficient Atiwa
  play;
- any solo timing concern discovered in testing.

A candidate card passes initial review only if:

1. Its progress is visible to opponents.
2. At least two players can credibly race for it from the revealed setup.
3. Pursuing it changes at least three meaningful decisions over the game.
4. It creates pressure on at least one shared action or face-up Terrain card.
5. It asks for more than simple accumulation of trained families, gold, fruit
   bats, or another normal high-value resource.
6. A player who loses first place has a real choice between accepting the
   smaller reward, pivoting to another revealed Commitment, or returning to
   their base engine.
7. The condition can be verified without hidden information or subjective
   judgment.
8. The condition does not prescribe an entire turn-by-turn script.

## Intended Playstyle Space

The full set should cover different ways of solving Atiwa's feeding, capacity,
and ecological puzzle. Candidate lanes include:

- wildlife preservation and orchard development;
- long-term goat husbandry rather than emergency consumption;
- distributed settlements across several Locations;
- dense or unusually arranged habitats;
- protected resources that sacrifice liquidity for capacity or scoring;
- low-pollution development with constrained access to mining income;
- Terrain-focused expansion rather than Location concentration;
- alternative family-training and fruit-bat timing.

These are design lanes, not card text. A card should be rejected if it merely
names one of these themes while ordinary efficient play completes it anyway.

## Relationship to Earlier Experiments

Test v0.3 independently:

- Do not use the v0.1 Landscape Priorities in the same game.
- Do not use the v0.1 private scoring Commitments.
- Do not use the v0.2 benefit-plus-constraint personal Commitments.

The earlier experiments remain useful controls:

- v0.1 tests whether scoring incentives alone change play;
- v0.2 tests whether a personal benefit and mandatory restriction create a
  distinct engine;
- v0.3 tests whether an open, declining-reward race creates both strategic
  divergence and player interaction.

Only combine modules after one of them independently demonstrates that players
make decisions they would not normally make.

## First Playtest Questions

1. Did each Open Commitment cause players to pursue a recognizably different
   playstyle?
2. Did players monitor and react to their opponents' progress?
3. Did claim order change worker placement or Terrain acquisition?
4. Did the second- and third-place rewards still produce interesting choices?
5. Was the first reward worth racing for without becoming mandatory?
6. Did the two-player `7/2` split create tension or merely punish the second
   player?
7. Did starting player order decide a race too often?
8. Could a player claim through temporary stockpiling and then erase the
   intended commitment immediately?
9. Did the player-count-plus-one display encourage different lanes, or did the
   same engine progress toward several of the revealed cards?
10. In solo, did the round deadlines redirect the opening and interact with
    blocked worker spaces?
11. Did revealing player count plus 1 goals provide useful pivot options, or
    did the larger display dilute the races?
12. Did the 2-claim limit create meaningful specialization without making a
    player's remaining progress feel irrelevant?

## Gates Before Card Production

Do not create final card graphics or a full printable set until:

- at least 8 distinct playstyle lanes have been outlined;
- every proposed claim has an action-timed, objectively verifiable trigger;
- overlapping goals have been identified and removed or intentionally paired;
- the `7/4/2` ladder has been tested at two and three or four players;
- at least 5 solo tests have checked the `III/V/VII` clock;
- no goal rewards unavoidable progress along the default Atiwa engine;
- the design has been checked against the official Terrain distribution once
  the 36-card transcription is available.

The decisive playtest question remains:

> Did this Open Commitment stretch you into a way of playing Atiwa that you
> would not otherwise have chosen?
