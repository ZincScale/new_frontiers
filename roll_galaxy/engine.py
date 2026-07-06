from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, Optional

from .model import BuildSlot, CapacityTrack, DieColor, Good, PHASE_COLOR, PHASE_ORDER, Phase, Player, Tile, TileKind
from .tiles import HOME_WORLDS, SAMPLE_TILES, START_FACTION_PAIRS


STRATEGY_BIAS: dict[str, dict[Phase, int]] = {
    "balanced": {
        Phase.EXPLORE: 2,
        Phase.DEVELOP: 2,
        Phase.SETTLE: 2,
        Phase.PRODUCE: 2,
        Phase.SHIP: 2,
    },
    "builder": {
        Phase.EXPLORE: 2,
        Phase.DEVELOP: 5,
        Phase.SETTLE: 2,
        Phase.PRODUCE: 1,
        Phase.SHIP: 2,
    },
    "settler": {
        Phase.EXPLORE: 2,
        Phase.DEVELOP: 1,
        Phase.SETTLE: 5,
        Phase.PRODUCE: 2,
        Phase.SHIP: 2,
    },
    "producer": {
        Phase.EXPLORE: 2,
        Phase.DEVELOP: 1,
        Phase.SETTLE: 2,
        Phase.PRODUCE: 5,
        Phase.SHIP: 4,
    },
    "shipper": {
        Phase.EXPLORE: 2,
        Phase.DEVELOP: 2,
        Phase.SETTLE: 1,
        Phase.PRODUCE: 3,
        Phase.SHIP: 5,
    },
}


@dataclass(frozen=True)
class BatteryConfig:
    starting_capacity: int = 2
    starting_white_capacity: int = 2
    max_track_capacity: int = 6
    starting_credits: int = 1
    minimum_recharge: int = 0
    yellow_mode: str = "alien"
    target_tableau_squares: int = 12
    vp_pool_per_player: int = 16
    max_rounds: int = 40


@dataclass(frozen=True)
class RoundReport:
    round_number: int
    selected: tuple[Phase, ...]
    used_pips: dict[str, int]
    scores: dict[str, int]


