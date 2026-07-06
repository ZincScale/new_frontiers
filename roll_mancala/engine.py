from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, Optional

from roll_galaxy.tiles import HOME_WORLDS, NON_START_TILES, START_FACTION_PAIRS

from .model import (
    COLOR_SECTION,
    PHASE_ORDER,
    PHASE_SECTION,
    SECTION_ORDER,
    SECTION_PHASE,
    Construction,
    DieColor,
    Good,
    Phase,
    Player,
    Section,
    SourceChoice,
    SowResult,
    Tile,
    TileKind,
)


STRATEGY_BIAS: dict[str, dict[Phase, int]] = {
    "balanced": {
        Phase.EXPLORE: 3,
        Phase.DEVELOP: 3,
        Phase.SETTLE: 3,
        Phase.PRODUCE: 3,
        Phase.SHIP: 3,
    },
    "builder": {
        Phase.EXPLORE: 3,
        Phase.DEVELOP: 6,
        Phase.SETTLE: 3,
        Phase.PRODUCE: 1,
        Phase.SHIP: 2,
    },
    "settler": {
        Phase.EXPLORE: 3,
        Phase.DEVELOP: 1,
        Phase.SETTLE: 6,
        Phase.PRODUCE: 2,
        Phase.SHIP: 2,
    },
    "producer": {
        Phase.EXPLORE: 2,
        Phase.DEVELOP: 1,
        Phase.SETTLE: 2,
        Phase.PRODUCE: 6,
        Phase.SHIP: 5,
    },
    "shipper": {
        Phase.EXPLORE: 2,
        Phase.DEVELOP: 2,
        Phase.SETTLE: 1,
        Phase.PRODUCE: 4,
        Phase.SHIP: 6,
    },
}


@dataclass(frozen=True)
class MancalaConfig:
    section_cap: int = 6
    starting_per_phase: int = 2
    starting_white: int = 2
    starting_yellow: int = 0
    starting_credits: int = 1
    credit_cap: int = 10
    recovery_sow_cost: int = 2
    conservative_bonus: bool = False
    selected_phase_benefits: bool = False
    dummy_phase_count: int = 0
    target_tableau_squares: int = 12
    vp_pool_per_player: int = 11
    max_rounds: int = 50


@dataclass(frozen=True)
class RoundReport:
    round_number: int
    selected: tuple[Phase, ...]
    selections: dict[str, Optional[Phase]]
    dummy_phases: tuple[Phase, ...]
    used_workers: dict[str, int]
    scores: dict[str, int]


