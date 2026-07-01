from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, Optional, Union

from .cards import PERSONALITIES, PLANETS, RIVAL_EMPIRES, UPGRADES
from .model import DieFace, EmpirePersonality, EmpireStep, Mission, PlanetCard, Player, Resource, RivalEmpireProfile, UpgradeCard


STRATEGY_FACE_BIAS = {
    "balanced": {
        DieFace.MOVE: 2,
        DieFace.ENERGY: 2,
        DieFace.CULTURE: 2,
        DieFace.ECONOMY: 2,
        DieFace.DIPLOMACY: 2,
        DieFace.COLONY: 2,
    },
    "mobility": {
        DieFace.MOVE: 5,
        DieFace.COLONY: 3,
        DieFace.DIPLOMACY: 2,
        DieFace.ENERGY: 2,
        DieFace.CULTURE: 1,
        DieFace.ECONOMY: 1,
    },
    "economy": {
        DieFace.ECONOMY: 5,
        DieFace.ENERGY: 4,
        DieFace.CULTURE: 3,
        DieFace.COLONY: 2,
        DieFace.MOVE: 1,
        DieFace.DIPLOMACY: 1,
    },
    "culture": {
        DieFace.CULTURE: 5,
        DieFace.DIPLOMACY: 4,
        DieFace.ECONOMY: 2,
        DieFace.ENERGY: 2,
        DieFace.COLONY: 1,
        DieFace.MOVE: 1,
    },
    "colonizer": {
        DieFace.COLONY: 5,
        DieFace.DIPLOMACY: 4,
        DieFace.MOVE: 3,
        DieFace.ENERGY: 2,
        DieFace.CULTURE: 1,
        DieFace.ECONOMY: 1,
    },
}


EMPIRE_TRACK = {
    1: EmpireStep(1, dice=4, ships=2, vp=0, upgrade_cost=2),
    2: EmpireStep(2, dice=5, ships=3, vp=1, upgrade_cost=3),
    3: EmpireStep(3, dice=5, ships=3, vp=2, upgrade_cost=4),
    4: EmpireStep(4, dice=6, ships=4, vp=4, upgrade_cost=5),
    5: EmpireStep(5, dice=6, ships=4, vp=6, upgrade_cost=6),
    6: EmpireStep(6, dice=7, ships=4, vp=8),
}


@dataclass(frozen=True)
class GameConfig:
    max_ships: int = 4
    resource_cap: int = 7
    planet_market_size: Optional[int] = None
    max_active_missions: int = 3
    enable_upgrades: bool = True
    upgrade_market_size: int = 3
    upgrade_cost: int = 3
    max_upgrades: int = 3
    auto_mitigate_dice: bool = True
    target_vp: int = 21
    max_turns: int = 30


@dataclass(frozen=True)
class TurnReport:
    player: str
    roll: tuple[DieFace, ...]
    used: tuple[DieFace, ...]
    bought_upgrade: Optional[str]
    claimed_planets: tuple[str, ...]
    vp: int
    colonies: int


