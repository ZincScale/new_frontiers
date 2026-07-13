# Project Notes

The active design/code work is the main Roll for the Galaxy minimal no-roll
variant:

- rules: `docs/roll_phase_battery_rules.md`
- print-and-play reference: `pnp/roll-phase-battery.html`
- simulator: `phase_battery/`

Avoid changing or reasoning from these older/parked variants unless the user
explicitly asks for them:

- `roll_mancala/`
- `docs/roll_mancala_dice_design.md`
- `pnp/roll-mancala.html`
- `roll_galaxy/`

Current main-rules direction:

- Goal: stay close to base Roll for the Galaxy, but remove player dice rolling
  swing.
- Secret phase selection is back. In solo, the player selects two eligible
  phases; in all multiplayer games, including 2p, each player selects one
  eligible phase. A phase is
  eligible only if the player has at least one ready pip for that phase.
  Selected phases resolve in normal order. Phase selection itself does not
  consume pips; pips are workers spent only when the selected phase resolves.
- Unselected phases do not occur.
- VP chip pool is back. Current playtest tuning uses 7 VP chips per player and
  starting colored tracks at 3/3.
- There is no White track because the tile set has no White die grants. Red is
  the single Settle track: every World spends Red pips equal to its cost and
  may store progress. Roll has no Military World type; gray, Rebel, and
  Red-grant Worlds use the same construction rule. Credits are unlimited chips
  like base Roll, stored as a scalar count.
- Preserve printed die location: Cup gains increase max and free-recharge at
  Manage Empire (starting Cup gains begin ready), Citizenry gains increase max
  only, and World gains increase max only plus place a Good. Reassign powers
  temporarily spend a source-color pip as a worker in their printed destination
  without changing either track's max. The simulator generically allows one
  any-source route per non-goal reassign Development because its retained tile
  data lacks the spreadsheet's detailed source/destination restrictions. A
  routed Produce or Ship pip performs the ordinary destination action; its
  source color does not alter the Good, Trade value, or Consume value.
- Produce spends Green pips one at a time. Each Green pip places one Good marker
  on a chosen empty non-gray World; each World holds at most one Good unless a
  tile power says otherwise. Keep this basic action separate from Reassign and
  from the later Ship resolution.
- Ship can Trade for Credits or Consume for VP chips. Current simulator
  heuristic trades when Credits are low, then consumes. Trade value comes only
  from the World color: Blue 3, Brown 4, Green 5, Yellow 6. Consume is a fixed
  1 VP chip with no Good-color or Shipper-color matching bonuses.
- Solo uses the same low-player selected-phase model: the player selects two
  eligible phases, Dummy phase cards add selected phases and resolve their
  Dummy effects, and only selected phases occur. Current solo cap is 15 rounds
  with a 24-chip VP pool: 12 for the player and 12 for the Dummy seat.
- Construction cards are parallel, not top-only. Developments can store pip
  progress from Brown or eligible Yellow. Multiple Developments can complete in
  one Develop phase. Multiple Worlds can complete in one Settle phase. Explore
  pips inspect one more tile than the number spent; Develop pips develop;
  Produce pips produce Goods on planets; Ship pips ship Goods.
- Scout spends N Blue to inspect N+1 candidates of one type and keep one. As a
  separate Explore action, spend 1 Blue to take another six-cost Development
  goal; before commitment it is another candidate, afterward it is another
  committed goal.
- Choose six-cost goal candidates before setup tiles. Reveal player count + 2
  Faction tiles and the same number of Home Worlds, then draft one of each in
  reverse turn order so players can build a synergistic starting tableau.
- After the starting-tile draft and its printed gains, each player specializes
  in Blue Explore or Brown Develop: increase that track's max and current by 1.
  This is a ready starting pip. Solo Industrial thresholds have not yet been
  retuned for this +1 starting max.
- Remove six-cost Developments from the normal bag. They are now endgame-goal
  candidates: reveal/set aside 2 + player count six-cost Developments, each
  player chooses 2, then after half the VP chips are gone or someone has 6
  completed Developments/Worlds, each player chooses one of their two as their
  endgame goal. The other returns to the Development market row, or its reverse
  side can be used as a World. Explore may optionally take another six-cost
  Development goal. A player loses 6 VP per chosen Development goal whose
  conditions are not fulfilled. In solo, each six-cost goal is tied to a named
  solo condition: Free Trade Association = Novelty; Galactic Bankers =
  Satisfied Populace; Galactic Exchange = Alien Contact; Galactic Federation =
  Developer; Galactic Renaissance = Builder; Galactic Reserves = Industrial;
  Mining League = Rare Elements; New Economy = Production; New Galactic Order =
  Military; System Diversification = Diverse. To mark one of those solo
  campaign conditions, the player must score the named VP threshold, commit the
  matching six-cost goal, and fulfill that goal's requirement. In campaign
  play, select the six-cost goal to match the condition being attempted; random
  goal availability is not a difficulty gate. Production currently requires 3
  production Worlds. Still clarify whether multiple players may choose the same
  goal from the `2 + player count` pool.
