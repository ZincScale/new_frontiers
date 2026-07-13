from __future__ import annotations

from enum import Enum

from roll_galaxy.model import Phase


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


SECTION_PHASE: dict[Section, Phase] = {
    Section.EXPLORE: Phase.EXPLORE,
    Section.DEVELOP: Phase.DEVELOP,
    Section.SETTLE: Phase.SETTLE,
    Section.PRODUCE: Phase.PRODUCE,
    Section.SHIP: Phase.SHIP,
}


PHASE_SECTION: dict[Phase, Section] = {
    phase: section for section, phase in SECTION_PHASE.items()
}


__all__ = [
    "PHASE_SECTION",
    "SECTION_ORDER",
    "SECTION_PHASE",
    "Section",
]