class UpgradeGame:
    def __init__(
        self,
        players: Optional[Iterable[tuple[str, Union[str, EmpirePersonality], str] | tuple[str, Union[str, EmpirePersonality], str, str]]] = None,
        seed: Optional[int] = None,
        config: Optional[GameConfig] = None,
    ):
        self.rng = random.Random(seed)
        self.config = config or GameConfig()
        personalities = {personality.id: personality for personality in PERSONALITIES}
        solo_profiles = {profile.id: profile for profile in RIVAL_EMPIRES}
        player_specs = list(players or [
            ("P1", "frontier_union", "mobility"),
            ("P2", "star_cartel", "economy"),
        ])
        self.planet_market_size = self.config.planet_market_size or min(6, len(player_specs) + 2)
        self.players = [
            Player(
                name=spec[0],
                personality=personalities[spec[1]] if isinstance(spec[1], str) else spec[1],
                strategy=spec[2],
                available_ships=self.empire_step(1).ships,
                rival_profile=solo_profiles[spec[3]] if len(spec) > 3 and spec[3] else None,
            )
            for spec in player_specs
        ]
        self.turn = 0
        self.upgrade_deck = list(UPGRADES)
        self.rng.shuffle(self.upgrade_deck)
        self.upgrade_market: list[UpgradeCard] = []
        self.discarded_upgrades: list[UpgradeCard] = []
        if self.config.enable_upgrades:
            self._refill_market()
        self.planet_deck = list(PLANETS)
        self.rng.shuffle(self.planet_deck)
        self.planet_market: list[PlanetCard] = []
        self.claimed_planets: list[PlanetCard] = []
        self._refill_planets()
        self._turn_faces: list[DieFace] = []
        self._turn_claims: list[PlanetCard] = []
        self._turn_scored_abilities: set[str] = set()
        self._last_move_to_orbit = False
        self.solo_profiles = solo_profiles
        self._followed_this_round: set[str] = set()

    def play(self):
        reports = []
        while not self.game_over():
            reports.extend(self.play_round())
        return self.final_scores(), reports

    def play_round(self):
        self.turn += 1
        self._followed_this_round = set()
        reports = []
        for active in self.players:
            report = self.play_turn(active)
            reports.append(report)
            for follower in [player for player in self.players if player is not active]:
                self.auto_follow(follower, report.used)
        return reports

    def play_turn(self, player: Player):
        player.dice_used.clear()
        self._turn_faces = []
        self._turn_claims = []
        self._turn_scored_abilities = set()
        roll = tuple(self.roll_dice(player))
        usable_roll = tuple(self.mitigate_roll(player, list(roll))) if self.config.auto_mitigate_dice else roll
        used = tuple(sorted(usable_roll, key=lambda face: self.face_priority(player, face), reverse=True))
        for face in used:
            self.use_die(player, face)
        if self.can_use_emergency_protocol(player, used):
            self.use_emergency_protocol(player)
        self.apply_rival_momentum(player)
        bought = self.auto_buy_upgrade(player)
        self.apply_end_turn_planets(player)
        return TurnReport(
            player.name,
            roll,
            used,
            bought.name if bought else None,
            tuple(planet.name for planet in self._turn_claims),
            player.vp,
            len(player.colonies),
        )

    def roll_dice(self, player: Player):
        faces = list(DieFace)
        return [self.rng.choice(faces) for _ in range(self.empire_step(player.empire_level).dice)]

    def mitigate_roll(self, player: Player, roll: list[DieFace]):
        roll = self.free_reroll_dead_faces(player, roll)
        return self.convert_for_missing_setup(player, roll)

    def free_reroll_dead_faces(self, player: Player, roll: list[DieFace]):
        dead = [face for face in roll if self.face_priority(player, face) <= 0]
        if not dead:
            return roll
        rerolled = list(roll)
        for index, face in enumerate(rerolled):
            if face in dead:
                rerolled[index] = self.rng.choice(list(DieFace))
        return rerolled

    def convert_for_missing_setup(self, player: Player, roll: list[DieFace]):
        if self.config.enable_upgrades and len(player.upgrades) >= 2:
            return roll
        can_launch = player.available_ships > 0 and len(player.missions) < self.config.max_active_missions
        if not can_launch or DieFace.MOVE in roll or len(roll) < 3:
            return roll
        ranked = sorted(range(len(roll)), key=lambda index: self.face_priority(player, roll[index]))
        spent = set(ranked[:2])
        converted = ranked[2]
        return [DieFace.MOVE if index == converted else face for index, face in enumerate(roll) if index not in spent]

    def use_die(self, player: Player, face: DieFace):
        player.dice_used.append(face)
        self._turn_faces.append(face)
        if face is DieFace.MOVE:
            self._last_move_to_orbit = False
        claimed_by_base = self.apply_base_face(player, face)
        claimed_by_upgrade = False
        for upgrade in [card for card in player.upgrades if card.face is face]:
            claimed_by_upgrade = self.apply_upgrade(player, upgrade, claimed_by_base or claimed_by_upgrade) or claimed_by_upgrade
        self.apply_after_die_planets(player, face)

    def auto_follow(self, player: Player, available_faces: Iterable[DieFace]):
        if player.culture <= 0:
            return None
        if player.name in self._followed_this_round:
            return None
        candidates = [face for face in available_faces if self.face_priority(player, face) > 0]
        if not candidates:
            return None
        face = max(candidates, key=lambda candidate: self.face_priority(player, candidate))
        self.spend_resource(player, Resource.CULTURE, 1)
        previous_faces = self._turn_faces
        previous_claims = self._turn_claims
        previous_scored = self._turn_scored_abilities
        self._turn_faces = []
        self._turn_claims = []
        self._turn_scored_abilities = set()
        self.use_die(player, face)
        self.apply_end_turn_planets(player)
        self._followed_this_round.add(player.name)
        self._turn_faces = previous_faces
        self._turn_claims = previous_claims
        self._turn_scored_abilities = previous_scored
        return face

    def apply_base_face(self, player: Player, face: DieFace):
        if face is DieFace.MOVE:
            self.move_ship(player)
            return False
        if face is DieFace.ENERGY:
            self.gain_resource(player, Resource.ENERGY, self.resource_income(player, Resource.ENERGY))
            return False
        if face is DieFace.CULTURE:
            self.gain_resource(player, Resource.CULTURE, self.resource_income(player, Resource.CULTURE))
            return False
        if face is DieFace.ECONOMY:
            return self.advance_mission(player, DieFace.ECONOMY, 1)
        if face is DieFace.DIPLOMACY:
            return self.advance_mission(player, DieFace.DIPLOMACY, 1)
        if face is DieFace.COLONY:
            if self.can_upgrade_empire(player):
                self.upgrade_empire(player)
                return False
            if self.use_colony_power(player):
                return False
            return False
        raise ValueError(f"unknown face: {face}")

    def apply_upgrade(self, player: Player, upgrade: UpgradeCard, already_claimed: bool):
        effect = upgrade.effect
        if effect == "move_orbit_resource":
            if self._last_move_to_orbit:
                self.gain_courier_resource(player)
        elif effect == "move_colony_progress":
            progressed = [mission for mission in player.missions if mission.progress > 0]
            if progressed:
                return self.advance_specific_mission(player, self.best_mission(player, progressed), 1)
            if player.missions and not player.colonies and player.energy > 0:
                self.spend_resource(player, Resource.ENERGY, 1)
                return self.advance_any_mission(player, 1)
            if player.missions and player.available_ships == 0 and player.energy > 0:
                self.spend_resource(player, Resource.ENERGY, 1)
                return self.advance_any_mission(player, 1)
        elif effect == "extra_energy":
            capped = player.energy >= self.config.resource_cap
            self.gain_resource(player, Resource.ENERGY, 1)
            if capped and self.mark_once("overflow_energy"):
                return self.advance_mission(player, DieFace.ECONOMY, 1)
        elif effect == "energy_vp_with_colonies":
            if len(player.colonies) >= 2:
                player.vp += 1
        elif effect == "extra_culture_with_colony":
            if player.colonies:
                capped = player.culture >= self.config.resource_cap
                self.gain_resource(player, Resource.CULTURE, 1)
                if capped and self.mark_once("overflow_culture"):
                    return self.advance_mission(player, DieFace.DIPLOMACY, 1)
        elif effect == "culture_diplomacy_progress":
            if self.mark_once("soft_power_networks"):
                return self.advance_mission(player, DieFace.DIPLOMACY, 1)
        elif effect == "economy_culture":
            self.gain_resource(player, Resource.CULTURE, 1)
        elif effect == "economy_colony_energy":
            capped = player.energy >= self.config.resource_cap
            convoy_energy = min(2, len(player.colonies))
            self.gain_resource(player, Resource.ENERGY, convoy_energy)
            if convoy_energy > 0 and capped and self.mark_once("merchant_convoys_overflow"):
                return self.advance_mission(player, DieFace.ECONOMY, 1)
        elif effect == "extra_diplomacy_progress":
            return self.advance_mission(player, DieFace.DIPLOMACY, 1)
        elif effect == "diplomacy_claim_vp":
            if already_claimed:
                player.vp += 1
        elif effect == "extra_colony_progress":
            if player.missions:
                return self.advance_any_mission(player, 1)
            if player.available_ships > 0 and player.energy >= 2:
                self.spend_resource(player, Resource.ENERGY, 2)
                self.start_mission(player)
            elif player.available_ships > 0 and not player.colonies and player.culture >= 2:
                self.spend_resource(player, Resource.CULTURE, 2)
                self.start_mission(player)
        elif effect == "colony_claim_culture":
            if already_claimed:
                self.gain_resource(player, Resource.CULTURE, 1)
                player.vp += 1
        else:
            raise ValueError(f"unknown upgrade effect: {effect}")
        return False

    def move_ship(self, player: Player):
        if player.available_ships <= 0:
            return self.redeploy_landed_ship(player)
        if self.should_land_on_surface(player):
            return self.land_on_surface(player)
        return self.start_mission(player)

    def should_land_on_surface(self, player: Player):
        if len(player.missions) >= self.config.max_active_missions:
            return True
        if player.energy <= 1 or player.culture <= 1:
            return True
        return False

    def land_on_surface(self, player: Player):
        active_ids = {planet.id for planet in player.landed}
        candidates = [planet for planet in self.planet_market if planet.id not in active_ids]
        if not candidates:
            return None
        choice = max(candidates, key=lambda planet: self.surface_value(player, planet))
        player.available_ships -= 1
        player.landed.append(choice)
        self.resolve_surface_effect(player, choice)
        return choice

    def start_mission(self, player: Player):
        if player.available_ships <= 0 or len(player.missions) >= self.config.max_active_missions:
            return None
        active_ids = {mission.planet.id for mission in player.missions}
        candidates = [planet for planet in self.planet_market if planet.id not in active_ids]
        if not candidates:
            return None
        choice = max(candidates, key=lambda planet: self.planet_value(player, planet))
        player.available_ships -= 1
        player.missions.append(Mission(choice))
        self._last_move_to_orbit = True
        return choice

    def redeploy_landed_ship(self, player: Player):
        if not player.landed:
            return None
        old_post = min(player.landed, key=lambda planet: self.surface_value(player, planet))
        player.landed.remove(old_post)
        self.recover_ship(player)
        return old_post

    def advance_mission(self, player: Player, face: DieFace, amount: int):
        candidates = [mission for mission in player.missions if mission.planet.colonize_face is face]
        if not candidates:
            return False
        return self.advance_specific_mission(player, self.best_mission(player, candidates), amount)

    def advance_any_mission(self, player: Player, amount: int):
        if not player.missions:
            return False
        return self.advance_specific_mission(player, self.best_mission(player, player.missions), amount)

    def can_use_emergency_protocol(self, player: Player, available_faces: Iterable[DieFace]):
        if player.culture <= 0 or not player.missions:
            return False
        faces = set(available_faces)
        has_matching_progress = any(mission.planet.colonize_face in faces for mission in player.missions)
        has_wild_progress = DieFace.COLONY in faces and (
            any(upgrade.effect == "extra_colony_progress" for upgrade in player.upgrades)
            or self.use_colony_power_available(player)
        )
        return not has_matching_progress and not has_wild_progress

    def use_emergency_protocol(self, player: Player):
        if player.culture <= 0 or not player.missions:
            return False
        self.spend_resource(player, Resource.CULTURE, 1)
        self.advance_any_mission(player, 1)
        return True

    def best_mission(self, player: Player, missions: list[Mission]):
        return max(
            missions,
            key=lambda mission: (
                mission.progress + 1 >= mission.planet.track_length,
                self.planet_value(player, mission.planet),
                mission.progress,
            ),
        )

    def advance_specific_mission(self, player: Player, mission: Mission, amount: int):
        mission.progress += amount
        if mission.progress < mission.planet.track_length:
            return False
        self.claim_planet(player, mission)
        return True

    def claim_planet(self, player: Player, mission: Mission):
        planet = mission.planet
        player.missions.remove(mission)
        self.recover_ship(player)
        self.return_landed_ship(player, planet)
        player.colonies.append(planet)
        player.vp += planet.vp
        self.claimed_planets.append(planet)
        self._turn_claims.append(planet)
        self.apply_claim_planet_ability(player, planet)
        if player.rival_profile:
            self.apply_rival_pressure(player, planet)
        if planet in self.planet_market:
            self.planet_market.remove(planet)
            self.return_contested_missions(planet, except_player=player)
            self._refill_planets()

    def auto_buy_upgrade(self, player: Player):
        if not self.config.enable_upgrades:
            return None
        if len(player.upgrades) >= self.config.max_upgrades:
            return None
        affordable = self.affordable_upgrades(player)
        if not affordable:
            return None
        choice = max(affordable, key=lambda card: self.upgrade_value(player, card))
        spend = self.choose_upgrade_payment(player)
        return self.buy_upgrade(player, choice, spend=spend)

    def affordable_upgrades(self, player: Player):
        if (
            player.energy < self.discounted_upgrade_cost(player, "energy")
            and player.culture < self.discounted_upgrade_cost(player, "culture")
        ):
            return []
        owned = {card.id for card in player.upgrades}
        return [card for card in self.upgrade_market if card.id not in owned]

    def buy_upgrade(self, player: Player, upgrade: UpgradeCard, spend: str = "energy", replace: Optional[UpgradeCard] = None):
        if not self.config.enable_upgrades:
            raise ValueError("upgrade module is disabled")
        if upgrade not in self.upgrade_market:
            raise ValueError("upgrade must be in the market")
        if len(player.upgrades) >= self.config.max_upgrades:
            if replace is None:
                raise ValueError("player already has the maximum number of upgrades")
            player.upgrades.remove(replace)
            self.discarded_upgrades.append(replace)
        self.pay_upgrade_cost(player, spend)
        player.upgrades.append(upgrade)
        self.upgrade_market.remove(upgrade)
        self.apply_upgrade_bought_planets(player)
        self._refill_market()
        return upgrade

    def pay_upgrade_cost(self, player: Player, spend: str):
        cost = self.discounted_upgrade_cost(player, spend)
        if spend == "energy":
            self.spend_resource(player, Resource.ENERGY, cost)
        elif spend == "culture":
            self.spend_resource(player, Resource.CULTURE, cost)
        else:
            raise ValueError("spend must be energy or culture")

    def discounted_upgrade_cost(self, player: Player, spend: str):
        cost = self.config.upgrade_cost
        if spend == "energy" and self.has_ability(player, "upgrade_energy_discount"):
            cost -= 1
        if spend == "culture" and self.has_ability(player, "upgrade_culture_discount"):
            cost -= 1
        return max(0, cost)

    def choose_upgrade_payment(self, player: Player):
        energy_cost = self.discounted_upgrade_cost(player, "energy")
        culture_cost = self.discounted_upgrade_cost(player, "culture")
        if player.energy >= energy_cost and player.energy >= player.culture:
            return "energy"
        if player.culture >= culture_cost:
            return "culture"
        return "culture"

    def face_priority(self, player: Player, face: DieFace):
        priority = STRATEGY_FACE_BIAS[player.strategy][face]
        if player.rival_profile:
            priority += self.rival_face_priority(player.rival_profile, face) * 3
        if face is DieFace.MOVE and player.available_ships > 0 and len(player.missions) < self.config.max_active_missions:
            priority += 10 if not player.missions else 4
        if face is DieFace.MOVE and not self.move_face_has_value(player):
            priority -= 8
        if face in (DieFace.ECONOMY, DieFace.DIPLOMACY):
            if not any(mission.planet.colonize_face is face for mission in player.missions):
                priority -= 4
        if face is DieFace.COLONY:
            if self.can_upgrade_empire(player):
                priority += 6
            elif player.colonies:
                priority += 2
            elif not player.missions:
                priority -= 4
        if face in player.personality.priority_faces:
            priority += len(player.personality.priority_faces) - player.personality.priority_faces.index(face)
        return priority

    def move_face_has_value(self, player: Player):
        if player.available_ships > 0:
            return True
        if player.landed and not player.missions and len(player.missions) < self.config.max_active_missions:
            return True
        if self.has_upgrade(player, "frontier_beacons") and player.missions:
            if any(mission.progress > 0 for mission in player.missions):
                return True
            if player.energy > 0 and (not player.colonies or player.available_ships == 0):
                return True
        return any(
            planet.ability in ("move_energy", "move_culture", "move_progress")
            for planet in player.colonies
        )

    def upgrade_value(self, player: Player, upgrade: UpgradeCard):
        value = STRATEGY_FACE_BIAS[player.strategy][upgrade.face] * 2
        if upgrade.face in player.personality.preferred_upgrade_faces:
            value += 8
        if player.rival_profile and upgrade.face in player.rival_profile.priority_faces:
            value += self.rival_face_priority(player.rival_profile, upgrade.face) * 2
        if player.rival_profile:
            value += sum(2 for tag in upgrade.tags if tag in player.rival_profile.preferred_planet_tags)
        value += sum(2 for tag in upgrade.tags if tag in player.strategy)
        if "score" in upgrade.tags:
            value += 1 + len(player.colonies)
        return value

    def rival_action_order(self, profile: RivalEmpireProfile, roll: Iterable[DieFace]):
        return tuple(sorted(roll, key=lambda face: self.rival_face_priority(profile, face), reverse=True))

    def rival_face_priority(self, profile: RivalEmpireProfile, face: DieFace):
        if face not in profile.priority_faces:
            return 0
        return len(profile.priority_faces) - profile.priority_faces.index(face)

    def rival_planet_value(self, profile: RivalEmpireProfile, planet: PlanetCard):
        value = planet.vp * 2
        if profile.pressure == "short_tracks":
            value += max(0, 6 - planet.track_length)
        if profile.pressure == "empire_upgrade" and "upgrade" in planet.tags:
            value += 5
        if profile.pressure == "resource_denial" and planet.resource in (Resource.ENERGY, Resource.CULTURE, Resource.MIXED):
            value += 3
        if profile.pressure == "dice_control" and planet.colonize_face is DieFace.DIPLOMACY:
            value += 3
        value += sum(2 for tag in planet.tags if tag in profile.preferred_planet_tags)
        return value

    def planet_value(self, player: Player, planet: PlanetCard):
        if player.rival_profile:
            return self.rival_planet_value(player.rival_profile, planet)
        value = planet.vp * 3
        value -= planet.track_length
        value += STRATEGY_FACE_BIAS[player.strategy][planet.colonize_face]
        value += sum(2 for tag in planet.tags if tag in player.strategy)
        if planet.colonize_face in player.personality.priority_faces:
            value += 2
        if planet.resource is Resource.ENERGY and "economy" in player.strategy:
            value += 2
        if planet.resource is Resource.CULTURE and "culture" in player.strategy:
            value += 2
        if "upgrade" in planet.tags and len(player.upgrades) < self.config.max_upgrades:
            value += 3
        return value

    def apply_rival_pressure(self, rival: Player, planet: PlanetCard):
        profile = rival.rival_profile
        if profile is None:
            return
        opponents = [player for player in self.players if player is not rival]
        if profile.attack == "regress_player_orbit":
            target = self.best_opponent_mission(opponents)
            if target:
                target.progress = max(0, target.progress - 1)
        elif profile.attack == "tax_resources":
            for opponent in opponents:
                self.reduce_highest_resource(opponent, 1)
        elif profile.attack == "steal_resource":
            for opponent in opponents:
                stolen = self.reduce_highest_resource(opponent, 1)
                if stolen is Resource.ENERGY:
                    self.gain_resource(rival, Resource.ENERGY, 1)
                elif stolen is Resource.CULTURE:
                    self.gain_resource(rival, Resource.CULTURE, 1)
        elif profile.attack == "lock_follow":
            self._followed_this_round.update(opponent.name for opponent in opponents)

    def apply_rival_momentum(self, rival: Player):
        profile = rival.rival_profile
        if profile is None:
            return
        if profile.priority_faces[0] not in self._turn_faces:
            return
        if profile.pressure == "short_tracks":
            progressed = [mission for mission in rival.missions if mission.progress > 0]
            if progressed:
                self.advance_specific_mission(rival, self.best_mission(rival, progressed), 1)
        elif profile.pressure == "empire_upgrade":
            if self.can_upgrade_empire(rival):
                self.upgrade_empire(rival)
            elif rival.missions:
                self.advance_any_mission(rival, 1)
            elif rival.available_ships > 0:
                self.start_mission(rival)
        elif profile.pressure == "resource_denial":
            if rival.missions:
                self.advance_any_mission(rival, 1)
            elif rival.available_ships > 0:
                self.start_mission(rival)
        elif profile.pressure == "dice_control":
            self.advance_mission(rival, DieFace.DIPLOMACY, 1)

    def best_opponent_mission(self, opponents: list[Player]):
        candidates = [mission for opponent in opponents for mission in opponent.missions]
        if not candidates:
            return None
        return max(candidates, key=lambda mission: (mission.progress, mission.planet.vp, -mission.planet.track_length))

    def reduce_highest_resource(self, player: Player, amount: int):
        if player.energy <= 0 and player.culture <= 0:
            return None
        if player.energy >= player.culture and player.energy > 0:
            player.energy = max(0, player.energy - amount)
            return Resource.ENERGY
        player.culture = max(0, player.culture - amount)
        return Resource.CULTURE

    def surface_value(self, player: Player, planet: PlanetCard):
        value = 1
        if planet.resource is Resource.ENERGY and player.energy <= player.culture:
            value += 4
        if planet.resource is Resource.CULTURE and player.culture <= player.energy:
            value += 4
        if planet.resource is Resource.MIXED:
            value += 3
        value += sum(1 for tag in planet.tags if tag in player.strategy)
        return value

    def resource_income(self, player: Player, resource: Resource):
        landed = sum(1 for planet in player.landed if planet.resource in (resource, Resource.MIXED))
        orbiting = sum(1 for mission in player.missions if mission.planet.resource in (resource, Resource.MIXED))
        base = landed + orbiting
        if resource is Resource.ENERGY:
            base += player.available_ships
        if base == 0:
            base = 1
        if resource is Resource.ENERGY and self.has_ability(player, "energy_faces_plus"):
            base += 1
        if resource is Resource.CULTURE and self.has_ability(player, "culture_faces_plus"):
            base += 1
        return base

    def gain_resource(self, player: Player, resource: Resource, amount: int):
        if resource is Resource.ENERGY:
            player.energy = min(self.config.resource_cap, player.energy + amount)
        elif resource is Resource.CULTURE:
            player.culture = min(self.config.resource_cap, player.culture + amount)
        elif resource is Resource.MIXED:
            self.gain_resource(player, Resource.ENERGY, amount)
            self.gain_resource(player, Resource.CULTURE, amount)

    def spend_resource(self, player: Player, resource: Resource, amount: int):
        if resource is Resource.ENERGY:
            if player.energy < amount:
                raise ValueError("not enough energy")
            player.energy -= amount
        elif resource is Resource.CULTURE:
            if player.culture < amount:
                raise ValueError("not enough culture")
            player.culture -= amount
        else:
            raise ValueError("must spend a specific resource")

    def gain_courier_resource(self, player: Player):
        if player.energy >= self.config.resource_cap and player.culture < self.config.resource_cap:
            self.gain_resource(player, Resource.CULTURE, 1)
        elif player.culture >= self.config.resource_cap and player.energy < self.config.resource_cap:
            self.gain_resource(player, Resource.ENERGY, 1)
        elif player.energy <= player.culture:
            self.gain_resource(player, Resource.ENERGY, 1)
        else:
            self.gain_resource(player, Resource.CULTURE, 1)

    def resolve_surface_effect(self, player: Player, planet: PlanetCard):
        if planet.surface_effect == "gain_planet_resource":
            self.gain_resource(player, planet.resource, 1)
        elif planet.surface_effect == "advance_matching_mission":
            self.advance_mission(player, planet.colonize_face, 1)

    def can_upgrade_empire(self, player: Player):
        step = self.empire_step(player.empire_level)
        if step.upgrade_cost is None:
            return False
        return player.energy >= step.upgrade_cost or player.culture >= step.upgrade_cost

    def upgrade_empire(self, player: Player):
        step = self.empire_step(player.empire_level)
        if step.upgrade_cost is None:
            return False
        if player.energy >= step.upgrade_cost and player.energy >= player.culture:
            self.spend_resource(player, Resource.ENERGY, step.upgrade_cost)
        elif player.culture >= step.upgrade_cost:
            self.spend_resource(player, Resource.CULTURE, step.upgrade_cost)
        else:
            return False
        player.empire_level += 1
        ship_gain = self.empire_step(player.empire_level).ships - self.empire_step(player.empire_level - 1).ships
        if ship_gain > 0:
            self.recover_ship(player, ship_gain)
        return True

    def use_colony_power(self, player: Player):
        if not player.colonies:
            return False
        colony = max(player.colonies, key=lambda planet: self.surface_value(player, planet))
        self.resolve_surface_effect(player, colony)
        return True

    def use_colony_power_available(self, player: Player):
        return bool(player.colonies)

    def empire_step(self, level: int):
        return EMPIRE_TRACK[min(max(level, 1), max(EMPIRE_TRACK))]

    def apply_after_die_planets(self, player: Player, face: DieFace):
        for planet in list(player.colonies):
            ability = planet.ability
            if face is DieFace.MOVE and ability == "move_energy":
                self.gain_resource(player, Resource.ENERGY, 1)
            elif face is DieFace.MOVE and ability == "move_culture":
                self.gain_resource(player, Resource.CULTURE, 1)
            elif face is DieFace.MOVE and ability == "move_progress":
                self.advance_any_mission(player, 1)
            elif face is DieFace.ECONOMY and ability == "economy_vp":
                self.score_once(player, planet, 1)
            elif face is DieFace.ECONOMY and ability == "economy_culture":
                self.gain_resource(player, Resource.CULTURE, 1)
            elif face is DieFace.DIPLOMACY and ability == "diplomacy_vp":
                self.score_once(player, planet, 1)
            elif face is DieFace.DIPLOMACY and ability == "diplomacy_energy":
                self.gain_resource(player, Resource.ENERGY, 1)
            elif face is DieFace.DIPLOMACY and ability == "diplomacy_culture":
                self.gain_resource(player, Resource.CULTURE, 1)
            elif face is DieFace.CULTURE and ability == "culture_progress":
                self.advance_mission(player, DieFace.DIPLOMACY, 1)
            elif face is DieFace.COLONY and ability == "colony_energy":
                self.gain_resource(player, Resource.ENERGY, 1)
            elif face is DieFace.COLONY and ability == "colony_culture":
                self.gain_resource(player, Resource.CULTURE, 1)
            elif face is DieFace.ENERGY and ability == "energy_colony_progress":
                self.advance_mission(player, DieFace.ECONOMY, 1)
            elif face is DieFace.ENERGY and ability == "resource_balance" and player.culture < player.energy:
                self.gain_resource(player, Resource.CULTURE, 1)
            elif face is DieFace.CULTURE and ability == "culture_balance" and player.energy < player.culture:
                self.gain_resource(player, Resource.ENERGY, 1)

    def apply_claim_planet_ability(self, player: Player, planet: PlanetCard):
        ability = planet.ability
        if ability == "energy_on_claim":
            self.gain_resource(player, Resource.ENERGY, 2)
        elif ability == "culture_on_claim":
            self.gain_resource(player, Resource.CULTURE, 2)
        elif ability == "ship_on_claim":
            self.recover_ship(player)
        elif ability == "vp_on_claim":
            player.vp += 1
        elif ability == "economy_on_claim_vp" and planet.colonize_face is DieFace.ECONOMY:
            player.vp += 1
        elif ability == "diplomacy_on_claim_vp" and planet.colonize_face is DieFace.DIPLOMACY:
            player.vp += 1
        for colony in player.colonies:
            if colony is planet:
                continue
            if colony.ability == "claim_culture_vp" and planet.resource is Resource.CULTURE:
                player.vp += 1

    def apply_upgrade_bought_planets(self, player: Player):
        for planet in player.colonies:
            if planet.ability == "upgrade_vp":
                player.vp += 1
            elif planet.ability == "upgrade_draw" and self.upgrade_market:
                self.discarded_upgrades.append(self.upgrade_market.pop(0))

    def apply_end_turn_planets(self, player: Player):
        if self.has_ability(player, "balanced_income"):
            if DieFace.CULTURE in self._turn_faces and DieFace.ENERGY in self._turn_faces:
                player.vp += 1
        if self.has_ability(player, "low_resource_vp") and player.energy + player.culture <= 2:
            player.vp += 1

    def score_once(self, player: Player, planet: PlanetCard, amount: int):
        if planet.id in self._turn_scored_abilities:
            return
        player.vp += amount
        self._turn_scored_abilities.add(planet.id)

    def mark_once(self, key: str):
        if key in self._turn_scored_abilities:
            return False
        self._turn_scored_abilities.add(key)
        return True

    def has_ability(self, player: Player, ability: str):
        return any(planet.ability == ability for planet in player.colonies)

    def has_upgrade(self, player: Player, upgrade_id: str):
        return any(upgrade.id == upgrade_id for upgrade in player.upgrades)

    def final_scores(self):
        scores = []
        for player in self.players:
            score = self.current_score(player) + self.endgame_bonus(player)
            scores.append((player.name, score, self.tie_breaker(player), self.player_summary(player)))
        return sorted(scores, key=lambda item: (item[1], item[2]), reverse=True)

    def current_score(self, player: Player):
        return player.vp + self.empire_vp_score(player)

    def empire_vp_score(self, player: Player):
        return min(self.empire_step(player.empire_level).vp, len(player.colonies) * 3)

    def endgame_bonus(self, player: Player):
        bonus = 0
        for planet in player.colonies:
            if planet.ability == "three_upgrade_vp" and len(player.upgrades) >= 3:
                bonus += 2
            elif planet.ability == "end_energy_vp":
                bonus += player.energy // 4
            elif planet.ability == "end_culture_vp":
                bonus += player.culture // 4
        if self.has_upgrade(player, "settler_mandate") and self.has_upgrade(player, "colony_prefabs"):
            bonus += max(0, len(player.colonies) - 1)
        if self.has_upgrade(player, "warp_couriers") and self.has_upgrade(player, "frontier_beacons"):
            bonus += min(3, len(player.missions) + len(player.landed))
        return bonus

    def tie_breaker(self, player: Player):
        return player.energy + player.culture + len(player.colonies) + player.empire_level

    def recover_ship(self, player: Player, count: int = 1):
        ship_limit = min(self.config.max_ships, self.empire_step(player.empire_level).ships)
        max_available = ship_limit - len(player.missions) - len(player.landed)
        player.available_ships = min(max_available, player.available_ships + count)

    def player_summary(self, player: Player):
        return {
            "personality": player.personality.name,
            "strategy": player.strategy,
            "energy": player.energy,
            "culture": player.culture,
            "empire_level": player.empire_level,
            "empire_vp": self.empire_vp_score(player),
            "colonies": len(player.colonies),
            "missions": [f"{mission.planet.name}:{mission.progress}/{mission.planet.track_length}" for mission in player.missions],
            "landed": [planet.name for planet in player.landed],
            "ships": player.available_ships,
            "planets": [planet.name for planet in player.colonies],
            "upgrades": [card.name for card in player.upgrades],
        }

    def game_over(self):
        if self.turn >= self.config.max_turns:
            return True
        return any(self.current_score(player) >= self.config.target_vp for player in self.players)

    def _refill_market(self):
        while len(self.upgrade_market) < self.config.upgrade_market_size and self.upgrade_deck:
            self.upgrade_market.append(self.upgrade_deck.pop())

    def _refill_planets(self):
        while len(self.planet_market) < self.planet_market_size and self.planet_deck:
            self.planet_market.append(self.planet_deck.pop())

    def return_contested_missions(self, planet: PlanetCard, except_player: Player):
        for player in self.players:
            returned = [mission for mission in player.missions if mission.planet is planet and player is not except_player]
            for mission in returned:
                player.missions.remove(mission)
                self.recover_ship(player)
            if player is not except_player:
                self.return_landed_ship(player, planet)

    def return_landed_ship(self, player: Player, planet: PlanetCard):
        if planet not in player.landed:
            return
        player.landed.remove(planet)
        self.recover_ship(player)
