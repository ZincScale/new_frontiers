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
  Selected phases resolve in normal order.
- Unselected phases do not occur.
- VP chip pool is back. Scoring is tableau VP + VP chips + converted 6-cost
  Development bonuses. Current playtest tuning uses 7 VP chips per player and
  starting colored tracks at 3/3.
- White dice/tracks are unused in the active minimal no-roll variant. Credits
  are unlimited chips like base Roll, stored as a scalar count.
- Ship can Trade for Credits or Consume for VP chips. Current simulator
  heuristic trades when Credits are low, then consumes.
- Solo uses the same low-player selected-phase model: the player selects two
  eligible phases, Dummy phase cards add selected phases and resolve their
  Dummy effects, and only selected phases occur. Current solo cap is 15 rounds
  with a 24-chip VP pool: 12 for the player and 12 for the Dummy seat.
- Construction cards are parallel, not top-only. Developments can store pip
  progress from Brown or eligible Yellow. Credits are spent on Develop only when
  they complete the card. Multiple Developments can complete in one Develop
  phase. Multiple Worlds can complete in one Settle phase, but each World is
  still paid in one shot.
- Red max is persistent Military level. Current Red is Military readiness:
  settling a Military World requires Red max at least equal to cost and exhausts
  1 current Red. Red current can be recharged with Credits.
- Current playtest read: this is intentionally a soft brake. If Military still
  runs away, the next tuning knob is Red-grant Military Worlds increasing Red
  max only, with current Red gained later through recharge.
- Parked larger-expansion ideas: all phases every round, no VP pool, Ship as
  Credits only, and special Development-completion Credit rewards.

When preserving context for future sessions, prefer updating this file with
short durable project assumptions rather than relying on chat history.
