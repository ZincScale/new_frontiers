# Atiwa Component Transcription Requirements

## Purpose

This document records the official component information needed to design and
test the *Living Landscape* Open Commitments against Atiwa's actual action
competition, card availability, and tableau constraints.

The work has two stages:

1. Transcribe the worker-placement system so the first Open Commitments can be
   designed around real contested actions.
2. Transcribe the Terrain and Location decks so those Commitments can be
   checked for attainability, strategic variety, and comparable difficulty.

The official rulebook explains the action vocabulary, combined-action rules,
and general setup. It also contains a useful four-player setup illustration.
It does not provide a dependable text inventory of every printed action space,
especially the 1-2 player side of the extension board. Component images or a
separate transcription are therefore required for an exact model.

## Acceptable Source Material

The source does not need to be a written description. Clear, straight-on
photos or scans are sufficient; the component data can be transcribed from
them.

For every image:

- show the entire component without cropped edges;
- keep icons, numbers, arrows, and player-count markings readable;
- photograph cards and tiles upright;
- avoid glare, shadows, and pieces covering printed information;
- provide a closer image when a symbol is ambiguous;
- identify the front and back of double-sided components.

Use `?` and add a note rather than guessing any unclear symbol.

## Stage 1: Worker-Placement System

Stage 1 is the minimum input needed to draft Open Commitments around genuine
worker-space competition.

### Base Action Board

Record the complete base action-board layout, including:

- every fixed worker-placement space;
- the actions printed underneath round spaces I-VII;
- the empty round I position;
- the positions occupied by the six shifting action-space tiles during setup;
- every Terrain-card acquisition space and the display position associated
  with it;
- every Location-card acquisition space and the Location stack associated
  with it;
- all printed costs, quantities, choices, multipliers, bonuses, arrows, and
  grouping marks;
- any restriction that depends on two spaces being paired or adjacent.

Preserve the physical ordering of spaces. Left-to-right and top-to-bottom
position can matter for understanding which cards, underlying actions, or
paired restrictions apply.

### Action Board Extensions

Record all three player-count configurations:

- the shared 1-2 player back side;
- the 3-player front side;
- the 4-player front side.

For each extension, record every worker-placement space and its exact:

- action or combination of actions;
- token quantities;
- gold or tree cost;
- nature-icon multiplier;
- four-Terrain-card bonus, if present;
- associated Terrain or Location card;
- pairing, arrow, or same-player restriction.

Do not infer the 1-2 player side from the 3- or 4-player layouts.

### Six Action-Space Tiles

Record all six action-space tiles separately. Assign temporary IDs `AT01`
through `AT06` unless the components provide identifiers.

For each tile, record:

- every printed action and quantity;
- any choice, cost, multiplier, or prerequisite;
- its upright orientation;
- whether it has a distinct reverse side.

The transcription must keep the tile action separate from the underlying
round action. During play, a covered round space provides both the action on
the tile and the action printed beneath it; those combinations shift as the
tiles move.

### Suggested Action-Space Format

The worker spaces can be supplied as images or in a table using fields such as:

```csv
source,player_count,space_id,position,printed_actions,associated_card,cost,restriction,notes
```

Where:

- `source` is `base`, `extension`, or `action_tile`;
- `player_count` is `all`, `1-2`, `3`, or `4`;
- `position` preserves the physical order or row and column;
- `printed_actions` lists actions in the order shown without combining an
  action tile with its current underlying action.

## Stage 2: Terrain Cards

An exact-deck model requires all 36 official Terrain cards. The rulebook states
that they are all different, so each physical card must be recorded.

Preserve:

- card ID or a temporary ID;
- name;
- copy count;
- printed VP;
- nature icons;
- upright orientation;
- the exact contents of all eight tableau spaces;
- special or combined spaces;
- any unusual printed rule.

Use one CSV row per distinct card:

```csv
id,name,copies,printed_vp,nature_icons,top_middle,top_right,middle_left,middle_center,middle_right,bottom_left,bottom_center,bottom_right,notes
```

Use these provisional space codes:

```text
B      blank
X      blocked/non-space
W      wild animal
T      tree
F      fruit
BAT    fruit bat
G      goat
H      normal house
HU     uninhabitable house
T+W    tree that can hold a wild animal
T+BAT  tree that can hold a fruit bat
```

Add a new documented code if an official card contains another distinct space
type. Preserve exact position because pollution fills spaces in positional
order.

## Stage 2: Location Cards

Record each unique Location-card face and its physical copy count. It is not
necessary to photograph or enter every physical copy when all copies of that
face are identical.

The base game contains four named Location stacks:

- Farmstead;
- Settlement;
- Village;
- Town.

For every unique face, record:

- card ID or a temporary ID;
- Location name;
- copy count;
- printed VP;
- upright orientation;
- all eight tableau spaces in their exact positions;
- every house, token, blank, blocked, or special space;
- any unusual printed rule or mark.

Use the same positional fields and space codes as the Terrain transcription
where possible:

```csv
id,name,copies,printed_vp,top_middle,top_right,middle_left,middle_center,middle_right,bottom_left,bottom_center,bottom_right,notes
```

Location acquisition costs belong in the action-board transcription, not in a
card record, unless a particular card itself changes or prints a cost.

## Rules and Symbol Clarifications

Alongside the component images, record any symbol or physical relationship
that remains unclear after consulting the official rules. In particular,
identify:

- whether apparently identical card faces are truly identical;
- whether any action-space tile or extension is double-sided;
- how a printed arrow or bracket groups action spaces;
- whether a symbol is a cost, prerequisite, reward, choice, or bonus;
- any component-specific exception not stated in the main rules text.

## Delivery Order

The material can be supplied incrementally:

1. Base action board.
2. The 1-2, 3-player, and 4-player extension layouts.
3. All six action-space tiles.
4. All 36 Terrain cards.
5. Each unique Location face with its copy count.
6. Close-ups or written clarification for ambiguous symbols.

The first three items are enough to begin drafting the Open Commitment set.
The Terrain and Location listings are required before treating attainability
or balance results as representative of the actual game.

## Validation Before Use

Before replacing synthetic data or drawing balance conclusions, verify:

- all worker spaces are present for each player count;
- all six action-space tiles are distinct and correctly oriented;
- tile actions and underlying round actions are stored separately;
- the Terrain transcription totals 36 physical cards;
- the Location copy counts match the physical stacks;
- every card has exactly eight recorded tableau positions;
- all symbols use known codes or carry an explicit clarification note;
- no unclear icon, number, or spatial relationship has been guessed.

Until this validation is complete, the existing synthetic Terrain model is
suitable only for legality, capacity, and extreme-value checks—not exact Atiwa
balance testing.