- Retuned solo thresholds for fixed 1-VP Consume are: Easy
  Great/Triumphant/Epic/Named 22/26/30/24, Normal 32/36/40/32, Advanced
  38/42/46/38, and Very Hard 44/48/52/44. Industrial max-pip targets remain
  17/19/21/23.
- Parked larger-expansion ideas: all phases every round, no VP pool, Ship as
  Credits only, and special Development-completion Credit rewards.

Adjacent design context, not part of the active Phase Battery rules:

- A July 2026 playtest found Phase Battery too resource-rich, too permissive,
  too multiplayer-solitaire, and poor at circulating Explore tiles. An
  explicitly reopened experimental alternative lives in
  `roll_mancala/roll_and_sow.py` with its runner in
  `roll_mancala/simulate_roll_and_sow.py`. Its table rules are
  `docs/roll_and_sow_rules.md` and its printable boards are
  `pnp/roll-and-sow.html`. It starts with 5 White dice: roll 3
  into face-matching phase bowls and put 2 in Citizenry. Secretly select a
  nonempty bowl; every selected phase activates that bowl for every player.
  Use dice first, then sow all unused dice clockwise. Cup gains roll into a
  bowl immediately; Citizenry dice cost 1 Credit to recruit and roll. Explore
  sees 4 candidates with the first die and +1 per extra die, using a discard
  cycle for rejected tiles. Manage Empire retains Recall from base Roll; when
  all five bowls are empty, recalling one construction/Good die and rolling it
  into a bowl is mandatory to prevent lockout. This is an experiment, not yet the adopted main
  ruleset. The experiment now converts applicable persistent powers and exact
  Reassign restrictions from `Roll_for_the_Galaxy_all_tiles.xls`. Six-cost
  Developments use a shared `2 + player count` candidate pool, commit at half
  the VP pool or 6 completed tiles, score converted printed end-game bonuses,
  and suffer -6 VP when their minimum is missed. Multiple players may mark the
  same shared candidate in this experiment. Galactic Reserves uses a provisional
  10-owned-dice Industrial minimum; a 1,000-game 4p sensitivity run raised its
  fulfillment from about 33% at 12 dice to about 75% at 10 dice. Goal cards
  grant no phase power, face VP, or tableau square. Advanced Logistics and Improved
  Reconnaissance are inert under the parallel-construction abstraction, and
  Backup Planning still uses a generic one-route approximation because Dictate
  is not separately modeled. The design supports 1-4 players maximum; solo
  phase support is still provisional. With goals enabled, 200-game automated
  samples after adding mandatory anti-lockout Recall averaged 19.8 rounds at
  solo (180/200 reached the round cap), 23.3 at 2p, 22.0 at 3p, and 18.7 at 4p.
  A separate 1,000-game 4p goal audit found Galactic Bankers/Federation
  generally safe and positive, while New Galactic Order, System
  Diversification, and Galactic Renaissance had materially higher failure
  rates. These are AI pacing and risk signals, not human balance validation.
- `New_Frontiers_Tile_List_ver_1_2.xlsx` and `New_frontiers_rules.pdf` are local
  untracked reference files. The workbook lists 40 unique Development entries,
  60 Worlds, and 16 starting-colony faces. New Frontiers has 56 physical
  Development tiles because some designs have multiple copies. Roll has 55
  non-start Development designs, but this variant removes 10 six-cost goals
  from the normal bag, leaving 45 ordinary Development designs.
- A candidate New Frontiers / Starry Rift military balance rule is an
  **Occupation Cost**: to conquer a Military World, meet its Military strength,
  place its printed colonists, and pay 1 Credit per colonist placed.
  Specialized Rebel/Xeno/Uplift/Alien Military helps meet strength but never
  reduces this recurring cost. Apply the same cost to Xeno Worlds; do not add
  extra colonists because the shared colonist supply is also an end timer,
  especially in solo. If tuning is needed, test a flat 1 Credit when too harsh
  or `colonists + 1` Credits when too weak. This proposal has not been adopted
  into any ruleset.
- Literal Wingspan-style row-running is currently rejected for Roll: its tiles
  mainly grant immediate effects, passive modifiers, Goods storage, or scoring,
  so repeatedly "running" a World or tile has no native meaning and would
  require rewriting the tile set. Wingspan-like spatial organization may still
  be useful as a phase-power index plus a separately organized galaxy, but it
  should not activate completed tiles as a chain in the minimal variant.

When preserving context for future sessions, prefer updating this file with
short durable project assumptions rather than relying on chat history.
