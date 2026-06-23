# Modified Rules Draft

This prototype is based on New Frontiers-style mechanisms, with changes aimed
at making military play powerful but not sacrifice-free.

## Components

- Public development tiles:
  - The prototype currently has 50 public developments based on Race for the
    Galaxy, New Frontiers, and Starry-Skies-style archetypes.
  - Small developments have fixed costs, fixed VP, and ongoing powers.
  - Large 9-cost developments are the board-game analogue of Race for the
    Galaxy 6-cost developments. They carry variable endgame scoring.
  - Public development tiles are unique once bought, each player is capped
    at 10 development spaces, and stacked development discounts are capped at
    1 plus the Develop selector bonus.
- World tiles:
  - The prototype currently has 82 world tiles spanning gray, production, and
    windfall civilian and military worlds.
  - Worlds are explored from a bag before they can be settled.
  - Settled worlds become colonies.
  - Worlds can be civilian or military.
  - Worlds can be production, windfall, or gray.
- Player resources:
  - Credits are money.
  - Colonists are required to settle worlds.
  - Goods are physical typed resources.
  - VP chips are earned mostly by consume effects.

## Action Structure

Players choose one unchosen action per round in priority order. Every player may
perform the selected action; only the selecting player receives its bonus.

Actions:

- Retreat into Isolation: selector gains credits.
- Develop: players may buy one development; selector gets a discount.
- Explore: players discover world tiles; selector may keep an extra world.
- Settle: players either gain colonists or settle one explored world; selector
  gains a colonist first.
- Produce: production colonies make goods; selector also refills one windfall
  and collects credits stored on the action.
- Trade/Consume: players may sell one good for credits, then must use available
  consume powers while possible; selector gains one VP chip.
- Send Diplomatic Envoys: selector gains VP and moves to first priority.

## Military Rebalance

Military settlement should preserve the feel of conquest without becoming
automatic free expansion.

To settle a military world:

1. The player must have military strength at least equal to the world's defense.
2. The player must spend the world's listed colonist requirement.
3. The player must pay logistics credits:
   - Defense 1: 0 credits.
   - Defense 2-3: 1 credit.
   - Defense 4-5: 2 credits.
   - Defense 6 or more: 3 credits.
   - Every 2 military strength above the world defense reduces this logistics
     cost by 1 credit, to a minimum of 0.

Military and credits do not combine to meet a defense threshold. Credits are only
logistics after the threshold is met; excess military represents force projection
that makes those logistics cheaper.

## Physical-Table Variant

For a physical copy, the lowest-bookkeeping military balance rule is:

- Military worlds require 1 extra military strength to settle.
- Do not use logistics credits with this variant unless the group still finds
  military too efficient.

In the simulator, this is:

```bash
python3 -m nf_engine.simulate --no-military-logistics --military-defense-bonus 1
```

## Strategic Intent

- Civilian worlds spend more credits but should produce stronger economies.
- Military worlds provide tempo and VP, but no longer bypass all costs.
- Military infrastructure reduces conquest costs through overmatch, making
  conquest a payoff for prior investment rather than a free default.
- Temporary or specialized military can remain efficient because it requires a
  timing decision.
- Large development scoring should reward coherent strategies rather than a
  single dominant path.
