"""Run bounded synthetic checks for the Stewardship Commitment prototype."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import json

from atiwa_living_landscape.commitments import (
    Commitment,
    food_demand,
    location_family_limit,
)
from atiwa_living_landscape.terrain import (
    Space,
    Token,
    generate_terrain_deck,
    reserve_blank_accepts,
)


@dataclass(frozen=True)
class SyntheticReport:
    seed: int
    deck_size: int
    sampled_decks: int
    archetypes: dict[str, int]
    spaces: dict[str, int]
    average_blank_spaces: float
    sampled_blank_spaces_per_card: dict[str, float]
    reserve_extra_initial_token_types_per_blank: int
    pastoral_food_demand_reduction_examples: dict[str, int]
    settlement_family_capacity_examples: dict[str, int]
    commitment_round_caps: dict[str, int]


def build_report(seed: int, sampled_decks: int = 1000) -> SyntheticReport:
    if sampled_decks < 1:
        raise ValueError("sampled_decks must be positive")

    deck = generate_terrain_deck(seed=seed)
    archetypes = Counter(card.archetype for card in deck)
    spaces = Counter(space.value for card in deck for space in card.spaces)
    blank_count = spaces[Space.BLANK.value]
    sampled_blank_averages = []
    for offset in range(sampled_decks):
        sampled_deck = generate_terrain_deck(seed=seed + offset)
        sampled_blanks = sum(
            card.spaces.count(Space.BLANK) for card in sampled_deck
        )
        sampled_blank_averages.append(sampled_blanks / len(sampled_deck))

    normally_seeded_types = 0
    reserve_types = sum(reserve_blank_accepts(token) for token in Token)

    pastoral_examples: dict[str, int] = {}
    for families, goats in ((4, 1), (7, 2), (10, 3), (13, 5)):
        normal = food_demand(families=families, goats=goats)
        pastoral = food_demand(
            families=families,
            goats=goats,
            commitment=Commitment.PASTORAL_COOPERATIVE,
        )
        pastoral_examples[f"{families}_families_{goats}_goats"] = normal - pastoral

    settlement_examples = {
        f"{locations}_four_house_locations": locations
        * location_family_limit(
            printed_houses=4,
            commitment=Commitment.DISTRIBUTED_SETTLEMENT_PLANNER,
        )
        for locations in (2, 4, 6)
    }

    return SyntheticReport(
        seed=seed,
        deck_size=len(deck),
        sampled_decks=sampled_decks,
        archetypes=dict(sorted(archetypes.items())),
        spaces=dict(sorted(spaces.items())),
        average_blank_spaces=round(blank_count / len(deck), 3),
        sampled_blank_spaces_per_card={
            "minimum": round(min(sampled_blank_averages), 3),
            "mean": round(sum(sampled_blank_averages) / sampled_decks, 3),
            "maximum": round(max(sampled_blank_averages), 3),
        },
        reserve_extra_initial_token_types_per_blank=reserve_types
        - normally_seeded_types,
        pastoral_food_demand_reduction_examples=pastoral_examples,
        settlement_family_capacity_examples=settlement_examples,
        commitment_round_caps={
            "wildlife_warden_bonus_fruit_over_7_rounds": 7,
            "bat_conservationist_bats_not_moved_over_7_rounds": 7,
            "pastoral_extra_recurring_food_reduction_per_goat": 1,
            "settlement_planner_gold_saved_per_location": 1,
            "forest_reserve_cards": 1,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260722)
    parser.add_argument("--decks", type=int, default=1000)
    args = parser.parse_args()
    print(
        json.dumps(
            asdict(build_report(args.seed, sampled_decks=args.decks)),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
