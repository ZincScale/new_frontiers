# New Frontiers-Style Strategy Prototype

This repository contains a small simulation engine for a New Frontiers-inspired
board game prototype. It uses Race for the Galaxy concepts as ancestry, but it
models board-game components: a Race for the Galaxy-template catalog of
36 public development tiles and 60 world tiles, explored worlds, colonists,
credits, goods, VP chips, priority, and action selection.

The current focus is balance exploration, especially a modified military model
where conquest is strong but no longer free:

- Military worlds still require enough military strength.
- Military worlds still require colonists.
- Defense 2-3 worlds cost 1 credit in logistics.
- Defense 4-5 worlds cost 2 credits in logistics.
- Defense 6+ worlds cost 3 credits in logistics.

Run a sample simulation:

```bash
python3 -m nf_engine.simulate --games 20 --players balanced military economy builder
```

The engine is intentionally compact and incomplete as a product, but complete
enough to run automated AI-vs-AI games and compare broad strategy incentives.

