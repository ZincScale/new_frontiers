from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DieFace(str, Enum):
    MOVE = "move"
    ENERGY = "energy"
    CULTURE = "culture"
    ECONOMY = "economy"
    DIPLOMACY = "diplomacy"
    COLONY = "colony"


class Resource(str, Enum):
    ENERGY = "energy"
    CULTURE = "culture"
    MIXED = "mixed"


@dataclass(frozen=True)
class UpgradeCard:
    id: str
    name: str
    face: DieFace
    effect: str
    text: str
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlanetCard:
    id: str
    name: str
    colonize_face: DieFace
    track_length: int
    vp: int
    resource: Resource
    ability: str
    text: str
    tags: tuple[str, ...] = ()
    surface_effect: str = "gain_planet_resource"


@dataclass(frozen=True)
class EmpireStep:
    level: int
    dice: int
    ships: int
    vp: int
    upgrade_cost: Optional[int] = None


@dataclass(frozen=True)
class EmpirePersonality:
    id: str
    name: str
    text: str
    priority_faces: tuple[DieFace, ...]
    preferred_upgrade_faces: tuple[DieFace, ...]


@dataclass(frozen=True)
class RivalEmpireProfile:
    id: str
    name: str
    text: str
    priority_faces: tuple[DieFace, ...]
    pressure: str
    attack: str
    preferred_planet_tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class RivalDifficultyCard:
    id: str
    name: str
    text: str
    empire_level: int
    energy: int
    culture: int
    vp: int = 0


@dataclass
class Mission:
    planet: PlanetCard
    progress: int = 0


@dataclass
class Player:
    name: str
    personality: EmpirePersonality
    strategy: str = "balanced"
    rival_profile: Optional[RivalEmpireProfile] = None
    energy: int = 2
    culture: int = 1
    vp: int = 0
    empire_level: int = 1
    available_ships: int = 2
    missions: list[Mission] = field(default_factory=list)
    landed: list[PlanetCard] = field(default_factory=list)
    colonies: list[PlanetCard] = field(default_factory=list)
    upgrades: list[UpgradeCard] = field(default_factory=list)
    dice_used: list[DieFace] = field(default_factory=list)
