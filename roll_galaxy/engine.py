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
    "mining": {
        Phase.EXPLORE: 4,
        Phase.DEVELOP: 2,
        Phase.SETTLE: 4,
        Phase.PRODUCE: 3,
        Phase.SHIP: 4,
    },
    "novelty": {
        Phase.EXPLORE: 4,
        Phase.DEVELOP: 2,
        Phase.SETTLE: 4,
        Phase.PRODUCE: 3,
        Phase.SHIP: 4,
    },
    "genes": {
        Phase.EXPLORE: 4,
        Phase.DEVELOP: 2,
        Phase.SETTLE: 4,
        Phase.PRODUCE: 4,
        Phase.SHIP: 3,
    },
    "alien": {
        Phase.EXPLORE: 4,
        Phase.DEVELOP: 3,
        Phase.SETTLE: 4,
        Phase.PRODUCE: 3,
        Phase.SHIP: 3,
    },
    "military": {
        Phase.EXPLORE: 3,
        Phase.DEVELOP: 2,
        Phase.SETTLE: 5,
        Phase.PRODUCE: 2,
        Phase.SHIP: 3,
    },
    "diverse": {
        Phase.EXPLORE: 5,
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
class BatteryConfig:
    starting_capacity: int = 2
    max_track_capacity: int = 6
    starting_credits: int = 1
    max_credits: int = 6
    minimum_recharge: int = 0
    yellow_mode: str = "alien"
    target_tableau_squares: int = 12
    vp_pool_per_player: Optional[int] = None
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
        self.vp_pool_per_player = self.effective_vp_pool_per_player(len(self.players))
        self.vp_pool = self.vp_pool_per_player * len(self.players)
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
            self.config.starting_credits,
            self.config.max_credits,
        )
        player.tracks[DieColor.YELLOW] = CapacityTrack(DieColor.YELLOW, 0, 0)
        return player

    def effective_vp_pool_per_player(self, player_count: int) -> int:
        if self.config.vp_pool_per_player is not None:
            return self.config.vp_pool_per_player
        return 8 if player_count == 2 else 12

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
            empty_worlds = self.producible_world_count(player) - len(player.goods)
            if empty_worlds <= 0:
                return -20
            return bias + empty_worlds * 3
        if phase is Phase.SHIP:
            if self.available_capacity(player, phase) <= 0:
                return -20
            if not player.goods:
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
        if phase is Phase.EXPLORE:
            self.resolve_explore_phase(player)
            return
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

    def spend_phase_pips(self, player: Player, phase: Phase, count: int) -> int:
        spent = 0
        while spent < count:
            spent_color = self.spend_phase_pip(player, phase)
            if spent_color is None:
                break
            spent += 1
        return spent

    def phase_colors(self, player: Player, phase: Phase) -> tuple[DieColor, ...]:
        if self.config.yellow_mode == "ship" and phase is Phase.SHIP:
            return (DieColor.PURPLE, DieColor.YELLOW)
        if self.config.yellow_mode == "alien" and self.has_alien_work(player, phase):
            if phase is Phase.SETTLE:
                return (DieColor.YELLOW,)
            return (PHASE_COLOR[phase], DieColor.YELLOW)
        if phase is Phase.SETTLE:
            return ()
        return (PHASE_COLOR[phase],)

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
        self.gain_credits(player, 2)
        return True

    def resolve_explore_phase(self, player: Player):
        scout_kind = self.explore_scout_kind(player)
        if scout_kind is not None:
            search_depth = self.explore_search_depth(player)
            spent_pips = self.spend_phase_pips(player, Phase.EXPLORE, search_depth)
            if spent_pips:
                self.scout_tile(player, scout_kind, search_depth=spent_pips)
                player.used_pips += spent_pips

        while self.explore_scout_kind(player) is None and self.available_capacity(player, Phase.EXPLORE) > 0:
            spent_color = self.spend_phase_pip(player, Phase.EXPLORE)
            if spent_color is None:
                break
            self.explore(player)
            player.used_pips += 1

    def explore_scout_kind(self, player: Player) -> Optional[TileKind]:
        if not player.dev_stack and not player.world_stack:
            if player.strategy in WORLD_FIRST_STRATEGIES:
                return TileKind.WORLD
            return TileKind.DEVELOPMENT
        if not player.dev_stack:
            return TileKind.DEVELOPMENT
        if not player.world_stack:
            return TileKind.WORLD
        return None

    def explore_search_depth(self, player: Player) -> int:
        available = self.available_capacity(player, Phase.EXPLORE)
        if available <= 0:
            return 0
        if not player.dev_stack and not player.world_stack:
            return min(2, available)
        return 1

    def scout_tile(self, player: Player, kind: TileKind, search_depth: Optional[int] = None):
        if search_depth is not None:
            candidates = []
            for index, tile in enumerate(self.tile_bag):
                if tile.kind is kind:
                    candidates.append((index, tile))
                    if len(candidates) >= search_depth:
                        break
            if not candidates:
                return None
            index, tile = max(candidates, key=lambda item: self.scout_tile_value(player, item[1]))
            player_stack = player.dev_stack if kind is TileKind.DEVELOPMENT else player.world_stack
            player_stack.append(BuildSlot(tile))
            del self.tile_bag[index]
            return tile

        for index, tile in enumerate(self.tile_bag):
            if tile.kind is kind:
                player_stack = player.dev_stack if kind is TileKind.DEVELOPMENT else player.world_stack
                player_stack.append(BuildSlot(tile))
                del self.tile_bag[index]
                return tile
        return None

    def scout_tile_value(self, player: Player, tile: Tile):
        return (
            self.strategy_tile_value(player, tile),
            tile.vp + len(tile.grants) + tile.immediate_credits,
            -tile.cost,
            STRATEGY_BIAS[player.strategy][Phase.DEVELOP if tile.kind is TileKind.DEVELOPMENT else Phase.SETTLE],
        )

    def strategy_tile_value(self, player: Player, tile: Tile) -> int:
        strategy = player.strategy
        value = 0
        if strategy == "builder":
            value += int(tile.kind is TileKind.DEVELOPMENT) * 8
            value += int("end_game" in tile.tags) * 18
            value += int(DieColor.BROWN in tile.grants) * 5
        elif strategy == "settler":
            value += int(tile.kind is TileKind.WORLD) * 8
            value += len(tile.grants) * 3
        elif strategy == "producer":
            value += int(tile.produces) * 16
            value += int(DieColor.GREEN in tile.grants) * 8
            value += int(DieColor.PURPLE in tile.grants) * 5
            value += int(tile.id in {"free_trade_association", "new_economy", "galactic_exchange"}) * 18
            value += int("phase_v" in tile.tags) * 5
        elif strategy == "shipper":
            value += int(tile.produces) * 8
            value += int(DieColor.PURPLE in tile.grants) * 12
            value += int(tile.id in {"free_trade_association", "galactic_bankers", "new_economy"}) * 18
            value += int("phase_v" in tile.tags) * 6
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
            value += int("phase_i" in tile.tags or "phase_iii" in tile.tags) * 4
        elif strategy == "military":
            value += int(DieColor.RED in tile.grants) * 14
            value += int("gray" in tile.tags) * 6
            value += int("rebel" in tile.id) * 8
            value += int(tile.id == "new_galactic_order") * 25
        elif strategy == "diverse":
            value += self.diversity_tile_value(player, tile)
            value += int(tile.id in {"system_diversification", "galactic_exchange"}) * 24
        return value

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

    def build(self, player: Player, stack: list[BuildSlot]) -> bool:
        if not stack:
            return False
        tile = stack[0].tile
        phase = Phase.DEVELOP if tile.kind is TileKind.DEVELOPMENT else Phase.SETTLE
        if not self.can_complete_build(player, phase, stack):
            return False
        spent_pips = self.spend_build_cost(player, phase, tile)
        player.used_pips += spent_pips
        self.complete_tile(player, stack.pop(0).tile)
        return True

    def resolve_build_phase(self, player: Player, phase: Phase, stack: list[BuildSlot]):
        if not stack:
            return
        tile = stack[0].tile
        if not self.can_complete_build(player, phase, stack):
            return
        spent_pips = self.spend_build_cost(player, phase, tile)
        player.used_pips += spent_pips
        self.complete_tile(player, stack.pop(0).tile)

    def can_complete_build(self, player: Player, phase: Phase, stack: list[BuildSlot]) -> bool:
        if not stack:
            return False
        tile = stack[0].tile
        if phase is Phase.SETTLE and self.is_military_world(tile):
            return self.military_level(player) >= tile.cost
        return tile.cost <= self.available_build_funds(player, phase, tile)

    def available_build_funds(self, player: Player, phase: Phase, tile: Tile) -> int:
        if phase is Phase.SETTLE and self.is_military_world(tile):
            return self.military_level(player)
        return player.credits + self.available_capacity(player, phase)

    def spend_build_cost(self, player: Player, phase: Phase, tile: Tile) -> int:
        if phase is Phase.SETTLE and self.is_military_world(tile):
            return 0
        remaining = tile.cost
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
            self.spend_credits(player, remaining)
        return spent_pips

    def is_military_world(self, tile: Tile) -> bool:
        if tile.kind is not TileKind.WORLD:
            return False
        return (
            DieColor.RED in tile.grants
            or "rebel" in tile.id
            or "rebel" in tile.name.lower()
        )

    def military_level(self, player: Player) -> int:
        return self.track(player, DieColor.RED).maximum

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
        if color is DieColor.RED:
            track.current = track.maximum
        else:
            track.current = min(track.maximum, track.current + 1)

    def lose_die(self, player: Player, avoid: tuple[DieColor, ...] = ()):
        candidates = [
            track
            for track in player.tracks.values()
            if track.maximum > 0 and track.color not in avoid and track.color is not DieColor.WHITE
        ]
        if not candidates:
            candidates = [track for track in player.tracks.values() if track.maximum > 0 and track.color is not DieColor.WHITE]
        if not candidates:
            return False
        track = min(candidates, key=lambda item: (self.track_value(player, item.color), item.maximum, item.current))
        track.maximum -= 1
        if track.color is DieColor.RED:
            track.current = track.maximum
        else:
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
            self.spend_credits(player, 1)
        if player.credits == 0:
            self.set_credits(player, 1)

    def gain_credits(self, player: Player, amount: int):
        before = player.credits
        self.set_credits(player, min(self.config.max_credits, player.credits + amount))
        player.credits_earned += player.credits - before

    def spend_credits(self, player: Player, amount: int):
        player.credits -= amount
        player.credits_spent += amount
        self.sync_credit_track(player)

    def set_credits(self, player: Player, amount: int):
        player.credits = max(0, min(self.config.max_credits, amount))
        self.sync_credit_track(player)

    def sync_credit_track(self, player: Player):
        track = self.track(player, DieColor.WHITE)
        track.maximum = self.config.max_credits
        track.current = player.credits

    def recharge_best_track(self, player: Player, amount: int) -> bool:
        candidates = [
            track
            for track in player.tracks.values()
            if track.current < track.maximum and track.color not in (DieColor.RED, DieColor.WHITE)
        ]
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
        return player.vp_chips + sum(tile.vp for tile in player.tableau) + self.endgame_bonus(player)

    def endgame_bonus(self, player: Player) -> int:
        return sum(self.endgame_tile_bonus(player, tile) for tile in player.tableau)

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
            return len(production_worlds) + player.vp_chips // 5
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
                        "tile_vp": sum(tile.vp for tile in player.tableau),
                        "endgame_bonus": self.endgame_bonus(player),
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
