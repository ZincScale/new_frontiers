"""Structured Roll tile-power conversions for Roll & Sow.

The source is ``Roll_for_the_Galaxy_all_tiles.xls``. The generated Tile records
retain phase tags but not their full text, so the rules that affect this engine
are kept explicitly here. Six-cost cards remain outside the ordinary
construction bag and are scored by ``RollAndSowGame`` as delayed goals; their
ongoing phase powers are therefore intentionally inactive.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from roll_galaxy.model import DieColor, Phase

from .model import Section


@dataclass(frozen=True)
class ReassignRule:
    count: int = 1
    destinations: Optional[frozenset[Section]] = None
    colors: Optional[frozenset[DieColor]] = None
    source_section: Optional[Section] = None


REASSIGN_RULES: dict[str, ReassignRule] = {
    # Backup Planning augments Dictate in the printed game. One generic route
    # is the retained simulator approximation until Dictate itself is modeled.
    "backup_planning": ReassignRule(),
    "colonial_affinity": ReassignRule(destinations=frozenset((Section.SETTLE,))),
    "diversification": ReassignRule(colors=frozenset((DieColor.WHITE,))),
    "executive_power": ReassignRule(count=2),
    "galactic_influence": ReassignRule(),
    "galactic_mandate": ReassignRule(count=3),
    "homeworld_patriotism": ReassignRule(count=2, colors=frozenset((DieColor.WHITE,))),
    "hydroponics_guild": ReassignRule(colors=frozenset((DieColor.BLUE, DieColor.GREEN))),
    "isolation_policy": ReassignRule(count=2, source_section=Section.EXPLORE),
    "local_subsidies": ReassignRule(colors=frozenset((DieColor.WHITE,))),
    "mad_scientists": ReassignRule(),
    "nanotechnology": ReassignRule(count=2),
    "operations_affinity": ReassignRule(
        destinations=frozenset((Section.EXPLORE, Section.PRODUCE))
    ),
    "propaganda_campaign": ReassignRule(count=2),
    "shipping_affinity": ReassignRule(destinations=frozenset((Section.SHIP,))),
    "space_mercenaries": ReassignRule(colors=frozenset((DieColor.RED, DieColor.BROWN))),
    "system_diversification": ReassignRule(
        count=2,
        colors=frozenset(
            (
                DieColor.BLUE,
                DieColor.BROWN,
                DieColor.GREEN,
                DieColor.YELLOW,
                DieColor.RED,
                DieColor.PURPLE,
            )
        ),
    ),
    "technology_affinity": ReassignRule(destinations=frozenset((Section.DEVELOP,))),
}


EXTRA_EXPLORE_WORKERS = {
    "alien_research_ship": 2,
    "major_research_labs": 1,
}

EXTRA_SHIP_WORKERS = {
    "organic_shipyards": 2,
    "space_docks": 1,
}


def phase_for_tag(tag: str) -> Phase:
    return {
        "phase_i": Phase.EXPLORE,
        "phase_ii": Phase.DEVELOP,
        "phase_iii": Phase.SETTLE,
        "phase_iv": Phase.PRODUCE,
        "phase_v": Phase.SHIP,
    }[tag]


__all__ = [
    "EXTRA_EXPLORE_WORKERS",
    "EXTRA_SHIP_WORKERS",
    "REASSIGN_RULES",
    "ReassignRule",
    "phase_for_tag",
]
