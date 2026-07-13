from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass, field
from math import isqrt
from typing import Iterable, Optional

from roll_galaxy.model import DieColor, Good, PHASE_ORDER, Phase, Tile, TileKind
from roll_galaxy.tiles import HOME_WORLDS, NON_START_TILES, START_FACTION_PAIRS

from .model import PHASE_SECTION, SECTION_ORDER, SECTION_PHASE, Section
from .roll_and_sow_powers import (
    EXTRA_EXPLORE_WORKERS,
    EXTRA_SHIP_WORKERS,
    REASSIGN_RULES,
)


# The official dice specialize as shown here, but this first simulator keeps the
# face table deliberately small and inspectable. White is exact (two Explore
# faces); the colored tables preserve their printed phase biases. None denotes
# a wild face, which the automated player places in its most valuable bowl.
DIE_FACES: dict[DieColor, tuple[Optional[Section], ...]] = {
    DieColor.WHITE: (
        Section.EXPLORE,
        Section.EXPLORE,
        Section.DEVELOP,
        Section.SETTLE,
        Section.PRODUCE,
        Section.SHIP,
    ),
    DieColor.BLUE: (
        Section.EXPLORE,
        Section.DEVELOP,
        Section.PRODUCE,
        Section.PRODUCE,
        Section.SHIP,
        Section.SHIP,
    ),
    DieColor.BROWN: (
        Section.EXPLORE,
        Section.DEVELOP,
        Section.DEVELOP,
        Section.DEVELOP,
        Section.SETTLE,
        Section.SHIP,
    ),
    DieColor.RED: (
        Section.EXPLORE,
        Section.DEVELOP,
        Section.DEVELOP,
        Section.SETTLE,
        Section.SETTLE,
        Section.SETTLE,
    ),
    DieColor.GREEN: (
        Section.EXPLORE,
        Section.SETTLE,
        Section.SETTLE,
        Section.PRODUCE,
        Section.SHIP,
        None,
    ),
    DieColor.PURPLE: (
        Section.DEVELOP,
        Section.SETTLE,
        Section.PRODUCE,
        Section.SHIP,
        Section.SHIP,
        Section.SHIP,
    ),
    DieColor.YELLOW: (
        Section.DEVELOP,
        Section.SETTLE,
        Section.PRODUCE,
        None,
        None,
        None,
    ),
}


STRATEGY_BIAS: dict[str, dict[Phase, int]] = {
    "balanced": {phase: 3 for phase in PHASE_ORDER},
    "builder": {
        Phase.EXPLORE: 4,
        Phase.DEVELOP: 6,
        Phase.SETTLE: 3,
        Phase.PRODUCE: 1,
        Phase.SHIP: 2,
    },
    "settler": {
        Phase.EXPLORE: 4,
        Phase.DEVELOP: 1,
        Phase.SETTLE: 6,
        Phase.PRODUCE: 3,
        Phase.SHIP: 2,
    },
    "producer": {
        Phase.EXPLORE: 3,
        Phase.DEVELOP: 1,
        Phase.SETTLE: 3,
        Phase.PRODUCE: 6,
        Phase.SHIP: 5,
    },
    "shipper": {
        Phase.EXPLORE: 3,
        Phase.DEVELOP: 2,
        Phase.SETTLE: 2,
        Phase.PRODUCE: 4,
        Phase.SHIP: 6,
    },
}


@dataclass(frozen=True)
class RollAndSowConfig:
    starting_active_white: int = 3
    starting_reserve_white: int = 2
    starting_credits: int = 1
    construction_limit: int = 3
    explore_base_candidates: int = 4
    stock_credits: int = 2
    credit_cap: Optional[int] = None
    vp_pool_per_player: int = 7
    target_tableau_squares: int = 12
    max_rounds: int = 30
    interaction_weight: int = 2
    two_player_dummy_phase: bool = True
    solo_dummy_phase: bool = True
    solo_vp_pool: int = 24
    solo_max_rounds: int = 20
    endgame_goal_pool_extra: int = 2
    endgame_goal_penalty: int = 6
    industrial_goal_dice: int = 10


@dataclass
class SowConstruction:
    tile: Tile
    workers: list[DieColor] = field(default_factory=list)

    @property
    def progress(self) -> int:
        return len(self.workers)

    @property
    def remaining(self) -> int:
        return max(0, self.tile.cost - self.progress)


@dataclass
class RollAndSowPlayer:
    name: str
    strategy: str
    sections: dict[Section, list[DieColor]] = field(default_factory=dict)
    citizenry: list[DieColor] = field(default_factory=list)
    dev_stack: list[SowConstruction] = field(default_factory=list)
    world_stack: list[SowConstruction] = field(default_factory=list)
    tableau: list[Tile] = field(default_factory=list)
    goods: list[Good] = field(default_factory=list)
    credits: int = 1
    vp_chips: int = 0
    completed_tiles: int = 0
    shipped_goods: int = 0
    credits_earned: int = 0
    credits_spent: int = 0
    recruited_dice: int = 0
    recalled_dice: int = 0
    used_dice: int = 0
    sown_dice: int = 0
    forced_sown_dice: int = 0
    activations: int = 0
    opponent_activations: int = 0
    zero_use_activations: int = 0
    dead_rounds: int = 0
    explore_candidates_seen: int = 0
    reassigned_dice: int = 0
    power_credits: int = 0
    power_vp: int = 0
    virtual_workers: int = 0
    selected_phases: list[Phase] = field(default_factory=list)


@dataclass(frozen=True)
class RollAndSowRoundReport:
    round_number: int
    selected: tuple[Phase, ...]
    selections: dict[str, Optional[Phase]]
    used_dice: dict[str, int]
    sown_dice: dict[str, int]
    scores: dict[str, int]


