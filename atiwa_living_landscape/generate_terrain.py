"""Emit synthetic Terrain cards as JSON or a printable HTML document."""

from __future__ import annotations

import argparse
import html
import json

from atiwa_living_landscape.terrain import TerrainCard, generate_terrain_deck


def card_record(card: TerrainCard) -> dict[str, object]:
    return {
        "id": card.synthetic_id,
        "archetype": card.archetype,
        "spaces": [space.value for space in card.spaces],
        "nature_icons": card.nature_icons,
        "printed_vp": card.printed_vp,
    }


def render_json(cards: tuple[TerrainCard, ...]) -> str:
    return json.dumps([card_record(card) for card in cards], indent=2)


def render_html(cards: tuple[TerrainCard, ...]) -> str:
    rendered_cards = []
    for card in cards:
        cells = [
            (
                '<div class="identity">'
                f"<strong>{html.escape(card.synthetic_id)}</strong>"
                f"<span>{html.escape(card.archetype)}</span>"
                f"<span>{card.nature_icons} nature / {card.printed_vp} VP</span>"
                "</div>"
            )
        ]
        cells.extend(
            f'<div class="space {space.value}">{space.value.replace("_", " ")}</div>'
            for space in card.spaces
        )
        rendered_cards.append('<section class="card">' + "".join(cells) + "</section>")

    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Living Landscape synthetic Terrain</title>
<style>
  :root { font-family: system-ui, sans-serif; color: #172218; }
  body { margin: 12mm; background: #f5f1e7; }
  .notice { max-width: 70rem; margin: 0 auto 8mm; }
  .deck { display: grid; grid-template-columns: repeat(3, 63mm); gap: 4mm; justify-content: center; }
  .card { width: 63mm; height: 63mm; display: grid; grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(3, 1fr); border: 0.5mm solid #263d2b; border-radius: 2mm;
    overflow: hidden; background: #fff; break-inside: avoid; }
  .card > div { border: 0.15mm solid #9aa992; display: flex; align-items: center;
    justify-content: center; padding: 1.2mm; text-align: center; font-size: 8pt; }
  .identity { flex-direction: column; background: #dbe7d5; }
  .identity span { display: block; font-size: 6.5pt; }
  .blank { background: #fffdf4; }
  .blocked { background: #555; color: #fff; }
  .tree { background: #d7ead0; }
  .wild_animal { background: #ead8bb; }
  .fruit { background: #f0d8b3; }
  .fruit_bat { background: #ddd5e9; }
  .goat { background: #eee8d8; }
  .house { background: #ead0c2; }
  @page { size: A4 portrait; margin: 10mm; }
  @media print { body { margin: 0; background: #fff; } .notice { display: none; } }
</style>
</head>
<body>
<div class="notice">
  <h1>Living Landscape synthetic Terrain</h1>
  <p>Testing geometry only. These cards do not reproduce Atiwa's commercial Terrain deck.</p>
</div>
<main class="deck">
""" + "\n".join(rendered_cards) + """
</main>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260722)
    parser.add_argument("--size", type=int, default=36)
    parser.add_argument("--format", choices=("json", "html"), default="json")
    args = parser.parse_args()

    cards = generate_terrain_deck(seed=args.seed, size=args.size)
    print(render_html(cards) if args.format == "html" else render_json(cards))


if __name__ == "__main__":
    main()
