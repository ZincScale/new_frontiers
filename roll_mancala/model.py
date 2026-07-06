from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from roll_galaxy.model import DieColor, Good, PHASE_ORDER, Phase, Tile, TileKind


class Section(str, Enum):
    EXPLORE = "explore"
    DEVELOP = "develop"
    SETTLE = "settle"
    PRODUCE = "produce"
    SHIP = "ship"


SECTION_ORDER = (
    Section.EXPLORE,
    Section.DEVELOP,
    Section.SETTLE,
    Section.PRODUCE,
    Section.SHIP,
)


SECTION_PHASE: dict[Section, Optional[Phase]] = {
    Section.EXPLORE: Phase.EXPLORE,
    Section.DEVELOP: Phase.DEVELOP,
    Section.SETTLE: Phase.SETTLE,
    Section.PRODUCE: Phase.PRODUCE,
    Section.SHIP: Phase.SHIP,
}


COLOR_SECTION: dict[DieColor, Optional[Section]] = {
    DieColor.BLUE: Section.EXPLORE,
    DieColor.BROWN: Section.DEVELOP,
    DieColor.RED: Section.SETTLE,
    DieColor.GREEN: Section.PRODUCE,
    DieColor.PURPLE: Section.SHIP,
    DieColor.WHITE: None,
    DieColor.YELLOW: None,
}


PHASE_SECTION: dict[Phase, Section] = {
    Phase.EXPLORE: Section.EXPLORE,
    Phase.DEVELOP: Section.DEVELOP,
    Phase.SETTLE: Section.SETTLE,
    Phase.PRODUCE: Section.PRODUCE,
    Phase.SHIP: Section.SHIP,
}


@dataclass
class Construction:
    tile: Tile
    workers: list[DieColor] = field(default_factory=list)

    @property
    def progress(self) -> int:
        return len(self.workers)


@dataclass(frozen=True)
class SourceChoice:
    kind: str
    section: Optional[Section] = None
    color: Optional[DieColor] = None
    count: int = 0
    order: tuple[DieColor, ...] = ()
    entry_section: Optional[Section] = None
    fallback_phase: Optional[Phase] = None


@dataclass(frozen=True)
class SowResult:
    final_section: Optional[Section]
    selected_phase: Optional[Phase]
    placed: tuple[tuple[Section, DieColor], ...]
    overflow: tuple[DieColor, ...]
    bonus_credit: bool = False


@dataclass
class Player:
    name: str
    strategy: str
    sections: dict[Section, list[DieColor]] = field(default_factory=dict)
    spent: dict[DieColor, int] = field(default_factory=dict)
    dev_stack: list[Construction] = field(default_factory=list)
    world_stack: list[Construction] = field(default_factory=list)
    tableau: list[Tile] = field(default_factory=list)
    goods: list[Good] = field(default_factory=list)
    credits: int = 1
    vp_chips: int = 0
    selected_phases: list[Phase] = field(default_factory=list)
    selected_sections: list[Optional[Section]] = field(default_factory=list)
    dead_rounds: int = 0
    used_workers: int = 0
    completed_tiles: int = 0
    credits_earned: int = 0
    credits_spent: int = 0
    recovery_sows: int = 0
    color_match_bonuses: int = 0


__all__ = [
    "COLOR_SECTION",
    "Construction",
    "DieColor",
    "Good",
    "PHASE_ORDER",
    "PHASE_SECTION",
    "Phase",
    "Player",
    "SECTION_ORDER",
    "SECTION_PHASE",
    "Section",
    "SourceChoice",
    "SowResult",
    "Tile",
    "TileKind",
]
