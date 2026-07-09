from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, Optional

from roll_galaxy.model import BuildSlot, CapacityTrack, DieColor, Good, PHASE_ORDER, Phase, Player, Tile, TileKind
from roll_galaxy.tiles import HOME_WORLDS, NON_START_TILES, START_FACTION_PAIRS


PHASE_COLOR: dict[Phase, DieColor] = {
    Phase.EXPLORE: DieColor.BLUE,
    Phase.DEVELOP: DieColor.BROWN,
    Phase.SETTLE: DieColor.WHITE,
    Phase.PRODUCE: DieColor.GREEN,
    Phase.SHIP: DieColor.PURPLE,
}

STRATEGY_BIAS: dict[str, dict[Phase, int]] = {
    "balanced": {phase: 3 for phase in PHASE_ORDER},
    "builder": {
        Phase.EXPLORE: 4,
        Phase.DEVELOP: 5,
        Phase.SETTLE: 4,
        Phase.PRODUCE: 2,
        Phase.SHIP: 3,
    },
    "settler": {
        Phase.EXPLORE: 3,
        Phase.DEVELOP: 1,
        Phase.SETTLE: 6,
        Phase.PRODUCE: 2,
        Phase.SHIP: 2,
    },
    "producer": {
        Phase.EXPLORE: 3,
        Phase.DEVELOP: 1,
        Phase.SETTLE: 2,
        Phase.PRODUCE: 6,
        Phase.SHIP: 5,
    },
    "shipper": {
        Phase.EXPLORE: 3,
        Phase.DEVELOP: 2,
        Phase.SETTLE: 1,
        Phase.PRODUCE: 4,
        Phase.SHIP: 6,
    },
    "mining": {
        Phase.EXPLORE: 5,
        Phase.DEVELOP: 3,
        Phase.SETTLE: 4,
        Phase.PRODUCE: 3,
        Phase.SHIP: 4,
    },
    "novelty": {
        Phase.EXPLORE: 5,
        Phase.DEVELOP: 2,
        Phase.SETTLE: 4,
        Phase.PRODUCE: 3,
        Phase.SHIP: 4,
    },
    "genes": {
        Phase.EXPLORE: 5,
        Phase.DEVELOP: 2,
        Phase.SETTLE: 4,
        Phase.PRODUCE: 5,
        Phase.SHIP: 3,
    },
    "alien": {
        Phase.EXPLORE: 5,
        Phase.DEVELOP: 3,
        Phase.SETTLE: 5,
        Phase.PRODUCE: 3,
        Phase.SHIP: 3,
    },
    "military": {
        Phase.EXPLORE: 4,
        Phase.DEVELOP: 2,
        Phase.SETTLE: 6,
        Phase.PRODUCE: 2,
        Phase.SHIP: 3,
    },
    "diverse": {
        Phase.EXPLORE: 6,
        Phase.DEVELOP: 2,
        Phase.SETTLE: 4,
        Phase.PRODUCE: 3,
        Phase.SHIP: 3,
    },
}

WORLD_FIRST_STRATEGIES = {
    "settler",
    "producer",
    "shipper",
    "mining",
    "novelty",
    "genes",
    "alien",
    "military",
    "diverse",
}


@dataclass(frozen=True)
class PhaseBatteryConfig:
    starting_capacity: int = 3
    starting_credits: int = 1
    max_track_capacity: int = 6
    max_credits: Optional[int] = None
    minimum_recharge: int = 0
    yellow_mode: str = "alien"
    target_tableau_squares: int = 12
    vp_pool_per_player: Optional[int] = None
    max_rounds: int = 40
    red_grants_current: bool = True
    construction_limit: int = 3
    endgame_goal_pool_extra: int = 2
    endgame_goal_penalty: int = 6


@dataclass(frozen=True)
class RoundReport:
    round_number: int
    phases: tuple[Phase, ...]
    used_pips: dict[str, int]
    red_exhausts: dict[str, int]
    scores: dict[str, int]


