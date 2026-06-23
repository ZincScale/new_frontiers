from nf_engine.engine import Game, GameConfig
from nf_engine.model import Good, Powers, SettleKind, WorldKind, WorldTile
from nf_engine.tiles import DEVELOPMENTS


def test_development_market_tiles_are_unique_once_built():
    game = Game(["builder", "builder"], seed=3)
    choice = game.players[0].ai.choose_development(game, game.players[0], game.affordable_developments(game.players[0]))

    game.action_develop(game.players[0])

    assert choice not in game.development_market
    built_ids = [tile.id for player in game.players for tile in player.developments]
    assert len(built_ids) == len(set(built_ids))


def test_player_view_tracks_good_types_and_military_strength():
    game = Game(["balanced"], seed=1)
    player = game.players[0]
    player.colonies.extend([
        WorldTile("novelty_test", "Novelty Test", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 1, 1, 1, Good.NOVELTY),
        WorldTile("alien_test", "Alien Test", WorldKind.WINDFALL, SettleKind.MILITARY, 1, 1, 1, Good.ALIEN, powers=Powers(military=2)),
    ])
    player.goods["novelty_test"] = Good.NOVELTY
    player.goods["alien_test"] = Good.ALIEN

    view = game.player_view(player)

    assert view.novelty_colony_count == 1
    assert view.alien_colony_count == 1
    assert view.novelty_goods_count == 1
    assert view.alien_goods_count == 1
    assert view.military == 2


def test_expanded_catalog_ids_are_unique():
    game = Game(["balanced", "military", "economy", "builder"], seed=5)
    development_ids = [tile.id for tile in DEVELOPMENTS]
    world_ids = [tile.id for tile in game.world_bag]

    assert len(development_ids) == len(set(development_ids))
    assert len(world_ids) == len(set(world_ids))
    assert len(DEVELOPMENTS) >= 50
    assert len(game.world_bag) >= 80


def test_development_space_limit_is_enforced():
    game = Game(["builder"], seed=7)
    player = game.players[0]
    large = next(tile for tile in game.development_market if tile.large)
    small = next(tile for tile in game.development_market if not tile.large)
    player.developments = [large, large, large, small]

    assert game.development_spaces(player) == 10
    assert game.affordable_developments(player) == []


def test_develop_discount_is_capped_but_selector_bonus_still_applies():
    game = Game(["builder"], seed=9)
    player = game.players[0]
    discount_tiles = [tile for tile in game.development_market if tile.powers.develop_discount]
    player.developments = discount_tiles[:2]
    target = next(tile for tile in game.development_market if tile.cost == 4 and tile not in player.developments)

    assert game.development_cost(player, target) == 3
    assert game.development_cost(player, target, selector_bonus=True) == 2


def test_ai_values_projected_large_development_scoring_bonus():
    game = Game(["builder"], seed=10)
    player = game.players[0]
    player.credits = 9
    filler = [tile for tile in DEVELOPMENTS if not tile.large and not tile.score_bonus][:6]
    player.developments = filler
    federation = next(tile for tile in DEVELOPMENTS if tile.id == "galactic_federation")
    replicators = next(tile for tile in DEVELOPMENTS if tile.id == "advanced_replicators")

    choice = player.ai.choose_development(game, player, [replicators, federation])

    assert choice is federation


def test_military_overmatch_reduces_logistics_cost():
    game = Game(["military"], seed=11)
    player = game.players[0]
    world = WorldTile("test_fort", "Test Fort", WorldKind.GRAY, SettleKind.MILITARY, 4, 1, 4)
    player.colonies.append(WorldTile("test_garrison", "Test Garrison", WorldKind.GRAY, SettleKind.MILITARY, 0, 0, 0, powers=Powers(military=6)))

    assert game.military_logistics_cost(world) == 2
    assert game.military_logistics_cost(world, player) == 1


def test_military_defense_bonus_increases_settlement_threshold():
    game = Game(["military"], seed=15, config=GameConfig(military_defense_bonus=1))
    player = game.players[0]
    world = WorldTile("test_fort", "Test Fort", WorldKind.GRAY, SettleKind.MILITARY, 4, 1, 4)
    player.credits = 3
    player.colonists = 1
    player.explored_worlds.append(world)
    player.colonies.append(WorldTile("test_garrison", "Test Garrison", WorldKind.GRAY, SettleKind.MILITARY, 0, 0, 0, powers=Powers(military=4)))

    assert game.military_target_defense(world) == 5
    assert not game.can_settle(player, world)


def test_military_settlement_spends_discounted_logistics_without_baseline_vp():
    game = Game(["military"], seed=12)
    player = game.players[0]
    player.credits = 2
    player.colonists = 2
    world = WorldTile("test_fort", "Test Fort", WorldKind.GRAY, SettleKind.MILITARY, 4, 1, 4)
    player.colonies.append(WorldTile("test_garrison", "Test Garrison", WorldKind.GRAY, SettleKind.MILITARY, 0, 0, 0, powers=Powers(military=6)))
    player.explored_worlds.append(world)

    game._settle_world(player, world)

    assert world in player.colonies
    assert player.credits == 1
    assert player.vp_chips == 0


def test_new_galactic_order_scores_military_strength():
    game = Game(["military"], seed=14)
    player = game.players[0]
    order = next(tile for tile in DEVELOPMENTS if tile.id == "new_galactic_order")
    player.developments.append(order)

    view = game.player_view(player)

    assert order.score_bonus(view) == game.military_strength(player)