class MancalaGame:
    def __init__(
        self,
        players: Optional[Iterable[tuple[str, str]]] = None,
        seed: Optional[int] = None,
        config: Optional[MancalaConfig] = None,
    ):
        self.rng = random.Random(seed)
        self.config = config or MancalaConfig()
        specs = list(players or [("P1", "builder"), ("P2", "producer")])
        self.players = [self.make_player(name, strategy) for name, strategy in specs]
        self.vp_pool = self.config.vp_pool_per_player * len(self.players)
        self.round_number = 0
        self.tile_bag = list(NON_START_TILES)
        self.rng.shuffle(self.tile_bag)

        start_pairs = list(START_FACTION_PAIRS)
        home_worlds = list(HOME_WORLDS)
        self.rng.shuffle(start_pairs)
        self.rng.shuffle(home_worlds)
        for player in self.players:
            for tile in start_pairs.pop():
                self.add_start_tile(player, tile)
            self.add_start_tile(player, home_worlds.pop())
            self.scout_tile(player, TileKind.DEVELOPMENT)
            self.scout_tile(player, TileKind.WORLD)

    def make_player(self, name: str, strategy: str) -> Player:
        player = Player(name=name, strategy=strategy, credits=self.config.starting_credits)
        player.sections = {section: [] for section in SECTION_ORDER}
        player.spent = {color: 0 for color in DieColor}
        for section, color in (
            (Section.EXPLORE, DieColor.BLUE),
            (Section.DEVELOP, DieColor.BROWN),
            (Section.SETTLE, DieColor.RED),
            (Section.PRODUCE, DieColor.GREEN),
            (Section.SHIP, DieColor.PURPLE),
        ):
            player.sections[section] = [color] * self.config.starting_per_phase
        player.spent[DieColor.WHITE] = self.config.starting_white
        player.spent[DieColor.YELLOW] = self.config.starting_yellow
        return player

    def play(self):
        reports = []
        while not self.game_over():
            reports.append(self.play_round())
        return self.final_scores(), reports

    def play_round(self) -> RoundReport:
        self.round_number += 1
        selections: dict[str, Optional[Phase]] = {}
        for player in self.players:
            choice = self.choose_source(player)
            result = self.sow_choice(player, choice)
            player.selected_sections.append(result.final_section)
            if result.selected_phase is not None:
                player.selected_phases.append(result.selected_phase)
            selections[player.name] = result.selected_phase

        selected_set = {phase for phase in selections.values() if phase is not None}
        dummy_phases: list[Phase] = []
        for _ in range(self.config.dummy_phase_count):
            missing = [phase for phase in PHASE_ORDER if phase not in selected_set]
            if not missing:
                break
            phase = self.rng.choice(missing)
            selected_set.add(phase)
            dummy_phases.append(phase)
        selected = tuple(phase for phase in PHASE_ORDER if phase in selected_set)
        used_workers: dict[str, int] = {}
        for player in self.players:
            before_workers = player.used_workers
            before_completed = player.completed_tiles
            for phase in selected:
                self.resolve_phase(player, phase)
            used_workers[player.name] = player.used_workers - before_workers
            if used_workers[player.name] == 0 and player.completed_tiles == before_completed:
                player.dead_rounds += 1
            self.manage_empire(player)

        return RoundReport(
            self.round_number,
            selected,
            selections,
            tuple(dummy_phases),
            used_workers,
            {player.name: self.score(player) for player in self.players},
        )

    def choose_source(self, player: Player) -> SourceChoice:
        choices = self.legal_source_choices(player)
        if not choices:
            return SourceChoice("none")
        return max(choices, key=lambda choice: self.choice_value(player, choice))

    def legal_source_choices(self, player: Player) -> list[SourceChoice]:
        choices: list[SourceChoice] = []
        for section in SECTION_ORDER:
            dice = tuple(player.sections[section])
            if dice:
                choices.append(SourceChoice("section", section=section, order=dice))
        for color, count in player.spent.items():
            for amount in range(1, count + 1):
                native = COLOR_SECTION[color]
                if native is None:
                    for entry_section in SECTION_ORDER:
                        choices.append(
                            SourceChoice(
                                "spent",
                                color=color,
                                count=amount,
                                order=(color,) * amount,
                                entry_section=entry_section,
                            )
                        )
                else:
                    choices.append(
                        SourceChoice(
                            "spent",
                            color=color,
                            count=amount,
                            order=(color,) * amount,
                            entry_section=native,
                        )
                    )
        return choices

    def choice_value(self, player: Player, choice: SourceChoice) -> int:
        result = self.preview_sow(player, choice)
        phase = result.selected_phase
        if phase is None:
            return -100
        value = self.phase_value(player, phase)
        if result.bonus_credit:
            value += 2
        if choice.kind == "spent":
            value += 1
        return value

    def phase_value(self, player: Player, phase: Phase) -> int:
        bias = STRATEGY_BIAS[player.strategy][phase]
        if phase is Phase.EXPLORE:
            need_tiles = int(not player.dev_stack) + int(not player.world_stack)
            return bias + need_tiles * 5 + int(player.credits <= 2) * 2
        if phase is Phase.DEVELOP:
            return bias + self.build_value(player.dev_stack)
        if phase is Phase.SETTLE:
            return bias + self.build_value(player.world_stack)
        if phase is Phase.PRODUCE:
            return bias + max(0, self.producible_world_count(player) - len(player.goods)) * 3
        if phase is Phase.SHIP:
            return bias + len(player.goods) * 5 + int(player.credits <= 2)
        raise ValueError(f"unknown phase: {phase}")

    def build_value(self, stack: list[Construction]) -> int:
        if not stack:
            return -8
        return max(0, 7 - stack[0].tile.cost) + stack[0].progress

    def preview_sow(self, player: Player, choice: SourceChoice) -> SowResult:
        sections = {section: list(dice) for section, dice in player.sections.items()}
        spent = dict(player.spent)
        return self._sow(choice, sections, spent, mutate_player=None)

    def sow_choice(self, player: Player, choice: SourceChoice) -> SowResult:
        return self._sow(choice, player.sections, player.spent, mutate_player=player)

    def _sow(
        self,
        choice: SourceChoice,
        sections: dict[Section, list[DieColor]],
        spent: dict[DieColor, int],
        mutate_player: Optional[Player],
    ) -> SowResult:
        if choice.kind == "none":
            return SowResult(None, None, (), ())
        if choice.kind == "section":
            if choice.section is None:
                raise ValueError("section source requires a section")
            dice = list(sections[choice.section])
            sections[choice.section] = []
            start_index = self.section_index(choice.section) + 1
        elif choice.kind == "spent":
            if choice.color is None:
                raise ValueError("spent source requires a color")
            available = spent.get(choice.color, 0)
            count = min(choice.count or available, available)
            dice = [choice.color] * count
            spent[choice.color] = available - count
            entry_section = choice.entry_section or COLOR_SECTION[choice.color]
            if entry_section is None:
                raise ValueError("spent white/yellow source requires an entry section")
            start_index = self.section_index(entry_section)
        else:
            raise ValueError(f"unknown source kind: {choice.kind}")

        if choice.order:
            ordered = list(choice.order)
            if sorted(color.value for color in ordered) == sorted(color.value for color in dice):
                dice = ordered

        placed: list[tuple[Section, DieColor]] = []
        overflow: list[DieColor] = []
        final_section: Optional[Section] = None
        bonus_credit = False
        bonus_awarded = False
        index = start_index
        for die in dice:
            landing = self.next_section_with_space(sections, index)
            if landing is None:
                spent[die] = spent.get(die, 0) + 1
                overflow.append(die)
                continue
            sections[landing].append(die)
            placed.append((landing, die))
            final_section = landing
            if (
                self.config.conservative_bonus
                and not bonus_awarded
                and COLOR_SECTION[die] is landing
            ):
                bonus_credit = True
                bonus_awarded = True
            index = self.section_index(landing) + 1

        selected_phase = self.selected_phase_for_section(final_section, choice.fallback_phase, mutate_player)
        if mutate_player is not None and bonus_credit:
            before = mutate_player.credits
            mutate_player.credits = min(self.config.credit_cap, mutate_player.credits + 1)
            gained = mutate_player.credits - before
            mutate_player.credits_earned += gained
            mutate_player.color_match_bonuses += gained
        return SowResult(final_section, selected_phase, tuple(placed), tuple(overflow), bonus_credit)

    def selected_phase_for_section(
        self,
        section: Optional[Section],
        fallback_phase: Optional[Phase],
        player: Optional[Player],
    ) -> Optional[Phase]:
        if section is None:
            return None
        phase = SECTION_PHASE[section]
        return phase

    def best_alien_phase(self, player: Player) -> Phase:
        candidates = [phase for phase in PHASE_ORDER if self.has_alien_work(player, phase)]
        if not candidates:
            candidates = list(PHASE_ORDER)
        return max(candidates, key=lambda phase: self.phase_value(player, phase))

    def next_section_with_space(
        self,
        sections: dict[Section, list[DieColor]],
        start_index: int,
    ) -> Optional[Section]:
        for offset in range(len(SECTION_ORDER)):
            section = SECTION_ORDER[(start_index + offset) % len(SECTION_ORDER)]
            if len(sections[section]) < self.config.section_cap:
                return section
        return None

    def section_index(self, section: Section) -> int:
        return SECTION_ORDER.index(section)

    def resolve_phase(self, player: Player, phase: Phase):
        if phase is Phase.DEVELOP:
            self.resolve_build_phase(player, player.dev_stack, phase)
            return
        if phase is Phase.SETTLE:
            self.resolve_build_phase(player, player.world_stack, phase)
            return
        while self.can_apply_worker(player, phase):
            worker = self.take_worker(player, phase)
            if worker is None:
                return
            if not self.apply_worker(player, phase, worker):
                self.add_spent(player, worker)
                return
            player.used_workers += 1

    def resolve_build_phase(self, player: Player, stack: list[Construction], phase: Phase):
        if not stack:
            return
        build = stack[0]
        while build.progress < build.tile.cost:
            worker = self.take_worker(player, phase, alien_only=self.is_alien_tile(build.tile))
            if worker is None:
                break
            build.workers.append(worker)
            player.used_workers += 1
            if build.progress + player.credits >= build.tile.cost:
                break
        if build.progress + player.credits < build.tile.cost:
            return
        credit_cost = max(0, build.tile.cost - build.progress)
        if credit_cost:
            player.credits -= credit_cost
            player.credits_spent += credit_cost
        for worker in build.workers:
            self.add_spent(player, worker)
        stack.pop(0)
        self.complete_tile(player, build.tile)

    def can_apply_worker(self, player: Player, phase: Phase) -> bool:
        if self.available_workers(player, phase) <= 0:
            return False
        if phase is Phase.EXPLORE:
            return True
        if phase is Phase.PRODUCE:
            return self.producible_world_count(player) > 0
        if phase is Phase.SHIP:
            return bool(player.goods)
        return False

    def available_workers(self, player: Player, phase: Phase, alien_only: bool = False) -> int:
        return len(player.sections[PHASE_SECTION[phase]])

    def take_worker(self, player: Player, phase: Phase, alien_only: bool = False) -> Optional[DieColor]:
        section = PHASE_SECTION[phase]
        if alien_only and DieColor.YELLOW in player.sections[section]:
            player.sections[section].remove(DieColor.YELLOW)
            return DieColor.YELLOW
        if player.sections[section]:
            return player.sections[section].pop(0)
        return None

    def apply_worker(self, player: Player, phase: Phase, worker: DieColor) -> bool:
        if phase is Phase.EXPLORE:
            return self.explore(player, worker)
        if phase is Phase.PRODUCE:
            return self.produce(player, worker)
        if phase is Phase.SHIP:
            return self.ship(player, worker)
        return False

    def explore(self, player: Player, worker: DieColor) -> bool:
        if not player.dev_stack:
            self.scout_tile(player, TileKind.DEVELOPMENT)
        elif not player.world_stack:
            self.scout_tile(player, TileKind.WORLD)
        else:
            self.gain_credits(player, 2)
        self.add_spent(player, worker)
        return True

    def scout_tile(self, player: Player, kind: TileKind) -> Optional[Tile]:
        for index, tile in enumerate(self.tile_bag):
            if tile.kind is kind:
                stack = player.dev_stack if kind is TileKind.DEVELOPMENT else player.world_stack
                stack.append(Construction(tile))
                del self.tile_bag[index]
                return tile
        return None

    def produce(self, player: Player, worker: DieColor) -> bool:
        candidates = self.producible_worlds(player)
        if worker is DieColor.YELLOW:
            alien_candidates = [tile for tile in candidates if self.is_alien_tile(tile)]
            candidates = alien_candidates or candidates
        if not candidates:
            return False
        world = max(candidates, key=lambda tile: tile.vp)
        player.goods.append(Good(world, worker))
        return True

    def ship(self, player: Player, worker: DieColor) -> bool:
        if not player.goods:
            return False
        candidates = player.goods
        if worker is DieColor.YELLOW:
            alien_goods = [good for good in candidates if self.is_alien_tile(good.world)]
            candidates = alien_goods or candidates
        good = max(candidates, key=lambda item: item.world.vp)
        player.goods.remove(good)
        self.add_spent(player, good.color)
        if player.credits <= 2:
            self.gain_credits(player, 3 + good.world.vp // 2)
        else:
            vp = 1 + int(good.color is self.world_color(good.world) or good.color is DieColor.WHITE)
            claimed = min(vp, self.vp_pool)
            player.vp_chips += claimed
            self.vp_pool -= claimed
        self.add_spent(player, worker)
        return True

    def complete_tile(self, player: Player, tile: Tile):
        player.tableau.append(tile)
        player.completed_tiles += 1
        self.apply_tile_immediate_effects(player, tile)

    def add_start_tile(self, player: Player, tile: Tile):
        player.tableau.append(tile)
        self.apply_tile_immediate_effects(player, tile)

    def apply_tile_immediate_effects(self, player: Player, tile: Tile):
        for _ in range(tile.die_loss):
            self.lose_die(player, avoid=tile.grants)
        for color in tile.grants:
            self.gain_die(player, color)
        if tile.immediate_credits:
            self.gain_credits(player, tile.immediate_credits)
        if tile.placement == "world" and tile.produces and tile.grants:
            self.move_owned_die_to_good(player, tile, tile.grants[0])

    def gain_die(self, player: Player, color: DieColor):
        section = COLOR_SECTION[color]
        if section is not None and len(player.sections[section]) < self.config.section_cap:
            player.sections[section].append(color)
        else:
            player.spent[color] += 1

    def lose_die(self, player: Player, avoid: tuple[DieColor, ...] = ()) -> bool:
        colors = [color for color in DieColor if color not in avoid]
        if self.remove_owned_die(player, colors, spent_first=True):
            return True
        return self.remove_owned_die(player, list(DieColor), spent_first=True)

    def remove_owned_die(self, player: Player, colors: list[DieColor], spent_first: bool) -> bool:
        if spent_first:
            for color in colors:
                if player.spent[color] > 0:
                    player.spent[color] -= 1
                    return True
        for section in SECTION_ORDER:
            for index, die in enumerate(player.sections[section]):
                if die in colors:
                    del player.sections[section][index]
                    return True
        for index, good in enumerate(player.goods):
            if good.color in colors:
                del player.goods[index]
                return True
        for build in player.dev_stack + player.world_stack:
            for index, die in enumerate(build.workers):
                if die in colors:
                    del build.workers[index]
                    return True
        return False

    def move_owned_die_to_good(self, player: Player, tile: Tile, color: DieColor) -> bool:
        section = COLOR_SECTION[color]
        if section is not None and color in player.sections[section]:
            player.sections[section].remove(color)
        elif player.spent[color] > 0:
            player.spent[color] -= 1
        else:
            for section in SECTION_ORDER:
                if color in player.sections[section]:
                    player.sections[section].remove(color)
                    break
            else:
                return False
        player.goods.append(Good(tile, color))
        return True

    def add_spent(self, player: Player, color: DieColor):
        player.spent[color] += 1

    def manage_empire(self, player: Player):
        while player.credits > self.config.recovery_sow_cost:
            choice = self.best_recovery_choice(player)
            if choice is None:
                break
            player.credits -= self.config.recovery_sow_cost
            player.credits_spent += self.config.recovery_sow_cost
            player.recovery_sows += 1
            self.sow_choice(player, choice)
        if player.credits == 0:
            player.credits = 1

    def best_recovery_choice(self, player: Player) -> Optional[SourceChoice]:
        choices = []
        for color, count in player.spent.items():
            if count <= 0:
                continue
            native = COLOR_SECTION[color]
            if native is None:
                for entry_section in SECTION_ORDER:
                    choices.append(
                        SourceChoice(
                            "spent",
                            color=color,
                            count=count,
                            order=(color,) * count,
                            entry_section=entry_section,
                        )
                    )
            else:
                choices.append(
                    SourceChoice("spent", color=color, count=count, order=(color,) * count, entry_section=native)
                )
        if not choices:
            return None
        return max(choices, key=lambda choice: self.choice_value(player, choice))

    def gain_credits(self, player: Player, amount: int):
        before = player.credits
        player.credits = min(self.config.credit_cap, player.credits + amount)
        player.credits_earned += player.credits - before

    def has_alien_work(self, player: Player, phase: Phase) -> bool:
        if phase is Phase.DEVELOP:
            return bool(player.dev_stack and self.is_alien_tile(player.dev_stack[0].tile))
        if phase is Phase.SETTLE:
            return bool(player.world_stack and self.is_alien_tile(player.world_stack[0].tile))
        if phase is Phase.PRODUCE:
            return any(self.is_alien_tile(tile) for tile in self.producible_worlds(player))
        if phase is Phase.SHIP:
            return any(self.is_alien_tile(good.world) for good in player.goods)
        return False

    def is_alien_tile(self, tile: Tile) -> bool:
        return (
            "alien_technology" in tile.tags
            or "alien" in tile.id
            or "alien" in tile.name.lower()
            or tile.world_color.strip().lower() == "alien technology"
        )

    def world_color(self, tile: Tile) -> Optional[DieColor]:
        normalized = tile.world_color.strip().lower()
        return {
            "novelty": DieColor.BLUE,
            "rare elemental": DieColor.BROWN,
            "rare elements": DieColor.BROWN,
            "genes": DieColor.GREEN,
            "alien technology": DieColor.YELLOW,
        }.get(normalized)

    def producible_world_count(self, player: Player) -> int:
        return len(self.producible_worlds(player))

    def producible_worlds(self, player: Player) -> list[Tile]:
        occupied = {good.world.id for good in player.goods}
        return [tile for tile in player.tableau if tile.produces and tile.id not in occupied]

    def score(self, player: Player) -> int:
        return player.vp_chips + sum(tile.vp for tile in player.tableau)

    def game_over(self) -> bool:
        if self.round_number >= self.config.max_rounds:
            return True
        if self.vp_pool <= 0:
            return True
        return any(len(player.tableau) >= self.config.target_tableau_squares for player in self.players)

    def final_scores(self):
        scored = []
        for player in self.players:
            scored.append(
                (
                    player.name,
                    self.score(player),
                    {
                        "strategy": player.strategy,
                        "rounds": self.round_number,
                        "tableau": len(player.tableau),
                        "credits": player.credits,
                        "goods": len(player.goods),
                        "dead_rounds": player.dead_rounds,
                        "used_workers": player.used_workers,
                        "completed_tiles": player.completed_tiles,
                        "credits_earned": player.credits_earned,
                        "credits_spent": player.credits_spent,
                        "recovery_sows": player.recovery_sows,
                        "color_match_bonuses": player.color_match_bonuses,
                        "sections": self.section_summary(player),
                        "spent": {color.value: count for color, count in player.spent.items() if count},
                    },
                )
            )
        return sorted(scored, key=lambda row: (row[1], row[2]["credits"]), reverse=True)

    def section_summary(self, player: Player):
        return {
            section.value: [die.value for die in dice]
            for section, dice in player.sections.items()
            if dice
        }
