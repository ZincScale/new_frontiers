from __future__ import annotations

import unittest

from atiwa_living_landscape.generate_terrain import render_html, render_json
from atiwa_living_landscape.commitments import (
    Commitment,
    bats_required_for_action,
    food_demand,
    location_family_limit,
    location_gold_cost,
    may_leave_reserve,
    may_spend_for_food,
    wildlife_warden_fruit_bonus,
)
from atiwa_living_landscape.terrain import (
    Token,
    generate_terrain_deck,
    reserve_blank_accepts,
)


class TerrainGenerationTests(unittest.TestCase):
    def test_generator_is_deterministic_and_makes_36_valid_cards(self) -> None:
        first = generate_terrain_deck(seed=7)
        second = generate_terrain_deck(seed=7)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 36)
        self.assertTrue(all(len(card.spaces) == 8 for card in first))
        self.assertEqual(len({card.synthetic_id for card in first}), 36)

    def test_reserve_blank_accepts_every_nonfamily_token(self) -> None:
        self.assertFalse(reserve_blank_accepts(Token.FAMILY))
        for token in Token:
            if token is not Token.FAMILY:
                self.assertTrue(reserve_blank_accepts(token))

    def test_generated_deck_can_be_inspected_as_json_or_html(self) -> None:
        cards = generate_terrain_deck(seed=11, size=2)
        self.assertIn('"id": "SYN-', render_json(cards))
        rendered = render_html(cards)
        self.assertEqual(rendered.count('<section class="card">'), 2)
        self.assertIn("Testing geometry only", rendered)


class CommitmentRuleTests(unittest.TestCase):
    def test_wildlife_warden_bonus_is_conditional_and_capped_at_one(self) -> None:
        self.assertEqual(
            wildlife_warden_fruit_bonus(
                trees_from_wildlife=2, fruit_in_supply=3, legal_new_tree=True
            ),
            1,
        )
        self.assertEqual(
            wildlife_warden_fruit_bonus(
                trees_from_wildlife=0, fruit_in_supply=3, legal_new_tree=True
            ),
            0,
        )
        self.assertFalse(
            may_spend_for_food("wild_animal", Commitment.WILDLIFE_WARDEN)
        )

    def test_pastoral_cooperative_reduces_demand_but_cannot_spend_goats(self) -> None:
        self.assertEqual(food_demand(families=9, goats=3), 6)
        self.assertEqual(
            food_demand(
                families=9,
                goats=3,
                commitment=Commitment.PASTORAL_COOPERATIVE,
            ),
            3,
        )
        self.assertFalse(
            may_spend_for_food("goat", Commitment.PASTORAL_COOPERATIVE)
        )

    def test_settlement_planner_discount_and_family_cap(self) -> None:
        self.assertEqual(
            location_gold_cost(
                printed_cost=3,
                commitment=Commitment.DISTRIBUTED_SETTLEMENT_PLANNER,
            ),
            2,
        )
        self.assertEqual(
            location_gold_cost(
                printed_cost=0,
                commitment=Commitment.DISTRIBUTED_SETTLEMENT_PLANNER,
            ),
            0,
        )
        self.assertEqual(
            location_family_limit(
                printed_houses=4,
                commitment=Commitment.DISTRIBUTED_SETTLEMENT_PLANNER,
            ),
            2,
        )

    def test_bat_conservationist_changes_only_first_action(self) -> None:
        self.assertEqual(
            bats_required_for_action(
                first_action_this_round=True,
                commitment=Commitment.BAT_CONSERVATIONIST,
            ),
            2,
        )
        self.assertEqual(
            bats_required_for_action(
                first_action_this_round=False,
                commitment=Commitment.BAT_CONSERVATIONIST,
            ),
            3,
        )
        self.assertFalse(
            may_spend_for_food("fruit_bat", Commitment.BAT_CONSERVATIONIST)
        )

    def test_reserve_tokens_leave_only_for_mandatory_effects(self) -> None:
        self.assertFalse(may_leave_reserve(mandatory_effect=False))
        self.assertTrue(may_leave_reserve(mandatory_effect=True))


if __name__ == "__main__":
    unittest.main()