class RollAndSowGame:
    """Experimental activate-use-sow Roll for the Galaxy loop.

    A selected phase activates that bowl for every player. Dice used by the
    phase follow Roll's normal lifecycle; all unused dice are sown clockwise.
    """

    def __init__(
        self,
        players: Optional[Iterable[tuple[str, str]]] = None,
        seed: Optional[int] = None,
        config: Optional[RollAndSowConfig] = None,
    ):
        self.rng = random.Random(seed)
        self.config = config or RollAndSowConfig()
        specs = list(players or (("P1", "builder"), ("P2", "producer")))
        if not 1 <= len(specs) <= 4:
            raise ValueError("roll-and-sow supports 1 to 4 players")
        self.players = [self.make_player(name, strategy) for name, strategy in specs]
        self.vp_pool = (
            self.config.solo_vp_pool
            if len(self.players) == 1
            else self.config.vp_pool_per_player * len(self.players)
        )
        self.starting_vp_pool = self.vp_pool
        self.round_number = 0
        endgame_tiles = [tile for tile in NON_START_TILES if self.is_endgame_goal(tile)]
        self.tile_bag = [tile for tile in NON_START_TILES if not self.is_endgame_goal(tile)]
        self.tile_discard: list[Tile] = []
        self.rng.shuffle(self.tile_bag)
        self.rng.shuffle(endgame_tiles)
        goal_pool_size = self.config.endgame_goal_pool_extra + len(self.players)
        self.endgame_goal_market = endgame_tiles[:goal_pool_size]
        self.extra_endgame_goals = endgame_tiles[goal_pool_size:]
        self.goal_candidates = {
            player.name: self.choose_goal_candidates(player, 2)
            for player in self.players
        }
        self.committed_goals: dict[str, list[Tile]] = {
            player.name: [] for player in self.players
        }
        self.goal_commit_round: Optional[int] = None
        self.solo_phase_deck: list[Phase] = []

        start_pairs = list(START_FACTION_PAIRS)
        home_worlds = list(HOME_WORLDS)
        self.rng.shuffle(start_pairs)
        self.rng.shuffle(home_worlds)
        for player in self.players:
            for tile in start_pairs.pop():
                self.add_start_tile(player, tile)
            self.add_start_tile(player, home_worlds.pop())
            self.add_initial_construction(player, TileKind.DEVELOPMENT)
            self.add_initial_construction(player, TileKind.WORLD)

    def make_player(self, name: str, strategy: str) -> RollAndSowPlayer:
        if strategy not in STRATEGY_BIAS:
            raise ValueError(f"unknown strategy: {strategy}")
        player = RollAndSowPlayer(
            name=name,
            strategy=strategy,
            credits=self.config.starting_credits,
            sections={section: [] for section in SECTION_ORDER},
            citizenry=[DieColor.WHITE] * self.config.starting_reserve_white,
        )
        for _ in range(self.config.starting_active_white):
            self.roll_into_bowl(player, DieColor.WHITE)
        return player

    def play(self):
        reports = []
        while not self.game_over():
            reports.append(self.play_round())
        return self.final_scores(), reports

    def play_round(self) -> RollAndSowRoundReport:
        self.round_number += 1
        before_used = {player.name: player.used_dice for player in self.players}
        before_sown = {player.name: player.sown_dice for player in self.players}
        before_completed = {player.name: player.completed_tiles for player in self.players}

        choices = {player.name: self.choose_section(player) for player in self.players}
        for player in self.players:
            selected_section = choices[player.name]
            if selected_section is not None:
                self.apply_reassign_powers(player, selected_section)
        selections = {
            name: SECTION_PHASE[section] if section is not None else None
            for name, section in choices.items()
        }
        selected_set = {
            selected_phase for selected_phase in selections.values() if selected_phase is not None
        }
        if len(self.players) == 2 and self.config.two_player_dummy_phase:
            selected_set.add(self.roll_two_player_phase())
        if len(self.players) == 1 and self.config.solo_dummy_phase:
            selected_set.add(self.draw_solo_phase())
        selected = tuple(phase for phase in PHASE_ORDER if phase in selected_set)
        for player in self.players:
            own = selections[player.name]
            if own is not None:
                player.selected_phases.append(own)

        for phase in selected:
            for player in self.players:
                self.activate_phase(player, phase, selected_by_player=selections[player.name] is phase)

        for player in self.players:
            if (
                player.used_dice == before_used[player.name]
                and player.completed_tiles == before_completed[player.name]
            ):
                player.dead_rounds += 1
            self.manage_empire(player)
        self.maybe_commit_goals()

        return RollAndSowRoundReport(
            round_number=self.round_number,
            selected=selected,
            selections=selections,
            used_dice={player.name: player.used_dice - before_used[player.name] for player in self.players},
            sown_dice={player.name: player.sown_dice - before_sown[player.name] for player in self.players},
            scores={player.name: self.score(player) for player in self.players},
        )

    def roll_two_player_phase(self) -> Phase:
        section = self.rng.choice(DIE_FACES[DieColor.WHITE])
        if section is None:
            section = self.rng.choice(SECTION_ORDER)
        return SECTION_PHASE[section]

    def draw_solo_phase(self) -> Phase:
        if not self.solo_phase_deck:
            self.solo_phase_deck = list(PHASE_ORDER)
            self.rng.shuffle(self.solo_phase_deck)
        return self.solo_phase_deck.pop()

    def choose_section(self, player: RollAndSowPlayer) -> Optional[Section]:
        choices = [section for section in SECTION_ORDER if player.sections[section]]
        if not choices:
            return None
        return max(choices, key=lambda section: self.selection_value(player, section))

    def selection_value(self, player: RollAndSowPlayer, section: Section) -> tuple[int, int]:
        phase = SECTION_PHASE[section]
        useful = self.useful_dice_count(player, phase)
        dice = len(player.sections[section])
        opponent_benefit = sum(
            min(len(other.sections[section]), self.useful_dice_count(other, phase))
            for other in self.players
            if other is not player
        )
        value = (
            STRATEGY_BIAS[player.strategy][phase]
            + useful * 8
            + min(dice, useful) * 3
            + max(0, dice - useful)
            - opponent_benefit * self.config.interaction_weight
        )
        return value, -SECTION_ORDER.index(section)

    def apply_reassign_powers(self, player: RollAndSowPlayer, selected: Section):
        """Route printed Reassign dice into the selected bowl before reveal.

        The spreadsheet's source-color and destination restrictions are
        retained where they map cleanly to bowls. Backup Planning remains the
        same one-route approximation used by the battery simulator because its
        printed effect augments Dictate rather than directly moving a worker.
        """
        for tile in player.tableau:
            rule = REASSIGN_RULES.get(tile.id)
            if rule is None:
                continue
            if rule.destinations is not None and selected not in rule.destinations:
                continue
            count = rule.count
            if tile.id == "mad_scientists" and self.has_unique_most_novelty_worlds(player):
                count = 2
            for _ in range(count):
                source = self.best_reassign_source(player, selected, rule)
                if source is None:
                    break
                die = self.take_reassign_die(player, source, rule)
                if die is None:
                    break
                player.sections[selected].append(die)
                player.reassigned_dice += 1

    def best_reassign_source(self, player, selected, rule):
        candidates = []
        for section in SECTION_ORDER:
            if section is selected or not player.sections[section]:
                continue
            if rule.source_section is not None and section is not rule.source_section:
                continue
            if rule.colors is not None and not any(die in rule.colors for die in player.sections[section]):
                continue
            candidates.append(section)
        if not candidates:
            return None
        return min(
            candidates,
            key=lambda section: (
                STRATEGY_BIAS[player.strategy][SECTION_PHASE[section]],
                -len(player.sections[section]),
            ),
        )

    def take_reassign_die(self, player, source, rule):
        dice = player.sections[source]
        if rule.colors is None:
            return dice.pop()
        index = next((index for index, die in enumerate(dice) if die in rule.colors), None)
        if index is None:
            return None
        return dice.pop(index)

    def has_unique_most_novelty_worlds(self, player: RollAndSowPlayer) -> bool:
        counts = [
            sum(1 for tile in other.tableau if "novelty" in tile.tags)
            for other in self.players
        ]
        own = sum(1 for tile in player.tableau if "novelty" in tile.tags)
        return counts.count(own) == 1 and own == max(counts, default=0)

    def useful_dice_count(self, player: RollAndSowPlayer, phase: Phase) -> int:
        available = len(player.sections[PHASE_SECTION[phase]])
        if phase is Phase.EXPLORE:
            open_slots = (
                self.config.construction_limit - len(player.dev_stack)
                + self.config.construction_limit - len(player.world_stack)
            )
            can_stock = self.config.credit_cap is None or player.credits < self.config.credit_cap
            return min(available, 1 if open_slots > 0 else int(can_stock))
        if phase is Phase.DEVELOP:
            return min(available, sum(self.build_remaining(player, build) for build in player.dev_stack))
        if phase is Phase.SETTLE:
            return min(available, sum(self.build_remaining(player, build) for build in player.world_stack))
        if phase is Phase.PRODUCE:
            return min(available, len(self.empty_production_worlds(player)))
        if phase is Phase.SHIP:
            return min(available, len(player.goods))
        return 0

    def activate_phase(self, player: RollAndSowPlayer, phase: Phase, selected_by_player: bool = False):
        section = PHASE_SECTION[phase]
        dice = list(player.sections[section])
        player.sections[section] = []
        if dice:
            player.activations += 1
            if not selected_by_player:
                player.opponent_activations += 1

        if phase is Phase.EXPLORE:
            used, leftovers = self.activate_explore(player, dice)
        elif phase is Phase.DEVELOP:
            used, leftovers = self.activate_build(player, dice, TileKind.DEVELOPMENT)
        elif phase is Phase.SETTLE:
            used, leftovers = self.activate_build(player, dice, TileKind.WORLD)
        elif phase is Phase.PRODUCE:
            used, leftovers = self.activate_produce(player, dice)
        elif phase is Phase.SHIP:
            used, leftovers = self.activate_ship(player, dice)
        else:
            raise ValueError(f"unknown phase: {phase}")

        player.used_dice += used
        if dice and used == 0:
            player.zero_use_activations += 1
        self.apply_phase_end_powers(player, phase)
        if not selected_by_player:
            player.forced_sown_dice += len(leftovers)
        self.sow_leftovers(player, section, leftovers)

    def activate_explore(self, player: RollAndSowPlayer, dice: list[DieColor]):
        virtual = sum(
            amount
            for tile_id, amount in EXTRA_EXPLORE_WORKERS.items()
            if self.has_tile(player, tile_id)
        )
        player.virtual_workers += virtual
        if dice and self.should_take_extra_goal(player):
            explorer = dice.pop(0)
            self.take_extra_goal(player)
            player.citizenry.append(explorer)
            return 1, dice
        dev_open = len(player.dev_stack) < self.config.construction_limit
        world_open = len(player.world_stack) < self.config.construction_limit
        if not dev_open and not world_open:
            if not dice:
                if virtual:
                    self.gain_power_credits(player, self.config.stock_credits * virtual)
                return 0, []
            yellow_index = next((index for index, die in enumerate(dice) if die is DieColor.YELLOW), None)
            if self.has_tile(player, "alien_archeology") and yellow_index is not None:
                die = dice.pop(yellow_index)
                self.gain_power_credits(player, 4)
            else:
                die = dice.pop(0)
                self.gain_credits(player, self.config.stock_credits)
            if virtual:
                self.gain_power_credits(player, self.config.stock_credits * virtual)
            player.citizenry.append(die)
            return 1, dice

        if not dice and virtual <= 0:
            return 0, []

        kind = self.explore_kind(player, dev_open, world_open)
        # Base four makes one explorer useful. Builder/settler specialists spend
        # a second die when available to improve the candidate set.
        depth = 1
        if len(dice) > 1 and player.strategy in {"builder", "settler"}:
            depth = 2
        used_dice = dice[:depth]
        leftovers = dice[depth:]
        keep_count = 2 if self.has_tile(player, "alien_research_team") else 1
        self.scout(player, kind, depth, virtual_workers=virtual, keep_count=keep_count)
        if (
            self.has_tile(player, "alien_research_team")
            and (
                DieColor.YELLOW in used_dice
                or self.has_tile(player, "alien_research_ship")
            )
        ):
            self.gain_power_credits(player, 1)
        player.citizenry.extend(used_dice)
        return len(used_dice), leftovers

    def explore_kind(self, player: RollAndSowPlayer, dev_open: bool, world_open: bool) -> TileKind:
        if dev_open and world_open:
            if len(player.dev_stack) < len(player.world_stack):
                return TileKind.DEVELOPMENT
            if len(player.world_stack) < len(player.dev_stack):
                return TileKind.WORLD
            return TileKind.DEVELOPMENT if player.strategy == "builder" else TileKind.WORLD
        return TileKind.DEVELOPMENT if dev_open else TileKind.WORLD

    def activate_build(
        self,
        player: RollAndSowPlayer,
        dice: list[DieColor],
        kind: TileKind,
    ):
        stack = player.dev_stack if kind is TileKind.DEVELOPMENT else player.world_stack
        remaining = list(dice)
        used = 0
        while stack:
            build = min(
                stack,
                key=lambda item: (self.build_remaining(player, item), -self.tile_value(player, item.tile)),
            )
            while remaining and self.build_remaining(player, build) > 0:
                build.workers.append(remaining.pop(0))
                used += 1
            if self.build_remaining(player, build) > 0:
                break
            stack.remove(build)
            player.citizenry.extend(build.workers)
            self.complete_tile(player, build.tile)
            if not remaining:
                break
        return used, remaining

    def activate_produce(self, player: RollAndSowPlayer, dice: list[DieColor]):
        remaining = list(dice)
        used = 0
        for world in self.empty_production_worlds(player):
            if not remaining:
                break
            producer = remaining.pop(0)
            player.goods.append(Good(world, producer))
            used += 1
        return used, remaining

    def activate_ship(self, player: RollAndSowPlayer, dice: list[DieColor]):
        remaining = list(dice)
        used = 0
        while remaining and player.goods:
            shipper = remaining.pop(0)
            self.ship_one_good(player, shipper)
            used += 1
        virtual = sum(
            amount
            for tile_id, amount in EXTRA_SHIP_WORKERS.items()
            if self.has_tile(player, tile_id)
        )
        player.virtual_workers += virtual
        while virtual > 0 and player.goods:
            self.ship_one_good(player, None)
            virtual -= 1
        return used, remaining

    def build_remaining(self, player: RollAndSowPlayer, build: SowConstruction) -> int:
        return max(0, self.effective_build_cost(player, build.tile) - build.progress)

    def effective_build_cost(self, player: RollAndSowPlayer, tile: Tile) -> int:
        cost = tile.cost
        if tile.kind is TileKind.DEVELOPMENT:
            if self.has_tile(player, "investment_credits"):
                cost -= 1
            if self.has_tile(player, "bilogical_adaptation") and "reassign" in tile.tags:
                cost -= 1
            return max(1, cost)

        if self.has_tile(player, "alien_uplift_blueprints") and (
            "genes" in tile.tags or "alien_technology" in tile.tags
        ):
            cost -= 1
        if self.has_tile(player, "free_trade_zone") and "gray" in tile.tags:
            cost = max(2, cost - 2)
        if self.has_tile(player, "replicant_robots"):
            cost -= 1
        return max(1, cost)

    def ship_one_good(
        self,
        player: RollAndSowPlayer,
        shipper: Optional[DieColor],
    ):
        good = self.best_good_to_ship(player)
        player.goods.remove(good)
        trading = player.credits <= 2
        if trading:
            self.gain_credits(player, self.trade_value(good.world))
            self.apply_trade_powers(player, good)
        else:
            self.gain_vp(player, 1)
            self.apply_consume_powers(player, good)
        if shipper is not None:
            player.citizenry.append(shipper)
        player.citizenry.append(good.color)
        player.shipped_goods += 1

    def apply_trade_powers(self, player: RollAndSowPlayer, good: Good):
        bonus = 0
        if self.has_tile(player, "export_duties"):
            bonus += 1
        if self.has_tile(player, "galactic_demand") and "novelty" in good.world.tags:
            bonus += 2
        if self.has_tile(player, "jumpdrive_research") and "rare_elemental" in good.world.tags:
            bonus += 1
        if bonus:
            self.gain_power_credits(player, bonus)

    def apply_consume_powers(self, player: RollAndSowPlayer, good: Good):
        bonus_vp = 0
        bonus_credits = 0
        if self.has_tile(player, "minor_research_labs") and (
            "genes" in good.world.tags or "alien_technology" in good.world.tags
        ):
            bonus_vp += 1
        if self.has_tile(player, "space_refineries") and "rare_elemental" in good.world.tags:
            bonus_vp += 1
        if self.has_tile(player, "trade_levies"):
            bonus_credits += 1
        if self.has_tile(player, "mining_industry") and "rare_elemental" in good.world.tags:
            bonus_credits += 1
        if bonus_vp:
            self.gain_power_vp(player, bonus_vp)
        if bonus_credits:
            self.gain_power_credits(player, bonus_credits)

    def apply_phase_end_powers(self, player: RollAndSowPlayer, phase: Phase):
        credits = 0
        vp = 0
        if phase is Phase.DEVELOP:
            if self.has_tile(player, "galactic_investors"):
                credits += 2
            if self.has_tile(player, "galactic_religion"):
                credits += sum(1 for die in player.citizenry if die is DieColor.BLUE)
        elif phase is Phase.SETTLE:
            if self.has_tile(player, "robot_surveyors"):
                credits += 2
        elif phase is Phase.PRODUCE:
            if self.has_tile(player, "consumer_markets"):
                credits += sum(1 for good in player.goods if "novelty" in good.world.tags)
            if self.has_tile(player, "genetics_lab"):
                credits += 2 * sum(1 for good in player.goods if good.color is DieColor.GREEN)
        elif phase is Phase.SHIP:
            if self.has_tile(player, "merchant_guild"):
                credits += 2
            if self.has_tile(player, "space_piracy"):
                military = sum(1 for die in player.citizenry if die is DieColor.RED)
                credits += (military + 1) // 2
            if self.has_tile(player, "space_tourism"):
                credits += 1
                if self.has_highest_cost_world(player):
                    credits += 1
            if self.has_tile(player, "galactic_salon"):
                vp += 1
        if phase in {Phase.EXPLORE, Phase.SHIP} and self.has_tile(player, "technology_unions"):
            if self.has_unique_most_developments(player):
                credits += 1
        if credits:
            self.gain_power_credits(player, credits)
        if vp:
            self.gain_power_vp(player, vp)

    def has_unique_most_developments(self, player: RollAndSowPlayer) -> bool:
        counts = [
            sum(1 for tile in other.tableau if tile.kind is TileKind.DEVELOPMENT)
            for other in self.players
        ]
        own = sum(1 for tile in player.tableau if tile.kind is TileKind.DEVELOPMENT)
        return counts.count(own) == 1 and own == max(counts, default=0)

    def has_highest_cost_world(self, player: RollAndSowPlayer) -> bool:
        own = max(
            (tile.cost for tile in player.tableau if tile.kind is TileKind.WORLD),
            default=-1,
        )
        highest = max(
            (
                tile.cost
                for other in self.players
                for tile in other.tableau
                if tile.kind is TileKind.WORLD
            ),
            default=-1,
        )
        return own == highest

    def sow_leftovers(
        self,
        player: RollAndSowPlayer,
        source: Section,
        dice: list[DieColor],
    ):
        start = SECTION_ORDER.index(source) + 1
        for offset, die in enumerate(dice):
            destination = SECTION_ORDER[(start + offset) % len(SECTION_ORDER)]
            player.sections[destination].append(die)
        player.sown_dice += len(dice)

    def manage_empire(self, player: RollAndSowPlayer):
        recruit_count = min(player.credits, len(player.citizenry))
        for _ in range(recruit_count):
            die = max(player.citizenry, key=lambda color: self.recruit_value(player, color))
            player.citizenry.remove(die)
            player.credits -= 1
            player.credits_spent += 1
            player.recruited_dice += 1
            self.roll_into_bowl(player, die)
        if player.credits == 0:
            player.credits = 1
        if not any(player.sections[section] for section in SECTION_ORDER):
            self.recall_one_die(player)

    def recall_one_die(self, player: RollAndSowPlayer) -> bool:
        builds = [
            build
            for build in (*player.dev_stack, *player.world_stack)
            if build.workers
        ]
        if builds:
            build = max(builds, key=lambda item: item.progress)
            die = build.workers.pop()
        elif player.goods:
            die = player.goods.pop().color
        else:
            return False
        self.roll_into_bowl(player, die)
        player.recalled_dice += 1
        return True

    def recruit_value(self, player: RollAndSowPlayer, color: DieColor) -> int:
        native = {
            DieColor.BLUE: Phase.EXPLORE,
            DieColor.BROWN: Phase.DEVELOP,
            DieColor.RED: Phase.SETTLE,
            DieColor.GREEN: Phase.PRODUCE,
            DieColor.PURPLE: Phase.SHIP,
        }.get(color)
        return STRATEGY_BIAS[player.strategy].get(native, 3) + int(color is DieColor.YELLOW) * 2

    def roll_into_bowl(
        self,
        player: RollAndSowPlayer,
        color: DieColor,
        forced_section: Optional[Section] = None,
    ) -> Section:
        section = forced_section
        if section is None:
            section = self.rng.choice(DIE_FACES[color])
        if section is None:
            section = self.best_wild_section(player)
        player.sections[section].append(color)
        return section

    def best_wild_section(self, player: RollAndSowPlayer) -> Section:
        return max(
            SECTION_ORDER,
            key=lambda section: (
                STRATEGY_BIAS[player.strategy][SECTION_PHASE[section]],
                -len(player.sections[section]),
            ),
        )

    def add_start_tile(self, player: RollAndSowPlayer, tile: Tile):
        player.tableau.append(tile)
        self.apply_tile_effects(player, tile)

    def complete_tile(self, player: RollAndSowPlayer, tile: Tile):
        player.tableau.append(tile)
        player.completed_tiles += 1
        self.apply_tile_effects(player, tile)
        self.apply_completion_powers(player, tile)

    def apply_completion_powers(self, player: RollAndSowPlayer, tile: Tile):
        credits = 0
        if tile.kind is TileKind.DEVELOPMENT:
            if tile.id != "public_works" and self.has_tile(player, "public_works"):
                credits += 1
            if tile.id != "galactic_recycling" and self.has_tile(player, "galactic_recycling"):
                credits += 1
        else:
            if self.has_tile(player, "galactic_recycling"):
                credits += 1
            if self.has_tile(player, "terraforming_robots"):
                credits += 1
                if "rare_elemental" in tile.tags:
                    credits += 1
        if credits:
            self.gain_power_credits(player, credits)

    def apply_tile_effects(self, player: RollAndSowPlayer, tile: Tile):
        for _ in range(tile.die_loss):
            self.lose_die(player)
        for color in tile.grants:
            self.gain_die(player, color, tile.placement, tile)
        if tile.immediate_credits:
            self.gain_credits(player, tile.immediate_credits)

    def gain_die(
        self,
        player: RollAndSowPlayer,
        color: DieColor,
        placement: str = "cup",
        world: Optional[Tile] = None,
    ):
        normalized = placement.strip().lower()
        if normalized == "world" and world is not None and not self.world_has_good(player, world):
            player.goods.append(Good(world, color))
        elif normalized == "citizenry":
            player.citizenry.append(color)
        else:
            self.roll_into_bowl(player, color)

    def lose_die(self, player: RollAndSowPlayer) -> bool:
        if player.citizenry:
            player.citizenry.pop()
            return True
        for section in reversed(SECTION_ORDER):
            if player.sections[section]:
                player.sections[section].pop()
                return True
        if player.goods:
            player.goods.pop()
            return True
        for stack in (player.dev_stack, player.world_stack):
            for build in stack:
                if build.workers:
                    build.workers.pop()
                    return True
        return False

    def add_initial_construction(self, player: RollAndSowPlayer, kind: TileKind):
        candidates = self.draw_candidates(kind, 1)
        if not candidates:
            return
        build = SowConstruction(candidates[0])
        (player.dev_stack if kind is TileKind.DEVELOPMENT else player.world_stack).append(build)

    def scout(
        self,
        player: RollAndSowPlayer,
        kind: TileKind,
        dice_spent: int,
        virtual_workers: int = 0,
        keep_count: int = 1,
    ) -> Optional[Tile]:
        count = (
            self.config.explore_base_candidates
            + max(0, dice_spent - 1)
            + virtual_workers
        )
        candidates = self.draw_candidates(kind, count)
        player.explore_candidates_seen += len(candidates)
        if not candidates:
            return None
        stack = player.dev_stack if kind is TileKind.DEVELOPMENT else player.world_stack
        available_slots = max(0, self.config.construction_limit - len(stack))
        keep_count = min(keep_count, available_slots, len(candidates))
        chosen_tiles = sorted(
            candidates,
            key=lambda tile: self.tile_value(player, tile),
            reverse=True,
        )[:keep_count]
        for chosen in chosen_tiles:
            candidates.remove(chosen)
            stack.append(SowConstruction(chosen))
        self.tile_discard.extend(candidates)
        return chosen_tiles[0] if chosen_tiles else None

    def draw_candidates(self, kind: TileKind, count: int) -> list[Tile]:
        drawn: list[Tile] = []
        while len(drawn) < count:
            index = next((i for i, tile in enumerate(self.tile_bag) if tile.kind is kind), None)
            if index is None:
                if not self.tile_discard:
                    break
                self.tile_bag.extend(self.tile_discard)
                self.tile_discard.clear()
                self.rng.shuffle(self.tile_bag)
                continue
            drawn.append(self.tile_bag.pop(index))
        return drawn

    def tile_value(self, player: RollAndSowPlayer, tile: Tile) -> int:
        value = tile.vp + len(tile.grants) * 3 + tile.immediate_credits
        if "reassign" in tile.tags:
            value += 4
        for tag, phase in (
            ("phase_i", Phase.EXPLORE),
            ("phase_ii", Phase.DEVELOP),
            ("phase_iii", Phase.SETTLE),
            ("phase_iv", Phase.PRODUCE),
            ("phase_v", Phase.SHIP),
        ):
            if tag in tile.tags:
                value += max(1, STRATEGY_BIAS[player.strategy][phase] - 1)
        if player.strategy == "builder":
            value += int(tile.kind is TileKind.DEVELOPMENT) * 8
        elif player.strategy == "settler":
            value += int(tile.kind is TileKind.WORLD) * 8
        elif player.strategy == "producer":
            value += int(tile.produces) * 10
            value += int(DieColor.GREEN in tile.grants) * 4
        elif player.strategy == "shipper":
            value += int(tile.produces) * 6
            value += int(DieColor.PURPLE in tile.grants) * 6
        return value - tile.cost

    def empty_production_worlds(self, player: RollAndSowPlayer) -> list[Tile]:
        occupied = {good.world.id for good in player.goods}
        return [
            tile
            for tile in player.tableau
            if tile.kind is TileKind.WORLD
            and tile.produces
            and "gray" not in tile.tags
            and tile.id not in occupied
        ]

    def world_has_good(self, player: RollAndSowPlayer, world: Tile) -> bool:
        return any(good.world.id == world.id for good in player.goods)

    def best_good_to_ship(self, player: RollAndSowPlayer) -> Good:
        if player.credits <= 2:
            return max(player.goods, key=lambda good: self.trade_value(good.world))
        return player.goods[0]

    def trade_value(self, world: Tile) -> int:
        color = world.world_color.strip().lower()
        if "alien" in color:
            return 6
        if "genes" in color:
            return 5
        if "rare" in color:
            return 4
        if "novelty" in color:
            return 3
        return 1

    def gain_credits(self, player: RollAndSowPlayer, amount: int):
        before = player.credits
        player.credits += amount
        if self.config.credit_cap is not None:
            player.credits = min(self.config.credit_cap, player.credits)
        player.credits_earned += player.credits - before

    def gain_power_credits(self, player: RollAndSowPlayer, amount: int):
        before = player.credits
        self.gain_credits(player, amount)
        player.power_credits += player.credits - before

    def gain_vp(self, player: RollAndSowPlayer, amount: int):
        gained = min(amount, self.vp_pool)
        player.vp_chips += gained
        self.vp_pool -= gained

    def gain_power_vp(self, player: RollAndSowPlayer, amount: int):
        before = player.vp_chips
        self.gain_vp(player, amount)
        player.power_vp += player.vp_chips - before

    def has_tile(self, player: RollAndSowPlayer, tile_id: str) -> bool:
        return any(tile.id == tile_id for tile in player.tableau)

    def is_endgame_goal(self, tile: Tile) -> bool:
        return tile.kind is TileKind.DEVELOPMENT and "end_game" in tile.tags

    def goal_strategy_value(self, player: RollAndSowPlayer, tile: Tile) -> int:
        preferred = {
            "balanced": {
                "galactic_exchange",
                "galactic_renaissance",
                "system_diversification",
            },
            "builder": {
                "galactic_federation",
                "galactic_renaissance",
                "system_diversification",
            },
            "settler": {
                "free_trade_association",
                "galactic_exchange",
                "mining_league",
                "new_galactic_order",
            },
            "producer": {
                "free_trade_association",
                "galactic_reserves",
                "new_economy",
            },
            "shipper": {
                "galactic_bankers",
                "galactic_renaissance",
                "new_economy",
            },
        }
        return 12 if tile.id in preferred[player.strategy] else 0

    def choose_goal_candidates(self, player: RollAndSowPlayer, count: int) -> list[Tile]:
        ranked = sorted(
            self.endgame_goal_market,
            key=lambda tile: (self.goal_strategy_value(player, tile), tile.name),
            reverse=True,
        )
        return ranked[:count]

    def should_take_extra_goal(self, player: RollAndSowPlayer) -> bool:
        if not self.extra_endgame_goals:
            return False
        owned = len(
            {
                goal.id
                for goal in (
                    *self.goal_candidates.get(player.name, ()),
                    *self.committed_goals.get(player.name, ()),
                )
            }
        )
        if owned >= 3:
            return False
        if self.goal_commit_round is None:
            return player.strategy == "builder" and len(player.dev_stack) >= self.config.construction_limit
        best = max(self.extra_endgame_goals, key=lambda tile: self.goal_choice_value(player, tile))
        return self.endgame_goal_fulfilled(player, best)

    def take_extra_goal(self, player: RollAndSowPlayer) -> Optional[Tile]:
        if not self.extra_endgame_goals:
            return None
        goal = max(
            self.extra_endgame_goals,
            key=lambda tile: self.goal_choice_value(player, tile),
        )
        self.extra_endgame_goals.remove(goal)
        if self.goal_commit_round is None:
            self.goal_candidates[player.name].append(goal)
        else:
            self.committed_goals[player.name].append(goal)
        return goal

    def goal_choice_value(self, player: RollAndSowPlayer, tile: Tile) -> tuple[int, int, int]:
        progress, required, _label = self.endgame_goal_requirement(player, tile)
        fit = progress * 100 // max(1, required)
        return (
            int(progress >= required),
            fit + self.goal_strategy_value(player, tile),
            self.endgame_tile_bonus(player, tile),
        )

    def maybe_commit_goals(self, force: bool = False):
        if self.goal_commit_round is not None:
            return
        if not force and (
            self.vp_pool > self.starting_vp_pool // 2
            and all(player.completed_tiles < 6 for player in self.players)
        ):
            return
        self.goal_commit_round = self.round_number
        for player in self.players:
            candidates = self.goal_candidates.get(player.name, [])
            if not candidates:
                continue
            chosen = max(candidates, key=lambda tile: self.goal_choice_value(player, tile))
            self.committed_goals[player.name] = [chosen]
            self.goal_candidates[player.name] = [chosen]

    def endgame_goal_score(self, player: RollAndSowPlayer) -> int:
        total = 0
        for goal in self.committed_goals.get(player.name, ()):
            if self.endgame_goal_fulfilled(player, goal):
                total += self.endgame_tile_bonus(player, goal)
            else:
                total -= self.config.endgame_goal_penalty
        return total

    def endgame_goal_fulfilled(self, player: RollAndSowPlayer, tile: Tile) -> bool:
        progress, required, _label = self.endgame_goal_requirement(player, tile)
        return progress >= required

    def endgame_goal_requirement(
        self,
        player: RollAndSowPlayer,
        tile: Tile,
    ) -> tuple[int, int, str]:
        worlds = [card for card in player.tableau if card.kind is TileKind.WORLD]
        developments = [
            card for card in player.tableau if card.kind is TileKind.DEVELOPMENT
        ]
        world_colors = {
            world.world_color.strip().lower()
            for world in worlds
            if world.world_color.strip()
        }
        inventory = self.inventory(player)
        if tile.id == "free_trade_association":
            return sum("novelty" in world.tags for world in worlds), 2, "Novelty"
        if tile.id == "galactic_bankers":
            return player.shipped_goods, 4, "Satisfied Populace"
        if tile.id == "galactic_exchange":
            return sum("alien_technology" in world.tags for world in worlds), 1, "Alien Contact"
        if tile.id == "galactic_federation":
            return len(developments), 4, "Developer"
        if tile.id == "galactic_renaissance":
            return player.completed_tiles, 8, "Builder"
        if tile.id == "galactic_reserves":
            return sum(inventory.values()), self.config.industrial_goal_dice, "Industrial"
        if tile.id == "mining_league":
            return sum("rare_elemental" in world.tags for world in worlds), 2, "Rare Elements"
        if tile.id == "new_economy":
            return sum(world.produces for world in worlds), 3, "Production"
        if tile.id == "new_galactic_order":
            return inventory[DieColor.RED], 5, "Military"
        if tile.id == "system_diversification":
            return len(world_colors), 4, "Diverse"
        return self.endgame_tile_bonus(player, tile), 1, "printed bonus"

    def endgame_tile_bonus(self, player: RollAndSowPlayer, tile: Tile) -> int:
        if not self.is_endgame_goal(tile):
            return 0
        worlds = [card for card in player.tableau if card.kind is TileKind.WORLD]
        developments = [
            card for card in player.tableau if card.kind is TileKind.DEVELOPMENT
        ]
        inventory = self.inventory(player)
        if tile.id == "free_trade_association":
            total_cost = sum(world.cost for world in worlds if "novelty" in world.tags)
            return (total_cost + 1) // 2
        if tile.id == "galactic_bankers":
            return len(developments) + 1
        if tile.id == "galactic_exchange":
            return sum(count > 0 for count in inventory.values())
        if tile.id == "galactic_federation":
            total_cost = sum(card.cost for card in developments) + tile.cost
            return (total_cost + 2) // 3
        if tile.id == "galactic_renaissance":
            return (isqrt(8 * player.vp_chips + 1) - 1) // 2
        if tile.id == "galactic_reserves":
            return len(player.goods)
        if tile.id == "mining_league":
            return 2 * sum("rare_elemental" in world.tags for world in worlds)
        if tile.id == "new_economy":
            return 1 + sum("reassign" not in card.tags for card in developments)
        if tile.id == "new_galactic_order":
            red_dice = inventory[DieColor.RED]
            return 2 * ((red_dice + 2) // 3)
        if tile.id == "system_diversification":
            reassign_cost = tile.cost + sum(
                card.cost for card in developments if "reassign" in card.tags
            )
            return (reassign_cost + 1) // 2
        return 0

    def goal_requirement_summary(self, player: RollAndSowPlayer):
        summary = {}
        for goal in self.committed_goals.get(player.name, ()):
            progress, required, label = self.endgame_goal_requirement(player, goal)
            summary[goal.name] = {
                "progress": progress,
                "required": required,
                "label": label,
                "fulfilled": progress >= required,
                "bonus": self.endgame_tile_bonus(player, goal),
            }
        return summary

    def game_over(self) -> bool:
        round_limit = (
            self.config.solo_max_rounds
            if len(self.players) == 1
            else self.config.max_rounds
        )
        if self.round_number >= round_limit:
            return True
        if self.vp_pool <= 0:
            return True
        return any(len(player.tableau) >= self.config.target_tableau_squares for player in self.players)

    def score(self, player: RollAndSowPlayer) -> int:
        return (
            sum(tile.vp for tile in player.tableau)
            + player.vp_chips
            + self.endgame_goal_score(player)
        )

    def inventory(self, player: RollAndSowPlayer) -> Counter:
        dice = Counter(player.citizenry)
        for section_dice in player.sections.values():
            dice.update(section_dice)
        for build in (*player.dev_stack, *player.world_stack):
            dice.update(build.workers)
        dice.update(good.color for good in player.goods)
        return dice

    def player_summary(self, player: RollAndSowPlayer):
        construction_dice = sum(
            build.progress for build in (*player.dev_stack, *player.world_stack)
        )
        return {
            "strategy": player.strategy,
            "rounds": self.round_number,
            "score": self.score(player),
            "tableau": len(player.tableau),
            "completed_tiles": player.completed_tiles,
            "credits": player.credits,
            "vp_chips": player.vp_chips,
            "goods": len(player.goods),
            "owned_dice": sum(self.inventory(player).values()),
            "bowl_dice": sum(len(dice) for dice in player.sections.values()),
            "citizenry_dice": len(player.citizenry),
            "construction_dice": construction_dice,
            "used_dice": player.used_dice,
            "sown_dice": player.sown_dice,
            "forced_sown_dice": player.forced_sown_dice,
            "activations": player.activations,
            "opponent_activations": player.opponent_activations,
            "zero_use_activations": player.zero_use_activations,
            "dead_rounds": player.dead_rounds,
            "recruited_dice": player.recruited_dice,
            "recalled_dice": player.recalled_dice,
            "credits_earned": player.credits_earned,
            "credits_spent": player.credits_spent,
            "shipped_goods": player.shipped_goods,
            "explore_candidates_seen": player.explore_candidates_seen,
            "reassigned_dice": player.reassigned_dice,
            "power_credits": player.power_credits,
            "power_vp": player.power_vp,
            "virtual_workers": player.virtual_workers,
            "goal_candidates": [
                tile.name for tile in self.goal_candidates.get(player.name, ())
            ],
            "committed_goals": [
                tile.name for tile in self.committed_goals.get(player.name, ())
            ],
            "goal_requirements": self.goal_requirement_summary(player),
            "goal_score": self.endgame_goal_score(player),
            "goal_commit_round": self.goal_commit_round,
            "sections": {
                section.value: len(player.sections[section])
                for section in SECTION_ORDER
            },
        }

    def final_scores(self):
        self.maybe_commit_goals(force=True)
        return sorted(
            (
                (player.name, self.score(player), self.player_summary(player))
                for player in self.players
            ),
            key=lambda item: item[1],
            reverse=True,
        )


__all__ = [
    "DIE_FACES",
    "RollAndSowConfig",
    "RollAndSowGame",
    "RollAndSowPlayer",
    "RollAndSowRoundReport",
    "SowConstruction",
]