class PhaseBatteryGame:
    def __init__(
        self,
        players: Optional[Iterable[tuple[str, str]]] = None,
        seed: Optional[int] = None,
        config: Optional[PhaseBatteryConfig] = None,
    ):
        self.rng = random.Random(seed)
        self.config = config or PhaseBatteryConfig()
        specs = list(players or [("P1", "builder"), ("P2", "producer")])
        self.players = [self.make_player(name, strategy) for name, strategy in specs]
        self.vp_pool_per_player = self.effective_vp_pool_per_player(len(self.players))
        self.vp_pool = self.vp_pool_per_player * len(self.players)
        self.starting_vp_pool = self.vp_pool
        self.round_number = 0
        endgame_tiles = [tile for tile in NON_START_TILES if self.is_endgame_goal(tile)]
        self.tile_bag = [tile for tile in NON_START_TILES if not self.is_endgame_goal(tile)]
        self.rng.shuffle(self.tile_bag)
        self.rng.shuffle(endgame_tiles)
        self.endgame_goal_market = endgame_tiles[: self.config.endgame_goal_pool_extra + len(self.players)]
        self.extra_endgame_goals = endgame_tiles[self.config.endgame_goal_pool_extra + len(self.players) :]
        self.goal_candidates: dict[str, list[Tile]] = {}
        self.committed_goals: dict[str, list[Tile]] = {player.name: [] for player in self.players}
        self.goal_commit_round: Optional[int] = None
        self._red_exhausts = {player.name: 0 for player in self.players}
        self._pending_cup_recharges = {
            player.name: {color: 0 for color in DieColor}
            for player in self.players
        }
        self._cup_recharges = {player.name: 0 for player in self.players}
        self._unready_die_gains = {player.name: 0 for player in self.players}
        self._reassign_remaining = {player.name: 0 for player in self.players}
        self._reassigned_pips = {player.name: 0 for player in self.players}

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
        for player in self.players:
            self.goal_candidates[player.name] = self.choose_goal_candidates(player, 2)

    def make_player(self, name: str, strategy: str) -> Player:
        if strategy not in STRATEGY_BIAS:
            raise ValueError(f"unknown strategy: {strategy}")
        player = Player(name=name, strategy=strategy, credits=self.config.starting_credits)
        player.tracks = {color: CapacityTrack(color=color) for color in DieColor}
        for color in (DieColor.BLUE, DieColor.BROWN, DieColor.RED, DieColor.WHITE, DieColor.GREEN, DieColor.PURPLE):
            player.tracks[color] = CapacityTrack(
                color=color,
                current=self.config.starting_capacity,
                maximum=self.config.starting_capacity,
            )
        player.tracks[DieColor.YELLOW] = CapacityTrack(DieColor.YELLOW, 0, 0)
        return player

    def effective_vp_pool_per_player(self, player_count: int) -> int:
        if self.config.vp_pool_per_player is not None:
            return self.config.vp_pool_per_player
        return 7

    def play(self):
        reports = []
        while not self.game_over():
            reports.append(self.play_round())
        return self.final_scores(), reports

    def play_round(self) -> RoundReport:
        self.round_number += 1
        for player in self.players:
            self.start_reassign_round(player)
        before_pips = {player.name: player.used_pips for player in self.players}
        before_red = dict(self._red_exhausts)
        before_completed = {player.name: player.completed_tiles for player in self.players}
        selected_phases = self.selected_phases()

        for phase in selected_phases:
            for player in self.players:
                self.resolve_phase(player, phase)
        for player in self.players:
            used = player.used_pips - before_pips[player.name]
            if used == 0 and player.completed_tiles == before_completed[player.name]:
                player.dead_rounds += 1
            self.manage_empire(player)
        self.maybe_commit_goals()

        return RoundReport(
            self.round_number,
            selected_phases,
            {player.name: player.used_pips - before_pips[player.name] for player in self.players},
            {player.name: self._red_exhausts[player.name] - before_red[player.name] for player in self.players},
            {player.name: self.score(player) for player in self.players},
        )

    def selected_phases(self) -> tuple[Phase, ...]:
        selected = {
            phase
            for player in self.players
            for phase in self.choose_phases(player, self.phase_selection_count())
        }
        return tuple(phase for phase in PHASE_ORDER if phase in selected)

    def phase_selection_count(self) -> int:
        return 2 if len(self.players) <= 2 else 1

    def start_reassign_round(self, player: Player):
        self._reassign_remaining[player.name] = sum(
            1
            for tile in player.tableau
            if tile.kind is TileKind.DEVELOPMENT and "reassign" in tile.tags
        )

    def choose_phase(self, player: Player) -> Optional[Phase]:
        phases = self.choose_phases(player, 1)
        if not phases:
            return None
        return phases[0]

    def choose_phases(self, player: Player, count: int) -> tuple[Phase, ...]:
        eligible = [phase for phase in PHASE_ORDER if self.can_select_phase(player, phase)]
        ranked = sorted(eligible, key=lambda phase: self.phase_selection_value(player, phase), reverse=True)
        selected = set(ranked[:count])
        return tuple(phase for phase in PHASE_ORDER if phase in selected)

    def can_select_phase(self, player: Player, phase: Phase) -> bool:
        if phase is Phase.EXPLORE:
            return self.available_native_capacity(player, phase) > 0
        if phase is Phase.DEVELOP:
            return bool(player.dev_stack) and any(
                self.available_native_build_pips(player, phase, build.tile) > 0
                for build in player.dev_stack
            )
        if phase is Phase.SETTLE:
            return any(
                self.can_settle_military(player, build.tile)
                if self.is_military_world(build.tile)
                else build.progress >= build.tile.cost
                or self.available_native_build_pips(player, phase, build.tile) > 0
                for build in player.world_stack
            )
        if phase is Phase.PRODUCE:
            return (
                self.producible_world_count(player) > 0
                and self.available_native_capacity(player, phase) > 0
            )
        if phase is Phase.SHIP:
            return (
                bool(player.goods)
                and self.available_native_capacity(player, phase) > 0
            )
        raise ValueError(f"unknown phase: {phase}")

    def phase_selection_value(self, player: Player, phase: Phase) -> tuple[int, int]:
        value = STRATEGY_BIAS[player.strategy][phase]
        if phase is Phase.EXPLORE:
            value += int(len(player.dev_stack) < self.config.construction_limit) * 3
            value += int(len(player.world_stack) < self.config.construction_limit) * 3
            value += int(player.credits <= 1) * 2
            value += self.available_capacity(player, phase) * 2
        elif phase is Phase.DEVELOP:
            if not player.dev_stack or self.available_develop_pips(player) <= 0:
                value -= 8
            value += int(bool(player.dev_stack)) * 5
            value += min(6, self.available_develop_pips(player) * 2)
        elif phase is Phase.SETTLE:
            if not player.world_stack or self.best_settle_target(player) is None:
                value -= 8
            value += int(bool(player.world_stack)) * 5
            value += min(6, self.available_settle_pips(player) * 2)
        elif phase is Phase.PRODUCE:
            if self.producible_world_count(player) <= 0 or self.available_capacity(player, phase) <= 0:
                value -= 8
            value += min(5, self.producible_world_count(player))
            value += self.available_capacity(player, phase)
        elif phase is Phase.SHIP:
            if not player.goods or self.available_capacity(player, phase) <= 0:
                value -= 8
            value += min(6, len(player.goods) * 2)
            value += int(player.credits <= 2 and bool(player.goods)) * 2
            value += self.available_capacity(player, phase)
        return (value, -PHASE_ORDER.index(phase))

    def resolve_phase(self, player: Player, phase: Phase):
        if phase is Phase.EXPLORE:
            self.resolve_explore_phase(player)
            return
        if phase is Phase.DEVELOP:
            self.resolve_develop_phase(player)
            return
        if phase is Phase.SETTLE:
            self.resolve_settle_phase(player)
            return
        if phase is Phase.PRODUCE:
            self.resolve_worker_phase(player, phase)
            return
        if phase is Phase.SHIP:
            self.resolve_worker_phase(player, phase)
            return
        raise ValueError(f"unknown phase: {phase}")

    def resolve_explore_phase(self, player: Player):
        while self.available_capacity(player, Phase.EXPLORE) > 0:
            if self.should_take_extra_goal(player):
                if self.spend_phase_pip(player, Phase.EXPLORE) is None:
                    return
                goal = self.take_extra_goal(player)
                if goal is None:
                    return
                player.used_pips += 1
                continue
            scout_kind = self.explore_scout_kind(player)
            if scout_kind is not None:
                depth = self.explore_search_depth(player)
                spent = self.spend_phase_pips(player, Phase.EXPLORE, depth)
                if not spent:
                    return
                self.scout_tile(player, scout_kind, search_depth=spent)
                player.used_pips += spent
                continue
            if player.credits > 2:
                return
            if self.spend_phase_pip(player, Phase.EXPLORE) is None:
                return
            self.gain_credits(player, 2)
            player.used_pips += 1

    def explore_scout_kind(self, player: Player) -> Optional[TileKind]:
        dev_open = len(player.dev_stack) < self.config.construction_limit
        world_open = len(player.world_stack) < self.config.construction_limit
        if not dev_open and not world_open:
            return None
        if dev_open and world_open and len(player.dev_stack) == len(player.world_stack):
            if player.strategy == "builder" and self.builder_endgame_plan_ids(player):
                return TileKind.WORLD
            return TileKind.WORLD if player.strategy in WORLD_FIRST_STRATEGIES else TileKind.DEVELOPMENT
        if dev_open and (not world_open or len(player.dev_stack) < len(player.world_stack)):
            return TileKind.DEVELOPMENT
        if world_open:
            return TileKind.WORLD
        return None

    def explore_search_depth(self, player: Player) -> int:
        available = self.available_capacity(player, Phase.EXPLORE)
        if not player.dev_stack and not player.world_stack:
            return min(2, available)
        return min(1, available)

    def resolve_develop_phase(self, player: Player):
        while player.dev_stack:
            build = self.best_completable_development(player)
            if build is None:
                break
            self.pay_development(player, build, complete=True)
            if build.progress >= build.tile.cost:
                player.dev_stack.remove(build)
                self.complete_tile(player, build.tile)

        while player.dev_stack and self.available_develop_pips(player) > 0:
            build = self.best_development_progress_target(player)
            if build is None:
                return
            before = build.progress
            self.pay_development(player, build, complete=False)
            if build.progress == before:
                return
            if build.progress >= build.tile.cost:
                player.dev_stack.remove(build)
                self.complete_tile(player, build.tile)

    def resolve_settle_phase(self, player: Player):
        while player.world_stack:
            build = self.best_settle_target(player)
            if build is None:
                return
            tile = build.tile
            if self.is_military_world(tile):
                self.spend_one(player, DieColor.RED)
                player.used_pips += 1
                self._red_exhausts[player.name] += 1
            else:
                needed = max(0, tile.cost - build.progress)
                pips = self.spend_build_pips(player, Phase.SETTLE, tile, needed)
                build.progress += pips
                player.used_pips += pips
                if build.progress < tile.cost:
                    return
            player.world_stack.remove(build)
            self.complete_tile(player, tile)

    def best_completable_development(self, player: Player) -> Optional[BuildSlot]:
        candidates = [
            build
            for build in player.dev_stack
            if self.can_pay_develop(player, build.tile, build.progress)
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda build: self.build_target_value(player, build))

    def best_development_progress_target(self, player: Player) -> Optional[BuildSlot]:
        incomplete = [build for build in player.dev_stack if build.progress < build.tile.cost]
        if not incomplete:
            return None
        return max(incomplete, key=lambda build: self.build_target_value(player, build))

    def build_target_value(self, player: Player, build: BuildSlot):
        remaining = max(0, build.tile.cost - build.progress)
        return (
            self.strategy_tile_value(player, build.tile) + build.tile.vp + build.progress * 3,
            -remaining,
        )

    def pay_development(self, player: Player, build: BuildSlot, complete: bool):
        needed = max(0, build.tile.cost - build.progress)
        if needed <= 0:
            return
        pips = self.spend_build_pips(player, Phase.DEVELOP, build.tile, needed)
        build.progress += pips
        player.used_pips += pips

    def available_develop_pips(self, player: Player) -> int:
        return sum(
            self.available_build_pips(player, Phase.DEVELOP, build.tile)
            for build in player.dev_stack
        )

    def best_settle_target(self, player: Player) -> Optional[BuildSlot]:
        candidates = []
        for build in player.world_stack:
            tile = build.tile
            if self.is_military_world(tile):
                if self.can_settle_military(player, tile):
                    candidates.append(build)
                continue
            if build.progress >= tile.cost or self.available_build_pips(player, Phase.SETTLE, tile) > 0:
                candidates.append(build)
        if not candidates:
            return None
        return max(candidates, key=lambda build: self.settle_target_value(player, build))

    def settle_target_value(self, player: Player, build: BuildSlot):
        tile = build.tile
        return (
            self.strategy_tile_value(player, tile) + tile.vp + len(tile.grants) * 2 + build.progress * 3,
            -(max(0, tile.cost - build.progress)),
        )

    def resolve_worker_phase(self, player: Player, phase: Phase):
        while self.can_apply_worker(player, phase):
            spent_color = self.spend_phase_pip(player, phase)
            if spent_color is None:
                return
            if not self.apply_worker(player, phase, spent_color):
                self.refund_pip(player, spent_color)
                return
            player.used_pips += 1

    def can_apply_worker(self, player: Player, phase: Phase) -> bool:
        if phase is Phase.PRODUCE:
            return self.producible_world_count(player) > 0 and self.available_capacity(player, phase) > 0
        if phase is Phase.SHIP:
            return bool(player.goods) and self.available_capacity(player, phase) > 0
        raise ValueError(f"unknown worker phase: {phase}")

    def apply_worker(self, player: Player, phase: Phase, spent_color: DieColor) -> bool:
        if phase is Phase.PRODUCE:
            return self.produce(player, spent_color)
        if phase is Phase.SHIP:
            return self.ship(player, spent_color)
        raise ValueError(f"unknown worker phase: {phase}")

    def can_pay_develop(self, player: Player, tile: Tile, progress: int = 0) -> bool:
        return progress + self.available_build_pips(player, Phase.DEVELOP, tile) >= tile.cost

    def can_pay_normal_world(self, player: Player, tile: Tile, progress: int = 0) -> bool:
        return progress + self.available_build_pips(player, Phase.SETTLE, tile) >= tile.cost

    def can_settle_military(self, player: Player, tile: Tile) -> bool:
        return self.track(player, DieColor.RED).current >= tile.cost

    def available_build_pips(self, player: Player, phase: Phase, tile: Tile) -> int:
        native_colors = self.build_colors(player, phase, tile)
        native = self.available_native_build_pips(player, phase, tile)
        routed = self.available_reassigned_pips(player, native_colors)
        return native + routed

    def available_native_build_pips(self, player: Player, phase: Phase, tile: Tile) -> int:
        return sum(
            self.track(player, color).current
            for color in self.build_colors(player, phase, tile)
        )

    def spend_build_pips(self, player: Player, phase: Phase, tile: Tile, limit: Optional[int] = None) -> int:
        remaining = tile.cost if limit is None else limit
        spent = 0
        for color in self.build_colors(player, phase, tile):
            if remaining <= 0:
                break
            track = self.track(player, color)
            amount = min(track.current, remaining)
            track.current -= amount
            remaining -= amount
            spent += amount
        native_colors = self.build_colors(player, phase, tile)
        while remaining > 0 and self.spend_reassigned_pip(player, native_colors) is not None:
            remaining -= 1
            spent += 1
        return spent

    def build_colors(self, player: Player, phase: Phase, tile: Tile) -> tuple[DieColor, ...]:
        if phase is Phase.DEVELOP:
            colors = [DieColor.BROWN]
            if self.config.yellow_mode == "alien" and self.is_alien_tile(tile):
                colors.append(DieColor.YELLOW)
            return tuple(colors)
        if phase is Phase.SETTLE:
            if self.config.yellow_mode == "alien" and self.is_alien_tile(tile):
                return (DieColor.WHITE, DieColor.YELLOW)
            return (DieColor.WHITE,)
        raise ValueError(f"unknown build phase: {phase}")

    def phase_colors(self, player: Player, phase: Phase) -> tuple[DieColor, ...]:
        if phase is Phase.SETTLE:
            colors = [DieColor.WHITE, DieColor.RED]
            if self.config.yellow_mode == "alien" and any(self.is_alien_tile(build.tile) for build in player.world_stack):
                colors.append(DieColor.YELLOW)
            return tuple(colors)
        if phase is Phase.PRODUCE:
            if self.config.yellow_mode == "alien" and any(self.is_alien_tile(tile) for tile in self.producible_worlds(player)):
                return (DieColor.GREEN, DieColor.YELLOW)
            return (DieColor.GREEN,)
        if phase is Phase.SHIP:
            if self.config.yellow_mode == "ship":
                return (DieColor.PURPLE, DieColor.YELLOW)
            if self.config.yellow_mode == "alien" and any(self.is_alien_tile(good.world) for good in player.goods):
                return (DieColor.PURPLE, DieColor.YELLOW)
            return (DieColor.PURPLE,)
        return (PHASE_COLOR[phase],)

    def available_capacity(self, player: Player, phase: Phase) -> int:
        native_colors = self.phase_colors(player, phase)
        native = self.available_native_capacity(player, phase)
        return native + self.available_reassigned_pips(player, native_colors)

    def available_native_capacity(self, player: Player, phase: Phase) -> int:
        return sum(
            self.track(player, color).current
            for color in self.phase_colors(player, phase)
        )

    def available_settle_pips(self, player: Player) -> int:
        return self.available_capacity(player, Phase.SETTLE)

    def spend_phase_pip(self, player: Player, phase: Phase) -> Optional[DieColor]:
        native_colors = self.phase_colors(player, phase)
        for color in native_colors:
            if self.spend_one(player, color):
                return color
        return self.spend_reassigned_pip(player, native_colors)

    def spend_phase_pips(self, player: Player, phase: Phase, count: int) -> int:
        spent = 0
        for _ in range(count):
            if self.spend_phase_pip(player, phase) is None:
                break
            spent += 1
        return spent

    def available_reassigned_pips(
        self,
        player: Player,
        native_colors: tuple[DieColor, ...],
    ) -> int:
        remaining = self._reassign_remaining[player.name]
        if remaining <= 0:
            return 0
        sources = sum(
            track.current
            for color, track in player.tracks.items()
            if color not in native_colors
        )
        return min(remaining, sources)

    def spend_reassigned_pip(
        self,
        player: Player,
        native_colors: tuple[DieColor, ...],
    ) -> Optional[DieColor]:
        if self._reassign_remaining[player.name] <= 0:
            return None
        candidates = [
            track
            for color, track in player.tracks.items()
            if color not in native_colors and track.current > 0
        ]
        if not candidates:
            return None
        track = min(
            candidates,
            key=lambda item: (self.track_value(player, item.color), -item.current),
        )
        track.current -= 1
        self._reassign_remaining[player.name] -= 1
        self._reassigned_pips[player.name] += 1
        return track.color

    def spend_color(self, player: Player, color: DieColor, count: int) -> int:
        track = self.track(player, color)
        spent = min(track.current, count)
        track.current -= spent
        return spent

    def spend_one(self, player: Player, color: DieColor) -> bool:
        track = self.track(player, color)
        if track.current <= 0:
            return False
        track.current -= 1
        return True

    def refund_pip(self, player: Player, color: DieColor):
        track = self.track(player, color)
        track.current = min(track.maximum, track.current + 1)

    def scout_tile(self, player: Player, kind: TileKind, search_depth: Optional[int] = None) -> Optional[Tile]:
        depth = search_depth or 1
        candidates = []
        for index, tile in enumerate(self.tile_bag):
            if tile.kind is kind:
                candidates.append((index, tile))
                if len(candidates) >= depth:
                    break
        if not candidates:
            return None
        index, tile = max(candidates, key=lambda item: self.scout_tile_value(player, item[1]))
        stack = player.dev_stack if kind is TileKind.DEVELOPMENT else player.world_stack
        stack.append(BuildSlot(tile))
        del self.tile_bag[index]
        return tile

    def scout_tile_value(self, player: Player, tile: Tile):
        phase = Phase.DEVELOP if tile.kind is TileKind.DEVELOPMENT else Phase.SETTLE
        return (
            self.strategy_tile_value(player, tile),
            tile.vp + len(tile.grants) + tile.immediate_credits,
            -tile.cost,
            STRATEGY_BIAS[player.strategy][phase],
        )

    def is_endgame_goal(self, tile: Tile) -> bool:
        return tile.kind is TileKind.DEVELOPMENT and "end_game" in tile.tags

    def choose_goal_candidates(self, player: Player, count: int) -> list[Tile]:
        ranked = sorted(
            self.endgame_goal_market,
            key=lambda tile: (self.strategy_tile_value(player, tile), self.builder_endgame_fit(player, tile), tile.vp),
            reverse=True,
        )
        return ranked[:count]

    def should_take_extra_goal(self, player: Player) -> bool:
        if not self.extra_endgame_goals:
            return False
        if player.strategy not in {"builder", "diverse"}:
            return False
        chosen_count = len(self.goal_candidates.get(player.name, [])) + len(self.committed_goals.get(player.name, []))
        if chosen_count >= 3:
            return False
        return len(player.dev_stack) >= self.config.construction_limit or self.goal_commit_round is not None

    def take_extra_goal(self, player: Player) -> Optional[Tile]:
        if not self.extra_endgame_goals:
            return None
        goal = max(
            self.extra_endgame_goals,
            key=lambda tile: (self.strategy_tile_value(player, tile), self.builder_endgame_fit(player, tile), tile.vp),
        )
        self.extra_endgame_goals.remove(goal)
        if self.goal_commit_round is None:
            self.goal_candidates.setdefault(player.name, []).append(goal)
        else:
            self.committed_goals.setdefault(player.name, []).append(goal)
        return goal

    def maybe_commit_goals(self):
        if self.goal_commit_round is not None:
            return
        if self.vp_pool > self.starting_vp_pool // 2 and all(player.completed_tiles < 6 for player in self.players):
            return
        self.goal_commit_round = self.round_number
        for player in self.players:
            candidates = self.goal_candidates.get(player.name, [])
            if not candidates:
                continue
            chosen = max(
                candidates,
                key=lambda tile: (self.endgame_tile_bonus(player, tile), self.strategy_tile_value(player, tile), tile.vp),
            )
            self.committed_goals[player.name] = [chosen]
            self.goal_candidates[player.name] = [chosen]

    def strategy_tile_value(self, player: Player, tile: Tile) -> int:
        strategy = player.strategy
        value = 0
        if strategy == "builder":
            value += self.builder_tile_value(player, tile)
        elif strategy == "settler":
            value += int(tile.kind is TileKind.WORLD) * 8
            value += len(tile.grants) * 3
        elif strategy == "producer":
            value += int(tile.produces) * 16
            value += int(DieColor.GREEN in tile.grants) * 8
            value += int(DieColor.PURPLE in tile.grants) * 5
            value += int(tile.id in {"free_trade_association", "new_economy", "galactic_exchange"}) * 18
        elif strategy == "shipper":
            value += int(tile.produces) * 8
            value += int(DieColor.PURPLE in tile.grants) * 12
            value += int(tile.id in {"free_trade_association", "galactic_bankers", "new_economy"}) * 18
        elif strategy == "mining":
            value += int("rare_elemental" in tile.tags) * 20
            value += int(DieColor.BROWN in tile.grants) * 8
            value += int(tile.id == "mining_league") * 25
        elif strategy == "novelty":
            value += int("novelty" in tile.tags) * 20
            value += int(DieColor.BLUE in tile.grants) * 8
            value += int(tile.id == "free_trade_association") * 25
        elif strategy == "genes":
            value += int("genes" in tile.tags) * 20
            value += int(DieColor.GREEN in tile.grants) * 8
            value += int(tile.id in {"new_economy", "galactic_exchange"}) * 18
        elif strategy == "alien":
            value += int(self.is_alien_tile(tile)) * 24
            value += int(DieColor.YELLOW in tile.grants) * 10
        elif strategy == "military":
            value += int(self.is_military_world(tile)) * 18
            value += int(DieColor.RED in tile.grants) * 12
            value += int(tile.id == "new_galactic_order") * 25
        elif strategy == "diverse":
            value += self.diversity_tile_value(player, tile)
            value += int(tile.id in {"system_diversification", "galactic_exchange"}) * 24
        return value

    def builder_tile_value(self, player: Player, tile: Tile) -> int:
        value = 0
        if tile.kind is TileKind.DEVELOPMENT:
            value += 5
            value += int(DieColor.BROWN in tile.grants) * 6
            value += int(DieColor.BLUE in tile.grants) * 4
            if "end_game" in tile.tags:
                value += 12 + self.builder_endgame_fit(player, tile) * 3
        if tile.kind is TileKind.WORLD:
            value += self.builder_support_value(player, tile)
            value += int(tile.immediate_credits > 0) * (tile.immediate_credits * 2)
            value += int(tile.produces) * 2
            value += int(DieColor.BLUE in tile.grants) * 3
            value += int(DieColor.BROWN in tile.grants) * 3
        return value

    def builder_endgame_fit(self, player: Player, tile: Tile) -> int:
        worlds = [tableau_tile for tableau_tile in player.tableau if tableau_tile.kind is TileKind.WORLD]
        developments = [tableau_tile for tableau_tile in player.tableau if tableau_tile.kind is TileKind.DEVELOPMENT]
        world_colors = {world.world_color.strip().lower() for world in worlds if world.world_color.strip()}
        if tile.id == "free_trade_association":
            return sum(1 for world in worlds if "novelty" in world.tags)
        if tile.id == "galactic_bankers":
            return player.tracks[DieColor.PURPLE].maximum + player.credits
        if tile.id == "galactic_exchange":
            return len(world_colors) + self.color_presence(player)
        if tile.id == "galactic_federation":
            return len(developments)
        if tile.id == "galactic_renaissance":
            return max(0, player.completed_tiles // 2) + len(world_colors)
        if tile.id == "galactic_reserves":
            return sum(track.current for track in self.non_white_tracks(player)) // 3
        if tile.id == "mining_league":
            return sum(1 for world in worlds if "rare_elemental" in world.tags) + player.tracks[DieColor.BROWN].maximum
        if tile.id == "new_economy":
            return sum(1 for world in worlds if world.produces)
        if tile.id == "new_galactic_order":
            return player.tracks[DieColor.RED].maximum
        if tile.id == "system_diversification":
            return len(world_colors) * 2
        return 0

    def builder_support_value(self, player: Player, tile: Tile) -> int:
        plan_ids = self.builder_endgame_plan_ids(player)
        if not plan_ids:
            plan_ids = {
                "free_trade_association",
                "galactic_exchange",
                "galactic_renaissance",
                "mining_league",
                "new_economy",
                "new_galactic_order",
                "system_diversification",
            }
            multiplier = 1
        else:
            multiplier = 2

        value = 0
        normalized = tile.world_color.strip().lower()
        existing_colors = {
            tableau_tile.world_color.strip().lower()
            for tableau_tile in player.tableau
            if tableau_tile.kind is TileKind.WORLD and tableau_tile.world_color.strip()
        }
        new_color = bool(normalized and normalized not in existing_colors)

        if "free_trade_association" in plan_ids and "novelty" in tile.tags:
            value += 5 * multiplier
        if "galactic_bankers" in plan_ids:
            value += int(DieColor.PURPLE in tile.grants) * 4 * multiplier
            value += tile.immediate_credits * multiplier
        if "galactic_exchange" in plan_ids:
            value += int(new_color) * 4 * multiplier
            value += self.new_color_grants(player, tile) * 2 * multiplier
        if "galactic_renaissance" in plan_ids:
            value += 2 * multiplier
            value += int(new_color) * 2 * multiplier
        if "mining_league" in plan_ids:
            value += int("rare_elemental" in tile.tags) * 5 * multiplier
            value += int(DieColor.BROWN in tile.grants) * 3 * multiplier
        if "new_economy" in plan_ids and tile.produces:
            value += 4 * multiplier
        if "new_galactic_order" in plan_ids and self.is_military_world(tile):
            value += 4 * multiplier
            value += int(DieColor.RED in tile.grants) * 3 * multiplier
        if "system_diversification" in plan_ids and new_color:
            value += 6 * multiplier
        return value

    def builder_endgame_plan_ids(self, player: Player) -> set[str]:
        ids = {tile.id for tile in self.goal_candidates.get(player.name, [])}
        ids.update(tile.id for tile in self.committed_goals.get(player.name, []))
        return ids

    def non_white_tracks(self, player: Player) -> list[CapacityTrack]:
        return [track for track in player.tracks.values() if track.color is not DieColor.WHITE]

    def color_presence(self, player: Player) -> int:
        return sum(1 for track in self.non_white_tracks(player) if track.maximum > 0)

    def new_color_grants(self, player: Player, tile: Tile) -> int:
        present = {track.color for track in self.non_white_tracks(player) if track.maximum > 0}
        return sum(1 for color in tile.grants if color not in present and color is not DieColor.WHITE)

    def diversity_tile_value(self, player: Player, tile: Tile) -> int:
        if tile.kind is not TileKind.WORLD:
            return 0
        existing = {
            tableau_tile.world_color.strip().lower()
            for tableau_tile in player.tableau
            if tableau_tile.kind is TileKind.WORLD and tableau_tile.world_color.strip()
        }
        color = tile.world_color.strip().lower()
        if not color:
            return 0
        return 22 if color not in existing else 4

    def produce(self, player: Player, spent_color: DieColor) -> bool:
        candidates = self.producible_worlds(player)
        if spent_color is DieColor.YELLOW and self.config.yellow_mode == "alien":
            candidates = [tile for tile in candidates if self.is_alien_tile(tile)]
        if not candidates:
            return False
        world = max(candidates, key=lambda tile: tile.vp)
        marker_color = DieColor.YELLOW if spent_color is DieColor.YELLOW else DieColor.GREEN
        player.goods.append(Good(world, marker_color))
        return True

    def ship(self, player: Player, spent_color: DieColor) -> bool:
        candidates = player.goods
        if spent_color is DieColor.YELLOW and self.config.yellow_mode == "alien":
            candidates = [good for good in candidates if self.is_alien_tile(good.world)]
        if not candidates:
            return False
        trading = player.credits <= 2
        if trading:
            good = max(candidates, key=self.ship_credit_value)
        else:
            good = max(candidates, key=lambda item: item.world.vp)
        player.goods.remove(good)
        player.shipped_goods += 1
        if trading:
            self.gain_credits(player, self.ship_credit_value(good))
            return True
        claimed = min(1, self.vp_pool)
        player.vp_chips += claimed
        self.vp_pool -= claimed
        return True

    def ship_credit_value(self, item: Tile | Good) -> int:
        world = item.world if isinstance(item, Good) else item
        world_color = self.world_color(world)
        if world_color is DieColor.BLUE:
            return 3
        if world_color is DieColor.BROWN:
            return 4
        if world_color is DieColor.GREEN:
            return 5
        if world_color is DieColor.YELLOW:
            return 6
        return 1

    def complete_tile(self, player: Player, tile: Tile):
        player.tableau.append(tile)
        player.completed_tiles += 1
        if "reassign" in tile.tags:
            self._reassign_remaining[player.name] += 1
        self.apply_tile_immediate_effects(player, tile)

    def add_start_tile(self, player: Player, tile: Tile):
        player.tableau.append(tile)
        self.apply_tile_immediate_effects(player, tile, during_setup=True)

    def apply_tile_immediate_effects(self, player: Player, tile: Tile, during_setup: bool = False):
        for _ in range(tile.die_loss):
            self.lose_die(player, avoid=tile.grants)
        gained_colors = []
        for color in tile.grants:
            if self.gain_die_from_placement(player, color, tile.placement, during_setup):
                gained_colors.append(color)
        if tile.immediate_credits:
            self.gain_credits(player, tile.immediate_credits)
        if tile.placement == "world" and tile.produces and gained_colors:
            self.add_windfall_good(player, tile, gained_colors[0])

    def gain_die_from_placement(
        self,
        player: Player,
        color: DieColor,
        placement: str,
        during_setup: bool = False,
    ) -> bool:
        normalized = placement.strip().lower()
        ready_now = during_setup and normalized == "cup"
        gained = self.gain_die(player, color, ready=ready_now)
        if not gained:
            return False
        if normalized == "cup" and not during_setup:
            if color is not DieColor.RED or self.config.red_grants_current:
                self._pending_cup_recharges[player.name][color] += 1
        elif normalized in {"", "citizenry", "world"}:
            self._unready_die_gains[player.name] += 1
        return True

    def gain_die(self, player: Player, color: DieColor, ready: bool = True) -> bool:
        track = self.track(player, color)
        old_max = track.maximum
        track.maximum = min(self.config.max_track_capacity, track.maximum + 1)
        if color is DieColor.RED and not self.config.red_grants_current:
            track.current = min(track.current, track.maximum)
            return track.maximum > old_max
        if ready and track.maximum > old_max:
            track.current = min(track.maximum, track.current + 1)
        return track.maximum > old_max

    def lose_die(self, player: Player, avoid: tuple[DieColor, ...] = ()) -> bool:
        candidates = [
            track
            for track in player.tracks.values()
            if track.maximum > 0 and track.color not in avoid
        ]
        if not candidates:
            candidates = [track for track in player.tracks.values() if track.maximum > 0]
        if not candidates:
            return False
        track = min(candidates, key=lambda item: (self.track_value(player, item.color), item.maximum, item.current))
        track.maximum -= 1
        track.current = min(track.current, track.maximum)
        return True

    def add_windfall_good(self, player: Player, tile: Tile, color: DieColor):
        if any(good.world.id == tile.id for good in player.goods):
            return False
        player.goods.append(Good(tile, color))
        return True

    def manage_empire(self, player: Player):
        self.apply_pending_cup_recharges(player)
        if self.config.minimum_recharge:
            if self.recharge_best_track(player, self.config.minimum_recharge):
                player.free_recharged += self.config.minimum_recharge
            else:
                player.blocked_recharge += self.config.minimum_recharge
        while player.credits > 0:
            if not self.recharge_best_track(player, 1):
                player.blocked_recharge += player.credits
                break
            self.spend_credits(player, 1)
        if player.credits == 0:
            self.set_credits(player, 1)

    def apply_pending_cup_recharges(self, player: Player):
        pending = self._pending_cup_recharges[player.name]
        for color, amount in pending.items():
            if amount <= 0:
                continue
            track = self.track(player, color)
            recharged = min(amount, track.maximum - track.current)
            track.current += recharged
            self._cup_recharges[player.name] += recharged
            pending[color] = 0

    def recharge_best_track(self, player: Player, amount: int) -> bool:
        candidates = [
            track
            for track in player.tracks.values()
            if track.current < track.maximum
        ]
        if not candidates:
            return False
        track = max(candidates, key=lambda item: (self.track_value(player, item.color), item.maximum - item.current))
        track.current = min(track.maximum, track.current + amount)
        return True

    def track_value(self, player: Player, color: DieColor) -> int:
        if color is DieColor.WHITE:
            return STRATEGY_BIAS[player.strategy][Phase.SETTLE]
        if color is DieColor.YELLOW:
            return 4 if player.strategy == "alien" else 2
        if color is DieColor.RED:
            return STRATEGY_BIAS[player.strategy][Phase.SETTLE]
        phase = next((phase for phase, phase_color in PHASE_COLOR.items() if phase_color is color), None)
        if phase is None:
            return 0
        return STRATEGY_BIAS[player.strategy][phase]

    def gain_credits(self, player: Player, amount: int):
        before = player.credits
        self.set_credits(player, player.credits + amount)
        player.credits_earned += player.credits - before

    def spend_credits(self, player: Player, amount: int):
        player.credits -= amount
        player.credits_spent += amount
        self.sync_credit_track(player)

    def set_credits(self, player: Player, amount: int):
        if self.config.max_credits is None:
            player.credits = max(0, amount)
        else:
            player.credits = max(0, min(self.config.max_credits, amount))
        self.sync_credit_track(player)

    def sync_credit_track(self, player: Player):
        player.tracks.setdefault(DieColor.WHITE, CapacityTrack(DieColor.WHITE, 0, 0))

    def is_military_world(self, tile: Tile) -> bool:
        if tile.kind is not TileKind.WORLD:
            return False
        return DieColor.RED in tile.grants or "rebel" in tile.id or "rebel" in tile.name.lower()

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

    def track(self, player: Player, color: DieColor) -> CapacityTrack:
        return player.tracks[color]

    def score(self, player: Player) -> int:
        return player.vp_chips + sum(tile.vp for tile in player.tableau) + self.endgame_goal_score(player)

    def endgame_goal_score(self, player: Player) -> int:
        total = 0
        for tile in self.committed_goals.get(player.name, []):
            if not self.endgame_goal_fulfilled(player, tile):
                total -= self.config.endgame_goal_penalty
            else:
                total += self.endgame_tile_bonus(player, tile)
        return total

    def endgame_goal_fulfilled(self, player: Player, tile: Tile) -> bool:
        progress, required, _label = self.endgame_goal_requirement(player, tile)
        return progress >= required

    def endgame_goal_requirement(self, player: Player, tile: Tile) -> tuple[int, int, str]:
        worlds = [tableau_tile for tableau_tile in player.tableau if tableau_tile.kind is TileKind.WORLD]
        developments = [tableau_tile for tableau_tile in player.tableau if tableau_tile.kind is TileKind.DEVELOPMENT]
        production_worlds = [world for world in worlds if world.produces]
        world_colors = {world.world_color.strip().lower() for world in worlds if world.world_color.strip()}
        die_tracks = [track for track in player.tracks.values() if track.color is not DieColor.WHITE]
        color_presence = sum(1 for track in die_tracks if track.maximum > 0)
        max_pips = sum(track.maximum for track in die_tracks)
        alien_worlds = sum(1 for world in worlds if self.is_alien_tile(world))
        rare_worlds = sum(1 for world in worlds if "rare_elemental" in world.tags)
        novelty_worlds = sum(1 for world in worlds if "novelty" in world.tags)

        if tile.id == "free_trade_association":
            return novelty_worlds, 2, "Novelty"
        if tile.id == "galactic_bankers":
            return player.shipped_goods, 4, "Satisfied Populace"
        if tile.id == "galactic_exchange":
            return alien_worlds, 1, "Alien Contact"
        if tile.id == "galactic_federation":
            return len(developments), 4, "Developer"
        if tile.id == "galactic_renaissance":
            return player.completed_tiles, 8, "Builder"
        if tile.id == "galactic_reserves":
            return max_pips, 19, "Industrial"
        if tile.id == "mining_league":
            return rare_worlds, 2, "Rare Elements"
        if tile.id == "new_economy":
            return len(production_worlds), 3, "Production"
        if tile.id == "new_galactic_order":
            return player.tracks[DieColor.RED].maximum, 5, "Military"
        if tile.id == "system_diversification":
            return len(world_colors), 4, "Diverse"
        return self.endgame_tile_bonus(player, tile), 1, "converted score"

    def endgame_tile_bonus(self, player: Player, tile: Tile) -> int:
        if "end_game" not in tile.tags:
            return 0
        worlds = [tableau_tile for tableau_tile in player.tableau if tableau_tile.kind is TileKind.WORLD]
        developments = [tableau_tile for tableau_tile in player.tableau if tableau_tile.kind is TileKind.DEVELOPMENT]
        production_worlds = [world for world in worlds if world.produces]
        world_colors = {world.world_color.strip().lower() for world in worlds if world.world_color.strip()}
        die_tracks = [track for track in player.tracks.values() if track.color is not DieColor.WHITE]
        color_presence = sum(1 for track in die_tracks if track.maximum > 0)
        if tile.id == "free_trade_association":
            return sum(1 for world in worlds if "novelty" in world.tags)
        if tile.id == "galactic_bankers":
            return player.tracks[DieColor.PURPLE].maximum + player.credits
        if tile.id == "galactic_exchange":
            return len(world_colors) + color_presence
        if tile.id == "galactic_federation":
            return len(developments)
        if tile.id == "galactic_renaissance":
            return max(0, player.completed_tiles // 2) + len(world_colors)
        if tile.id == "galactic_reserves":
            return sum(track.current for track in die_tracks) // 3
        if tile.id == "mining_league":
            return sum(1 for world in worlds if "rare_elemental" in world.tags) + player.tracks[DieColor.BROWN].maximum
        if tile.id == "new_economy":
            return len(production_worlds)
        if tile.id == "new_galactic_order":
            return player.tracks[DieColor.RED].maximum
        if tile.id == "system_diversification":
            return len(world_colors) * 2
        return 0

    def game_over(self) -> bool:
        if self.round_number >= self.config.max_rounds:
            return True
        if self.vp_pool <= 0:
            return True
        return any(len(player.tableau) >= self.config.target_tableau_squares for player in self.players)

    def final_scores(self):
        self.maybe_commit_goals()
        scored = []
        for player in self.players:
            summary = self.player_summary(player)
            scored.append((player.name, self.score(player), summary))
        return sorted(
            scored,
            key=lambda row: (row[1], row[2]["credits"] + sum(v[0] for v in row[2]["tracks"].values())),
            reverse=True,
        )

    def player_summary(self, player: Player):
        worlds = [tile for tile in player.tableau if tile.kind is TileKind.WORLD]
        return {
            "strategy": player.strategy,
            "rounds": self.round_number,
            "tableau": len(player.tableau),
            "credits": player.credits,
            "goods": len(player.goods),
            "shipped_goods": player.shipped_goods,
            "dead_rounds": player.dead_rounds,
            "used_pips": player.used_pips,
            "red_exhausts": self._red_exhausts[player.name],
            "cup_recharges": self._cup_recharges[player.name],
            "unready_die_gains": self._unready_die_gains[player.name],
            "reassigned_pips": self._reassigned_pips[player.name],
            "credits_earned": player.credits_earned,
            "credits_spent": player.credits_spent,
            "goal_candidates": [tile.name for tile in self.goal_candidates.get(player.name, [])],
            "committed_goals": [tile.name for tile in self.committed_goals.get(player.name, [])],
            "goal_requirements": self.goal_requirement_summary(player),
            "goal_score": self.endgame_goal_score(player),
            "goal_commit_round": self.goal_commit_round,
            "free_recharged": player.free_recharged,
            "blocked_recharge": player.blocked_recharge,
            "completed_tiles": player.completed_tiles,
            "military_worlds": sum(1 for tile in worlds if self.is_military_world(tile)),
            "normal_worlds": sum(1 for tile in worlds if not self.is_military_world(tile)),
            "production_worlds": sum(1 for tile in worlds if tile.produces),
            "tile_vp": sum(tile.vp for tile in player.tableau),
            "vp_chips": player.vp_chips,
            "endgame_bonus": self.endgame_goal_score(player),
            "tracks": self.track_summary(player),
        }

    def track_summary(self, player: Player):
        return {
            color.value: (track.current, track.maximum)
            for color, track in player.tracks.items()
            if track.maximum > 0 or track.current > 0
        }

    def goal_requirement_summary(self, player: Player):
        summary = {}
        for tile in self.committed_goals.get(player.name, []):
            progress, required, label = self.endgame_goal_requirement(player, tile)
            summary[tile.name] = {
                "progress": progress,
                "required": required,
                "label": label,
                "fulfilled": progress >= required,
            }
        return summary