class BatteryGame:
    def __init__(
        self,
        players: Optional[Iterable[tuple[str, str]]] = None,
        seed: Optional[int] = None,
        config: Optional[BatteryConfig] = None,
    ):
        self.rng = random.Random(seed)
        self.config = config or BatteryConfig()
        specs = list(players or [("P1", "builder"), ("P2", "producer")])
        self.players = [self.make_player(name, strategy) for name, strategy in specs]
        self.vp_pool = self.config.vp_pool_per_player * len(self.players)
        self.round_number = 0
        self.tile_bag = list(SAMPLE_TILES)
        self.rng.shuffle(self.tile_bag)
        start_pairs = list(START_FACTION_PAIRS)
        home_worlds = list(HOME_WORLDS)
        self.rng.shuffle(start_pairs)
        self.rng.shuffle(home_worlds)
        for player in self.players:
            faction_pair = start_pairs.pop()
            home_world = home_worlds.pop()
            for tile in faction_pair:
                self.add_start_tile(player, tile)
            self.add_start_tile(player, home_world)
            self.scout_tile(player, TileKind.DEVELOPMENT)
            self.scout_tile(player, TileKind.WORLD)

    def make_player(self, name: str, strategy: str) -> Player:
        player = Player(name=name, strategy=strategy, credits=self.config.starting_credits)
        player.tracks = {
            color: CapacityTrack(color=color)
            for color in DieColor
        }
        for phase in PHASE_ORDER:
            color = PHASE_COLOR[phase]
            player.tracks[color] = CapacityTrack(color, self.config.starting_capacity, self.config.starting_capacity)
        player.tracks[DieColor.WHITE] = CapacityTrack(
            DieColor.WHITE,
            self.config.starting_white_capacity,
            self.config.starting_white_capacity,
        )
        player.tracks[DieColor.YELLOW] = CapacityTrack(DieColor.YELLOW, 0, 0)
        return player

    def play(self):
        reports = []
        while not self.game_over():
            reports.append(self.play_round())
        return self.final_scores(), reports

    def play_round(self) -> RoundReport:
        self.round_number += 1
        selected = []
        for player in self.players:
            phase = self.choose_phase(player)
            player.selected_phases.append(phase)
            selected.append(phase)
        selected_phases = tuple(phase for phase in PHASE_ORDER if phase in set(selected))
        used_pips = {}
        for player in self.players:
            before = player.used_pips
            before_completed = player.completed_tiles
            for phase in selected_phases:
                self.resolve_phase(player, phase)
            used_pips[player.name] = player.used_pips - before
            if used_pips[player.name] == 0 and player.completed_tiles == before_completed:
                player.dead_rounds += 1
            self.manage_empire(player)
        return RoundReport(
            self.round_number,
            selected_phases,
            used_pips,
            {player.name: self.score(player) for player in self.players},
        )

    def choose_phase(self, player: Player) -> Phase:
        return max(PHASE_ORDER, key=lambda phase: self.phase_value(player, phase))

    def phase_value(self, player: Player, phase: Phase) -> int:
        bias = STRATEGY_BIAS[player.strategy][phase]
        if phase is Phase.EXPLORE:
            if self.available_capacity(player, phase) <= 0:
                return -20
            need_tiles = int(not player.dev_stack) + int(not player.world_stack)
            return bias + need_tiles * 5 + int(player.credits <= 2) * 2
        if phase is Phase.DEVELOP:
            if not self.can_complete_build(player, phase, player.dev_stack):
                return -20
            return bias + self.stack_need(player.dev_stack)
        if phase is Phase.SETTLE:
            if not self.can_complete_build(player, phase, player.world_stack):
                return -20
            return bias + self.stack_need(player.world_stack)
        if phase is Phase.PRODUCE:
            if self.available_capacity(player, phase) <= 0:
                return -20
            return bias + max(0, self.producible_world_count(player) - len(player.goods)) * 3
        if phase is Phase.SHIP:
            if self.available_capacity(player, phase) <= 0:
                return -20
            return bias + len(player.goods) * 5 + int(player.credits <= 2)
        raise ValueError(f"unknown phase: {phase}")

    def stack_need(self, stack: list[BuildSlot]) -> int:
        if not stack:
            return -4
        return max(0, 7 - stack[0].tile.cost)

    def available_capacity(self, player: Player, phase: Phase) -> int:
        return sum(self.track(player, color).current for color in self.phase_colors(player, phase))

    def resolve_phase(self, player: Player, phase: Phase):
        if phase is Phase.DEVELOP:
            self.resolve_build_phase(player, phase, player.dev_stack)
            return
        if phase is Phase.SETTLE:
            self.resolve_build_phase(player, phase, player.world_stack)
            return
        while self.available_capacity(player, phase) > 0 and self.can_apply_worker(player, phase):
            spent_color = self.spend_phase_pip(player, phase)
            if spent_color is None:
                break
            if not self.apply_worker(player, phase, spent_color):
                self.refund_pip(player, spent_color)
                break
            player.used_pips += 1

    def can_apply_worker(self, player: Player, phase: Phase) -> bool:
        if phase is Phase.EXPLORE:
            return True
        if phase is Phase.DEVELOP:
            return self.can_complete_build(player, phase, player.dev_stack)
        if phase is Phase.SETTLE:
            return self.can_complete_build(player, phase, player.world_stack)
        if phase is Phase.PRODUCE:
            return self.producible_world_count(player) > len(player.goods)
        if phase is Phase.SHIP:
            return bool(player.goods)
        raise ValueError(f"unknown phase: {phase}")

    def spend_phase_pip(self, player: Player, phase: Phase) -> Optional[DieColor]:
        for color in self.phase_colors(player, phase):
            native = self.track(player, color)
            if native.current > 0:
                native.current -= 1
                return color
        return None

    def phase_colors(self, player: Player, phase: Phase) -> tuple[DieColor, ...]:
        if self.config.yellow_mode == "ship" and phase is Phase.SHIP:
            return (DieColor.PURPLE, DieColor.YELLOW, DieColor.WHITE)
        if self.config.yellow_mode == "alien" and self.has_alien_work(player, phase):
            return (PHASE_COLOR[phase], DieColor.YELLOW, DieColor.WHITE)
        return (PHASE_COLOR[phase], DieColor.WHITE)

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

    def refund_pip(self, player: Player, color: DieColor):
        track = self.track(player, color)
        track.current = min(track.maximum, track.current + 1)

    def apply_worker(self, player: Player, phase: Phase, spent_color: DieColor) -> bool:
        if phase is Phase.EXPLORE:
            return self.explore(player)
        if phase is Phase.DEVELOP:
            return False
        if phase is Phase.SETTLE:
            return False
        if phase is Phase.PRODUCE:
            return self.produce(player, spent_color)
        if phase is Phase.SHIP:
            return self.ship(player, spent_color)
        raise ValueError(f"unknown phase: {phase}")

    def is_alien_build(self, stack: list[BuildSlot]) -> bool:
        return bool(stack and self.is_alien_tile(stack[0].tile))

    def explore(self, player: Player) -> bool:
        if not player.dev_stack:
            self.scout_tile(player, TileKind.DEVELOPMENT)
            return True
        if not player.world_stack:
            self.scout_tile(player, TileKind.WORLD)
            return True
        self.gain_credits(player, 2)
        return True

    def scout_tile(self, player: Player, kind: TileKind):
        for index, tile in enumerate(self.tile_bag):
            if tile.kind is kind:
                player_stack = player.dev_stack if kind is TileKind.DEVELOPMENT else player.world_stack
                player_stack.append(BuildSlot(tile))
                del self.tile_bag[index]
                return tile
        return None

    def build(self, player: Player, stack: list[BuildSlot]) -> bool:
        if not stack:
            return False
        tile = stack[0].tile
        phase = Phase.DEVELOP if tile.kind is TileKind.DEVELOPMENT else Phase.SETTLE
        if not self.can_complete_build(player, phase, stack):
            return False
        spent_pips = self.spend_build_cost(player, phase, tile.cost)
        player.used_pips += spent_pips
        self.complete_tile(player, stack.pop(0).tile)
        return True

    def resolve_build_phase(self, player: Player, phase: Phase, stack: list[BuildSlot]):
        if not stack:
            return
        tile = stack[0].tile
        if not self.can_complete_build(player, phase, stack):
            return
        spent_pips = self.spend_build_cost(player, phase, tile.cost)
        player.used_pips += spent_pips
        self.complete_tile(player, stack.pop(0).tile)

    def can_complete_build(self, player: Player, phase: Phase, stack: list[BuildSlot]) -> bool:
        if not stack:
            return False
        return stack[0].tile.cost <= self.available_build_funds(player, phase)

    def available_build_funds(self, player: Player, phase: Phase) -> int:
        return player.credits + self.available_capacity(player, phase)

    def spend_build_cost(self, player: Player, phase: Phase, cost: int) -> int:
        remaining = cost
        spent_pips = 0
        for color in self.phase_colors(player, phase):
            if remaining <= 0:
                break
            track = self.track(player, color)
            spent = min(track.current, remaining)
            track.current -= spent
            remaining -= spent
            spent_pips += spent
        if remaining > 0:
            player.credits -= remaining
            player.credits_spent += remaining
        return spent_pips

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
            self.add_windfall_good(player, tile, tile.grants[0])

    def gain_die(self, player: Player, color: DieColor):
        track = self.track(player, color)
        track.maximum = min(self.config.max_track_capacity, track.maximum + 1)
        track.current = min(track.maximum, track.current + 1)

    def lose_die(self, player: Player, avoid: tuple[DieColor, ...] = ()):
        candidates = [track for track in player.tracks.values() if track.maximum > 0 and track.color not in avoid]
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

    def produce(self, player: Player, spent_color: DieColor) -> bool:
        candidates = self.producible_worlds(player)
        if spent_color is DieColor.YELLOW and self.config.yellow_mode == "alien":
            candidates = [tile for tile in candidates if self.is_alien_tile(tile)]
        if not candidates:
            return False
        world = max(candidates, key=lambda tile: tile.vp)
        player.goods.append(Good(world, spent_color))
        return True

    def ship(self, player: Player, spent_color: DieColor) -> bool:
        if not player.goods:
            return False
        candidates = player.goods
        if spent_color is DieColor.YELLOW and self.config.yellow_mode == "alien":
            candidates = [good for good in candidates if self.is_alien_tile(good.world)]
        if not candidates:
            return False
        good = max(candidates, key=lambda item: item.world.vp)
        player.goods.remove(good)
        vp = 1 + int(good.color is self.world_color(good.world) or good.color is DieColor.WHITE)
        player.vp_chips += min(vp, self.vp_pool)
        self.vp_pool = max(0, self.vp_pool - vp)
        if player.credits <= 2:
            self.gain_credits(player, 3 + good.world.vp // 2)
        return True

    def producible_world_count(self, player: Player) -> int:
        return len(self.producible_worlds(player))

    def producible_worlds(self, player: Player) -> list[Tile]:
        occupied = {good.world.id for good in player.goods}
        return [tile for tile in player.tableau if tile.produces and tile.id not in occupied]

    def manage_empire(self, player: Player):
        if self.recharge_best_track(player, self.config.minimum_recharge):
            player.free_recharged += self.config.minimum_recharge
        else:
            player.blocked_recharge += self.config.minimum_recharge
        while player.credits > 0:
            if not self.recharge_best_track(player, 1):
                player.blocked_recharge += player.credits
                break
            player.credits -= 1
            player.credits_spent += 1
        if player.credits == 0:
            player.credits = 1

    def gain_credits(self, player: Player, amount: int):
        before = player.credits
        player.credits = min(10, player.credits + amount)
        player.credits_earned += player.credits - before

    def recharge_best_track(self, player: Player, amount: int) -> bool:
        candidates = [track for track in player.tracks.values() if track.current < track.maximum]
        if not candidates:
            return False
        track = max(candidates, key=lambda item: (self.track_value(player, item.color), item.maximum - item.current))
        track.current = min(track.maximum, track.current + amount)
        return True

    def track_value(self, player: Player, color: DieColor) -> int:
        if color is DieColor.WHITE:
            return 3
        if color is DieColor.YELLOW:
            return STRATEGY_BIAS[player.strategy][Phase.SHIP]
        phase = next((phase for phase, phase_color in PHASE_COLOR.items() if phase_color is color), None)
        if phase is None:
            return 0
        return STRATEGY_BIAS[player.strategy][phase]

    def track(self, player: Player, color: DieColor) -> CapacityTrack:
        return player.tracks[color]

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
                        "used_pips": player.used_pips,
                        "credits_earned": player.credits_earned,
                        "credits_spent": player.credits_spent,
                        "free_recharged": player.free_recharged,
                        "blocked_recharge": player.blocked_recharge,
                        "completed_tiles": player.completed_tiles,
                        "tracks": self.track_summary(player),
                    },
                )
            )
        return sorted(scored, key=lambda row: (row[1], row[2]["credits"] + sum(v[0] for v in row[2]["tracks"].values())), reverse=True)

    def track_summary(self, player: Player):
        return {
            color.value: (track.current, track.maximum)
            for color, track in player.tracks.items()
            if track.maximum > 0 or track.current > 0
        }
