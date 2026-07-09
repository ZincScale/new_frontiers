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
- Secret phase selection is back. In solo and 2p, each player selects two
  eligible phases; at 3p+, each player selects one eligible phase. A phase is
  eligible only if the player has at least one ready pip for that phase.
  Selected phases resolve in normal order. Phase selection itself does not
  consume pips; pips are workers spent only when the selected phase resolves.
- Unselected phases do not occur.
- VP chip pool is back. Current playtest tuning uses 7 VP chips per player and
  starting colored tracks at 3/3.
- White dice/tracks are back as the Settle track for non-Military Worlds. Use
  White pips as Settle workers for non-red Worlds. Credits are unlimited chips
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
  pips dig that many tiles from the bag; Develop pips develop; Produce pips
  produce Goods on planets; Ship pips ship Goods.
- Red pips are Military value/readiness. Settling a Military World uses Red as
  the Military value and exhausts 1 Red pip after the settle.
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
- Current playtest read: this is intentionally a soft brake. If Military still
  runs away, the next tuning knob is Red-grant Military Worlds increasing Red
  max only, with current Red gained later through recharge.
- Parked larger-expansion ideas: all phases every round, no VP pool, Ship as
  Credits only, and special Development-completion Credit rewards.

When preserving context for future sessions, prefer updating this file with
short durable project assumptions rather than relying on chat history.
