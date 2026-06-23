from __future__ import annotations

import random
from dataclasses import dataclass, replace

from .model import Action, SettleKind, WorldKind


@dataclass(frozen=True)
class Strategy:
    name: str
    develop_weight: int
    explore_weight: int
    settle_weight: int
    produce_weight: int
    trade_weight: int
    military_bias: int
    economy_bias: int


STRATEGIES = {
    "random": Strategy("random", 1, 1, 1, 1, 1, 0, 0),
    "balanced": Strategy("balanced", 3, 3, 3, 2, 2, 1, 1),
    "military": Strategy("military", 2, 3, 5, 1, 1, 4, 0),
    "economy": Strategy("economy", 3, 3, 2, 5, 6, 0, 4),
    "builder": Strategy("builder", 8, 2, 1, 2, 2, 0, 2),
}


class AIPlayer:
    def __init__(self, strategy: str, rng: random.Random):
        if strategy not in STRATEGIES:
            raise ValueError(f"unknown strategy: {strategy}")
        self.strategy = STRATEGIES[strategy]
        self.rng = rng

    def choose_action(self, game, player, available_actions):
        scores = {action: 1 for action in available_actions}
        s = self.strategy

        if Action.DEVELOP in scores:
            affordable = game.affordable_developments(player)
            scores[Action.DEVELOP] += s.develop_weight + len(affordable)
        if Action.EXPLORE in scores:
            scores[Action.EXPLORE] += s.explore_weight
            if len(player.explored_worlds) < 2:
                scores[Action.EXPLORE] += 3
        if Action.SETTLE in scores:
            candidates = game.settle_candidates(player)
            if candidates:
                military_targets = sum(1 for world in candidates if world.settle_kind is SettleKind.MILITARY)
                scores[Action.SETTLE] += s.settle_weight + 3 + military_targets * s.military_bias
            elif player.colonists < 2 and player.explored_worlds:
                scores[Action.SETTLE] += 2
            else:
                scores[Action.SETTLE] = 0
        if Action.PRODUCE in scores:
            scores[Action.PRODUCE] += s.produce_weight + game.empty_production_count(player)
        if Action.TRADE_CONSUME in scores:
            scores[Action.TRADE_CONSUME] += s.trade_weight + len(player.goods)
        if Action.RETREAT in scores and player.credits <= 1:
            scores[Action.RETREAT] += 4
        if Action.RETREAT in scores and not game.settle_candidates(player):
            civilian_gaps = [
                game.civilian_settle_cost(player, world) - player.credits
                for world in player.explored_worlds
                if world.settle_kind is SettleKind.CIVILIAN
            ]
            if civilian_gaps and min(civilian_gaps) > 0:
                scores[Action.RETREAT] += min(civilian_gaps) + s.economy_bias
        if Action.DIPLOMACY in scores and game.vp_pool <= 5:
            scores[Action.DIPLOMACY] += 2

        return self.weighted_choice(scores)

    def choose_development(self, game, player, affordable):
        if not affordable:
            return None
        s = self.strategy
        view = game.player_view(player)

        def value(tile):
            val = tile.vp + tile.spaces
            val += tile.powers.military * s.military_bias
            val += tile.powers.military_settle_vp * (s.military_bias + s.settle_weight)
            val += tile.powers.trade_bonus * s.economy_bias
            val += tile.powers.consume_vp_per_good * (s.economy_bias + 1)
            val += tile.powers.develop_discount * s.develop_weight
            val += tile.powers.settle_discount * s.settle_weight
            if tile.large:
                val += 3
            if tile.score_bonus:
                projected = replace(
                    view,
                    development_count=view.development_count + 1,
                    large_development_count=view.large_development_count + int(tile.large),
                )
                val += tile.score_bonus(projected)
            return val

        return max(affordable, key=value)

    def choose_world_to_keep(self, worlds, count, game=None, player=None):
        s = self.strategy

        def value(world):
            val = world.vp
            if world.settle_kind is SettleKind.MILITARY:
                val += s.military_bias
            if world.kind in (WorldKind.PRODUCTION, WorldKind.WINDFALL):
                val += s.economy_bias
            if game is not None and player is not None:
                if world.settle_kind is SettleKind.MILITARY:
                    gap = max(0, game.military_target_defense(world) - game.military_strength(player))
                    val -= gap * (2 + s.military_bias)
                    val -= game.military_logistics_cost(world, player)
                else:
                    gap = max(0, game.civilian_settle_cost(player, world) - player.credits)
                    val -= gap * 2
                if player.colonists < world.colonists:
                    val -= (world.colonists - player.colonists) * 2
                if game.can_settle(player, world):
                    val += 5
            return val

        return sorted(worlds, key=value, reverse=True)[:count]

    def choose_settle_candidate(self, game, player, candidates):
        if not candidates:
            return None
        s = self.strategy

        def value(world):
            val = world.vp * 2
            if world.settle_kind is SettleKind.MILITARY:
                val += s.military_bias * 2
                val += game.total_powers(player).military_settle_vp
                val -= game.military_logistics_cost(world, player)
            if world.kind in (WorldKind.PRODUCTION, WorldKind.WINDFALL):
                val += s.economy_bias * 2
            val -= world.colonists
            return val

        return max(candidates, key=value)

    def weighted_choice(self, scores):
        total = sum(max(0, score) for score in scores.values())
        pick = self.rng.uniform(0, total)
        running = 0
        for item, score in scores.items():
            running += max(0, score)
            if pick <= running:
                return item
        return next(iter(scores))
