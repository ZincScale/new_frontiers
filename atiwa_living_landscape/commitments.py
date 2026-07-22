"""Pure rule helpers for the five Stewardship Commitment prototypes."""

from __future__ import annotations

from enum import Enum


class Commitment(str, Enum):
    WILDLIFE_WARDEN = "wildlife_warden"
    PASTORAL_COOPERATIVE = "pastoral_cooperative"
    DISTRIBUTED_SETTLEMENT_PLANNER = "distributed_settlement_planner"
    BAT_CONSERVATIONIST = "bat_conservationist"
    FOREST_RESERVE_KEEPER = "forest_reserve_keeper"


def wildlife_warden_fruit_bonus(
    *, trees_from_wildlife: int, fruit_in_supply: int, legal_new_tree: bool
) -> int:
    """Return the number of bonus fruit provided by SC01 this round."""

    return int(trees_from_wildlife > 0 and fruit_in_supply > 0 and legal_new_tree)


def food_demand(
    *, families: int, goats: int, commitment: Commitment | None = None
) -> int:
    """Calculate food demand before tokens are spent."""

    goat_value = 2 if commitment is Commitment.PASTORAL_COOPERATIVE else 1
    return max(0, families - goat_value * goats)


def may_spend_for_food(
    token: str, commitment: Commitment | None = None
) -> bool:
    """Return whether a Commitment permits spending this token for food."""

    if commitment is Commitment.WILDLIFE_WARDEN and token == "wild_animal":
        return False
    if commitment is Commitment.PASTORAL_COOPERATIVE and token == "goat":
        return False
    if commitment is Commitment.BAT_CONSERVATIONIST and token == "fruit_bat":
        return False
    return True


def location_gold_cost(
    *, printed_cost: int, commitment: Commitment | None = None
) -> int:
    """Apply SC03's Location gold discount."""

    if printed_cost < 0:
        raise ValueError("printed cost cannot be negative")
    discount = (
        1 if commitment is Commitment.DISTRIBUTED_SETTLEMENT_PLANNER else 0
    )
    return max(0, printed_cost - discount)


def location_family_limit(
    *, printed_houses: int, commitment: Commitment | None = None
) -> int:
    """Return the maximum families permitted on one Location card."""

    if printed_houses < 0:
        raise ValueError("printed houses cannot be negative")
    if commitment is Commitment.DISTRIBUTED_SETTLEMENT_PLANNER:
        return min(2, printed_houses)
    return printed_houses


def bats_required_for_action(
    *, first_action_this_round: bool, commitment: Commitment | None = None
) -> int:
    """Return the fruit bats moved to the Night card for one bat action."""

    if commitment is Commitment.BAT_CONSERVATIONIST and first_action_this_round:
        return 2
    return 3


def may_leave_reserve(*, mandatory_effect: bool) -> bool:
    """Return whether SC05 permits a token to leave the Reserve."""

    return mandatory_effect
