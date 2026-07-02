from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Phase(str, Enum):
    EXPLORE = "explore"
    DEVELOP = "develop"
    SETTLE = "settle"
    PRODUCE = "produce"
    SHIP = "ship"


PHASE_ORDER = (
    Phase.EXPLORE,
    Phase.DEVELOP,
    Phase.SETTLE,
    Phase.PRODUCE,
    Phase.SHIP,
)


class DieColor(str, Enum):
    WHITE = "white"
    BLUE = "blue"
    BROWN = "brown"
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    PURPLE = "purple"


COLOR_PHASE: dict[DieColor, Optional[Phase]] = {
    DieColor.WHITE: None,
    DieColor.BLUE: Phase.EXPLORE,
    DieColor.BROWN: Phase.DEVELOP,
    DieColor.RED: Phase.SETTLE,
    DieColor.GREEN: Phase.PRODUCE,
    DieColor.PURPLE: Phase.SHIP,
    DieColor.YELLOW: Phase.SHIP,
}


PHASE_COLOR: dict[Phase, DieColor] = {
    Phase.EXPLORE: DieColor.BLUE,
    Phase.DEVELOP: DieColor.BROWN,
    Phase.SETTLE: DieColor.RED,
    Phase.PRODUCE: DieColor.GREEN,
    Phase.SHIP: DieColor.PURPLE,
}


class TileKind(str, Enum):
    DEVELOPMENT = "development"
    WORLD = "world"


@dataclass
class CapacityTrack:
    color: DieColor
    current: int = 0
    maximum: int = 0


@dataclass(frozen=True)
class Tile:
    id: str
    name: str
    kind: TileKind
    cost: int
    vp: int
    grants: tuple[DieColor, ...] = ()
    placement: str = ""
    die_loss: int = 0
    immediate_credits: int = 0
    world_color: str = ""
    produces: bool = False
    tags: tuple[str, ...] = ()


@dataclass
class BuildSlot:
    tile: Tile
    progress: int = 0


@dataclass
class Good:
    world: Tile
    color: DieColor


@dataclass
class Player:
    name: str
    strategy: str
    tracks: dict[DieColor, CapacityTrack] = field(default_factory=dict)
    dev_stack: list[BuildSlot] = field(default_factory=list)
    world_stack: list[BuildSlot] = field(default_factory=list)
    tableau: list[Tile] = field(default_factory=list)
    goods: list[Good] = field(default_factory=list)
    credits: int = 1
    vp_chips: int = 0
    selected_phases: list[Phase] = field(default_factory=list)
    dead_rounds: int = 0
    used_pips: int = 0
    credits_earned: int = 0
    credits_spent: int = 0
    free_recharged: int = 0
    blocked_recharge: int = 0
    completed_tiles: int = 0
