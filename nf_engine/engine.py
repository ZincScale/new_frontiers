from __future__ import annotations

import random
from dataclasses import dataclass, field, replace

from .ai import AIPlayer
from .model import Action, DevelopmentTile, Good, PlayerView, Powers, SettleKind, WorldKind, WorldTile
from .tiles import DEVELOPMENTS, WORLDS


TRADE_VALUE = {
    Good.NOVELTY: 1,
    Good.RARE: 2,
    Good.GENES: 3,
    Good.ALIEN: 4,
}


@dataclass
class Player:
    name: str
    ai: AIPlayer
    credits: int = 4
    colonists: int = 0
    vp_chips: int = 0
    developments: list[DevelopmentTile] = field(default_factory=list)
    explored_worlds: list[WorldTile] = field(default_factory=list)
    colonies: list[WorldTile] = field(default_factory=list)
    goods: dict[str, Good] = field(default_factory=dict)


@dataclass(frozen=True)
class GameConfig:
    vp_per_player: int = 12
    colonists_per_player: int = 20
    max_rounds: int = 80
    explore_draw: int = 7
    development_space_limit: int = 10
    max_develop_discount: int = 1
    military_overmatch_per_logistics_discount: int = 2
    military_defense_bonus: int = 0
    military_logistics: bool = True


