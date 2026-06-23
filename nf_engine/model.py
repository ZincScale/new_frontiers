from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class Good(str, Enum):
    NOVELTY = "novelty"
    RARE = "rare"
    GENES = "genes"
    ALIEN = "alien"


class WorldKind(str, Enum):
    GRAY = "gray"
    PRODUCTION = "production"
    WINDFALL = "windfall"


class SettleKind(str, Enum):
    CIVILIAN = "civilian"
    MILITARY = "military"


class Action(str, Enum):
    RETREAT = "retreat"
    DEVELOP = "develop"
    EXPLORE = "explore"
    SETTLE = "settle"
    PRODUCE = "produce"
    TRADE_CONSUME = "trade_consume"
    DIPLOMACY = "diplomacy"


@dataclass(frozen=True)
class Powers:
    military: int = 0
    develop_discount: int = 0
    settle_discount: int = 0
    explore_extra: int = 0
    trade_bonus: int = 0
    consume_vp_per_good: int = 0
    consume_credit_per_good: int = 0
    produce_credit: int = 0
    military_settle_vp: int = 0


@dataclass(frozen=True)
class DevelopmentTile:
    id: str
    name: str
    cost: int
    vp: int
    spaces: int
    large: bool = False
    powers: Powers = field(default_factory=Powers)
    score_bonus: Callable[["PlayerView"], int] | None = None


@dataclass(frozen=True)
class WorldTile:
    id: str
    name: str
    kind: WorldKind
    settle_kind: SettleKind
    cost_or_defense: int
    colonists: int
    vp: int
    good: Good | None = None
    powers: Powers = field(default_factory=Powers)
    score_bonus: Callable[["PlayerView"], int] | None = None


@dataclass(frozen=True)
class PlayerView:
    development_count: int
    large_development_count: int
    colony_count: int
    military_colony_count: int
    production_colony_count: int
    windfall_colony_count: int
    novelty_colony_count: int
    rare_colony_count: int
    genes_colony_count: int
    alien_colony_count: int
    goods_count: int
    novelty_goods_count: int
    rare_goods_count: int
    genes_goods_count: int
    alien_goods_count: int
    vp_chips: int
    military: int

