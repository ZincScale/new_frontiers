"""Generate synthetic Atiwa-like Terrain records for prototype testing.

The generated records model rules-relevant capacity only.  They deliberately
do not reproduce the names, art, or exact composition of Atiwa's commercial
Terrain deck.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
import random


class Space(str, Enum):
    BLANK = "blank"
    WILD_ANIMAL = "wild_animal"
    TREE = "tree"
    FRUIT = "fruit"
    FRUIT_BAT = "fruit_bat"
    GOAT = "goat"
    HOUSE = "house"
    BLOCKED = "blocked"


class Token(str, Enum):
    WILD_ANIMAL = "wild_animal"
    TREE = "tree"
    FRUIT = "fruit"
    FRUIT_BAT = "fruit_bat"
    GOAT = "goat"
    FAMILY = "family"


@dataclass(frozen=True)
class TerrainCard:
    synthetic_id: str
    archetype: str
    spaces: tuple[Space, ...]
    nature_icons: int
    printed_vp: int

    def __post_init__(self) -> None:
        if len(self.spaces) != 8:
            raise ValueError("a Terrain card must have exactly eight spaces")
        if not 0 <= self.nature_icons <= 2:
            raise ValueError("synthetic nature icon count must be between 0 and 2")
        if self.spaces.count(Space.HOUSE) > 2:
            raise ValueError("synthetic Terrain cards may have at most two houses")

    @property
    def counts(self) -> Counter[Space]:
        return Counter(self.spaces)


_ARCHETYPES: dict[str, tuple[tuple[Space, ...], tuple[Space, ...]]] = {
    "forest": (
        (Space.TREE, Space.TREE, Space.WILD_ANIMAL),
        (Space.BLANK, Space.TREE, Space.WILD_ANIMAL, Space.FRUIT_BAT, Space.BLOCKED),
    ),
    "orchard": (
        (Space.TREE, Space.TREE, Space.FRUIT),
        (Space.BLANK, Space.TREE, Space.FRUIT, Space.FRUIT_BAT, Space.BLOCKED),
    ),
    "wildlife": (
        (Space.WILD_ANIMAL, Space.WILD_ANIMAL, Space.TREE),
        (Space.BLANK, Space.WILD_ANIMAL, Space.TREE, Space.FRUIT_BAT, Space.BLOCKED),
    ),
    "pasture": (
        (Space.GOAT, Space.GOAT, Space.TREE),
        (Space.BLANK, Space.GOAT, Space.TREE, Space.WILD_ANIMAL, Space.BLOCKED),
    ),
    "wetland": (
        (Space.FRUIT_BAT, Space.FRUIT_BAT, Space.TREE),
        (Space.BLANK, Space.FRUIT_BAT, Space.TREE, Space.FRUIT, Space.BLOCKED),
    ),
    "settlement_edge": (
        (Space.HOUSE, Space.TREE, Space.GOAT),
        (Space.BLANK, Space.TREE, Space.GOAT, Space.FRUIT_BAT, Space.BLOCKED),
    ),
}


def _make_card(rng: random.Random, index: int, archetype: str) -> TerrainCard:
    anchors, fill_pool = _ARCHETYPES[archetype]
    spaces = list(anchors)
    spaces.extend(rng.choice(fill_pool) for _ in range(8 - len(spaces)))
    rng.shuffle(spaces)

    flexible_spaces = spaces.count(Space.BLANK)
    blocked_spaces = spaces.count(Space.BLOCKED)
    houses = spaces.count(Space.HOUSE)
    nature_icons = rng.choices((0, 1, 2), weights=(5, 4, 1), k=1)[0]

    # Flexible cards receive lower printed VP; constrained cards receive more.
    # This is a testing heuristic, not a reconstruction of official values.
    printed_vp = max(-5, min(4, blocked_spaces + houses - flexible_spaces))

    return TerrainCard(
        synthetic_id=f"SYN-{index:02d}",
        archetype=archetype,
        spaces=tuple(spaces),
        nature_icons=nature_icons,
        printed_vp=printed_vp,
    )


def generate_terrain_deck(seed: int = 0, size: int = 36) -> tuple[TerrainCard, ...]:
    """Return a deterministic, shuffled synthetic Terrain deck."""

    if size < 1:
        raise ValueError("deck size must be positive")

    rng = random.Random(seed)
    archetypes = tuple(_ARCHETYPES)
    cards = [
        _make_card(rng, index, archetypes[(index - 1) % len(archetypes)])
        for index in range(1, size + 1)
    ]
    rng.shuffle(cards)
    return tuple(cards)


def normal_blank_accepts(token: Token, tokens_already_on_card: set[Token]) -> bool:
    """Apply the base blank-space prerequisite relevant to synthetic tests."""

    if token is Token.FAMILY:
        return False
    if token is Token.TREE:
        return Token.TREE in tokens_already_on_card
    if token is Token.FRUIT:
        return Token.FRUIT in tokens_already_on_card
    if token is Token.FRUIT_BAT:
        return Token.FRUIT_BAT in tokens_already_on_card
    return token in tokens_already_on_card


def reserve_blank_accepts(token: Token) -> bool:
    """Apply SC05's override for a blank space on the Reserve."""

    return token is not Token.FAMILY