class Game:
    def __init__(self, strategies: list[str], seed: int | None = None, config: GameConfig | None = None):
        self.rng = random.Random(seed)
        self.config = config or GameConfig()
        self.players = [
            Player(f"P{i + 1}-{strategy}", AIPlayer(strategy, self.rng))
            for i, strategy in enumerate(strategies)
        ]
        self.priority = list(range(len(self.players)))
        self.vp_pool = self.config.vp_per_player * len(self.players)
        self.colonist_supply = self.config.colonists_per_player * len(self.players)
        self.round = 0
        self.produce_credits = 0
        self.development_market = list(DEVELOPMENTS)
        self.world_bag = list(WORLDS)
        self.rng.shuffle(self.world_bag)
        for player in self.players:
            player.colonies.append(
                WorldTile(
                    id=f"{player.name}_home",
                    name="Home Colony",
                    kind=WorldKind.GRAY,
                    settle_kind=SettleKind.CIVILIAN,
                    cost_or_defense=0,
                    colonists=0,
                    vp=0,
                    powers=Powers(),
                )
            )
            self._gain_colonists(player, 2)

    def play(self):
        while not self.game_over() and self.round < self.config.max_rounds:
            self.play_round()
        return self.final_scores()

    def play_round(self):
        self.round += 1
        available = [
            Action.RETREAT,
            Action.DEVELOP,
            Action.EXPLORE,
            Action.SETTLE,
            Action.PRODUCE,
            Action.TRADE_CONSUME,
            Action.DIPLOMACY,
        ]
        selected: list[tuple[int, Action]] = []
        for player_index in self.priority:
            player = self.players[player_index]
            action = player.ai.choose_action(self, player, available)
            available.remove(action)
            selected.append((player_index, action))

        produced = False
        for selector_index, action in selected:
            if action is Action.PRODUCE:
                produced = True
            self.resolve_action(selector_index, action)
            if self.game_over():
                break
        if not produced:
            self.produce_credits += 1

    def resolve_action(self, selector_index: int, action: Action):
        selector = self.players[selector_index]
        if action is Action.RETREAT:
            selector.credits += 2
        elif action is Action.DEVELOP:
            self.action_develop(selector)
        elif action is Action.EXPLORE:
            self.action_explore(selector)
        elif action is Action.SETTLE:
            self.action_settle(selector)
        elif action is Action.PRODUCE:
            self.action_produce(selector)
        elif action is Action.TRADE_CONSUME:
            self._gain_vp(selector, 1)
            self.action_trade_consume(selector)
        elif action is Action.DIPLOMACY:
            self._gain_vp(selector, 1)
            self._move_to_first_priority(selector_index)

    def action_develop(self, selector: Player):
        for player in self.players:
            affordable = self.affordable_developments(player, selector_bonus=(player is selector))
            choice = player.ai.choose_development(self, player, affordable)
            if choice is None:
                continue
            cost = self.development_cost(player, choice, selector_bonus=(player is selector))
            player.credits -= cost
            player.developments.append(choice)
            self.development_market.remove(choice)

    def action_explore(self, selector: Player):
        for player in self.players:
            draw_count = self.config.explore_draw + self.total_powers(player).explore_extra
            drawn = self._draw_worlds(draw_count)
            if not drawn:
                continue
            keep_count = 2 if player is selector else 1
            keep = player.ai.choose_world_to_keep(drawn, keep_count, self, player)
            player.explored_worlds.extend(keep)
            self._trim_explored_worlds(player)

    def action_settle(self, selector: Player):
        self._gain_colonists(selector, 1)
        for player in self.players:
            candidates = self.settle_candidates(player)
            choice = player.ai.choose_settle_candidate(self, player, candidates)
            if choice is None:
                self._gain_colonists(player, 2)
                continue
            self._settle_world(player, choice)

    def action_produce(self, selector: Player):
        selector.credits += self.produce_credits
        self.produce_credits = 0
        for player in self.players:
            for colony in player.colonies:
                if colony.kind is WorldKind.PRODUCTION and colony.good and colony.id not in player.goods:
                    player.goods[colony.id] = colony.good
            player.credits += self.total_powers(player).produce_credit
        windfalls = [
            colony for colony in selector.colonies
            if colony.kind is WorldKind.WINDFALL and colony.good and colony.id not in selector.goods
        ]
        if windfalls:
            colony = max(windfalls, key=lambda world: TRADE_VALUE[world.good])
            selector.goods[colony.id] = colony.good

    def action_trade_consume(self, selector: Player):
        for player in [selector] + [p for p in self.players if p is not selector]:
            powers = self.total_powers(player)
            if player.goods:
                colony_id, good = max(player.goods.items(), key=lambda item: TRADE_VALUE[item[1]])
                del player.goods[colony_id]
                player.credits += TRADE_VALUE[good] + powers.trade_bonus
            consume_vp = powers.consume_vp_per_good
            consume_credit = powers.consume_credit_per_good
            while player.goods and (consume_vp or consume_credit):
                colony_id, _good = next(iter(player.goods.items()))
                del player.goods[colony_id]
                if consume_vp:
                    self._gain_vp(player, consume_vp)
                player.credits += consume_credit

    def affordable_developments(self, player: Player, selector_bonus: bool = False):
        built = {tile.id for tile in player.developments}
        return [
            tile for tile in self.development_market
            if tile.id not in built
            and self.development_cost(player, tile, selector_bonus) <= player.credits
            and self.can_add_development(player, tile)
        ]

    def development_cost(self, player: Player, tile: DevelopmentTile, selector_bonus: bool = False):
        discount = min(self.total_powers(player).develop_discount, self.config.max_develop_discount)
        if selector_bonus:
            discount += 1
        return max(0, tile.cost - discount)

    def development_spaces(self, player: Player):
        return sum(tile.spaces for tile in player.developments)

    def can_add_development(self, player: Player, tile: DevelopmentTile):
        return self.development_spaces(player) + tile.spaces <= self.config.development_space_limit

    def settle_candidates(self, player: Player):
        return [world for world in player.explored_worlds if self.can_settle(player, world)]

    def can_settle(self, player: Player, world: WorldTile):
        if player.colonists < world.colonists:
            return False
        if world.settle_kind is SettleKind.CIVILIAN:
            return player.credits >= self.civilian_settle_cost(player, world)
        return self.military_strength(player) >= self.military_target_defense(world) and player.credits >= self.military_logistics_cost(world, player)

    def civilian_settle_cost(self, player: Player, world: WorldTile):
        return max(0, world.cost_or_defense - self.total_powers(player).settle_discount)

    def military_target_defense(self, world: WorldTile):
        return world.cost_or_defense + self.config.military_defense_bonus

    def military_logistics_cost(self, world: WorldTile, player: Player | None = None):
        if not self.config.military_logistics:
            return 0
        if world.cost_or_defense >= 6:
            cost = 3
        elif world.cost_or_defense >= 4:
            cost = 2
        elif world.cost_or_defense >= 2:
            cost = 1
        else:
            cost = 0

        if player is not None and self.config.military_overmatch_per_logistics_discount > 0:
            overmatch = max(0, self.military_strength(player) - self.military_target_defense(world))
            cost -= overmatch // self.config.military_overmatch_per_logistics_discount
        return max(0, cost)

    def military_strength(self, player: Player):
        return self.total_powers(player).military

    def empty_production_count(self, player: Player):
        return sum(
            1 for colony in player.colonies
            if colony.kind is WorldKind.PRODUCTION and colony.good and colony.id not in player.goods
        )

    def total_powers(self, player: Player):
        powers = Powers()
        for tile in [*player.developments, *player.colonies]:
            powers = Powers(
                military=powers.military + tile.powers.military,
                develop_discount=powers.develop_discount + tile.powers.develop_discount,
                settle_discount=powers.settle_discount + tile.powers.settle_discount,
                explore_extra=powers.explore_extra + tile.powers.explore_extra,
                trade_bonus=powers.trade_bonus + tile.powers.trade_bonus,
                consume_vp_per_good=powers.consume_vp_per_good + tile.powers.consume_vp_per_good,
                consume_credit_per_good=powers.consume_credit_per_good + tile.powers.consume_credit_per_good,
                produce_credit=powers.produce_credit + tile.powers.produce_credit,
                military_settle_vp=powers.military_settle_vp + tile.powers.military_settle_vp,
            )
        return powers

    def final_scores(self):
        scores = []
        for player in self.players:
            score = player.vp_chips
            score += sum(tile.vp for tile in player.developments)
            score += sum(tile.vp for tile in player.colonies)
            view = self.player_view(player)
            score += sum(tile.score_bonus(view) for tile in player.developments if tile.score_bonus)
            score += sum(tile.score_bonus(view) for tile in player.colonies if tile.score_bonus)
            scores.append((player.name, score, self.tie_breaker(player), self.player_summary(player)))
        return sorted(scores, key=lambda item: (item[1], item[2]), reverse=True)

    def player_summary(self, player: Player):
        return {
            "credits": player.credits,
            "colonists": player.colonists,
            "vp_chips": player.vp_chips,
            "developments": len(player.developments),
            "dev_spaces": self.development_spaces(player),
            "colonies": len(player.colonies),
            "military": self.military_strength(player),
            "goods": len(player.goods),
        }

    def player_view(self, player: Player):
        colonies_by_good = {good: 0 for good in Good}
        goods_by_type = {good: 0 for good in Good}
        for colony in player.colonies:
            if colony.good:
                colonies_by_good[colony.good] += 1
        for good in player.goods.values():
            goods_by_type[good] += 1

        return PlayerView(
            development_count=len(player.developments),
            large_development_count=sum(1 for tile in player.developments if tile.large),
            colony_count=len(player.colonies),
            military_colony_count=sum(1 for tile in player.colonies if tile.settle_kind is SettleKind.MILITARY),
            production_colony_count=sum(1 for tile in player.colonies if tile.kind is WorldKind.PRODUCTION),
            windfall_colony_count=sum(1 for tile in player.colonies if tile.kind is WorldKind.WINDFALL),
            novelty_colony_count=colonies_by_good[Good.NOVELTY],
            rare_colony_count=colonies_by_good[Good.RARE],
            genes_colony_count=colonies_by_good[Good.GENES],
            alien_colony_count=colonies_by_good[Good.ALIEN],
            goods_count=len(player.goods),
            novelty_goods_count=goods_by_type[Good.NOVELTY],
            rare_goods_count=goods_by_type[Good.RARE],
            genes_goods_count=goods_by_type[Good.GENES],
            alien_goods_count=goods_by_type[Good.ALIEN],
            vp_chips=player.vp_chips,
            military=self.military_strength(player),
        )

    def tie_breaker(self, player: Player):
        return player.credits + len(player.goods)

    def game_over(self):
        if self.vp_pool <= 0:
            return True
        if self.colonist_supply < 5:
            return True
        for player in self.players:
            if self.development_spaces(player) >= self.config.development_space_limit:
                return True
            if len(player.colonies) > 7:
                return True
        return False

    def _settle_world(self, player: Player, world: WorldTile):
        player.colonists -= world.colonists
        if world.settle_kind is SettleKind.CIVILIAN:
            player.credits -= self.civilian_settle_cost(player, world)
        else:
            player.credits -= self.military_logistics_cost(world, player)
        player.explored_worlds.remove(world)
        player.colonies.append(world)
        if world.kind is WorldKind.WINDFALL and world.good:
            player.goods[world.id] = world.good
        if world.settle_kind is SettleKind.MILITARY:
            self._gain_vp(player, self.total_powers(player).military_settle_vp)

    def _gain_colonists(self, player: Player, count: int):
        gained = min(count, self.colonist_supply)
        player.colonists += gained
        self.colonist_supply -= gained

    def _gain_vp(self, player: Player, count: int):
        gained = min(count, self.vp_pool)
        player.vp_chips += gained
        self.vp_pool -= gained

    def _draw_worlds(self, count: int):
        drawn = []
        for _ in range(count):
            if not self.world_bag:
                self.world_bag = [replace(world, id=f"{world.id}_reshuffle_{self.round}") for world in WORLDS]
                self.rng.shuffle(self.world_bag)
            drawn.append(self.world_bag.pop())
        return drawn

    def _trim_explored_worlds(self, player: Player):
        total = len(player.explored_worlds) + len(player.colonies)
        if total <= 9:
            return
        excess = total - 9
        player.explored_worlds = player.explored_worlds[:-excess]

    def _move_to_first_priority(self, player_index: int):
        if player_index in self.priority:
            self.priority.remove(player_index)
        self.priority.insert(0, player_index)
