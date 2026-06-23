# New Frontiers-Style Strategy Prototype

This repository contains a small simulation engine for a New Frontiers-inspired
board game prototype. It uses Race for the Galaxy concepts as ancestry, but it
models board-game components: a Race for the Galaxy-template catalog of
50 public development tiles and 82 world tiles, explored worlds, colonists,
credits, goods, VP chips, priority, capped development discounts, a 10-space development display, and action selection.

The current focus is balance exploration, especially a modified military model
where conquest is strong but no longer free:

- Military worlds still require enough military strength.
- Military worlds still require colonists.
- Excess military strength reduces logistics costs: every 2 military above the target defense reduces logistics by 1 credit.
- Defense 2-3 worlds cost 1 credit in logistics before overmatch discounts.
- Defense 4-5 worlds cost 2 credits in logistics before overmatch discounts.
- Defense 6+ worlds cost 3 credits in logistics before overmatch discounts.

Run a sample simulation:

```bash
python3 -m nf_engine.simulate --games 20 --players balanced military economy builder
```

Run the simpler physical-table house rule instead:

```bash
python3 -m nf_engine.simulate --games 20 --no-military-logistics --military-defense-bonus 1 --players balanced military economy builder
```

The engine is intentionally compact and incomplete as a product, but complete
enough to run automated AI-vs-AI games and compare broad strategy incentives.
