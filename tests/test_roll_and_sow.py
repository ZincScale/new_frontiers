import pytest

from roll_galaxy.model import DieColor, Good, Phase, Tile, TileKind
from roll_galaxy.tiles import NON_START_TILES
from roll_mancala.model import SECTION_ORDER, Section
from roll_mancala.roll_and_sow import RollAndSowConfig, RollAndSowGame, SowConstruction


def empty_player(player):
    for section in SECTION_ORDER:
        player.sections[section] = []
    player.citizenry = []
    player.dev_stack = []
    player.world_stack = []
    player.tableau = []
    player.goods = []
    player.credits = 1


def goal_tile(tile_id):
    return next(tile for tile in NON_START_TILES if tile.id == tile_id)


def test_opening_rolls_three_white_dice_and_reserves_two():
    game = RollAndSowGame(seed=1)
    player = game.make_player("Test", "balanced")

    assert sum(len(dice) for dice in player.sections.values()) == 3
    assert player.citizenry == [DieColor.WHITE, DieColor.WHITE]
    assert game.inventory(player)[DieColor.WHITE] == 5


def test_player_count_is_limited_to_one_through_four():
    RollAndSowGame(players=(("Solo", "balanced"),), seed=18)

    with pytest.raises(ValueError, match="1 to 4 players"):
        RollAndSowGame(
            players=tuple((f"P{i}", "balanced") for i in range(5)), seed=19
        )


def test_activate_uses_build_dice_then_sows_every_leftover():
    game = RollAndSowGame(seed=2)
    player = game.players[0]
    empty_player(player)
    development = Tile("d", "Development", TileKind.DEVELOPMENT, 2, 2)
    player.dev_stack = [SowConstruction(development)]
    player.sections[Section.DEVELOP] = [DieColor.WHITE, DieColor.BLUE, DieColor.RED]

    game.activate_phase(player, Phase.DEVELOP, selected_by_player=True)

    assert development in player.tableau
    assert player.citizenry == [DieColor.WHITE, DieColor.BLUE]
    assert player.sections[Section.DEVELOP] == []
    assert player.sections[Section.SETTLE] == [DieColor.RED]
    assert player.used_dice == 2
    assert player.sown_dice == 1


def test_build_progress_holds_dice_until_completion():
    game = RollAndSowGame(seed=3)
    player = game.players[0]
    empty_player(player)
    development = Tile("d", "Development", TileKind.DEVELOPMENT, 3, 3)
    build = SowConstruction(development)
    player.dev_stack = [build]
    player.sections[Section.DEVELOP] = [DieColor.WHITE, DieColor.BROWN]

    game.activate_phase(player, Phase.DEVELOP, selected_by_player=True)

    assert build.progress == 2
    assert player.citizenry == []
    assert game.inventory(player) == {DieColor.WHITE: 1, DieColor.BROWN: 1}

    player.sections[Section.DEVELOP] = [DieColor.RED]
    game.activate_phase(player, Phase.DEVELOP, selected_by_player=True)

    assert development in player.tableau
    assert player.citizenry == [DieColor.WHITE, DieColor.BROWN, DieColor.RED]


def test_opponent_selected_phase_forces_activation_and_sowing():
    game = RollAndSowGame(seed=4)
    player = game.players[0]
    empty_player(player)
    player.sections[Section.PRODUCE] = [DieColor.GREEN, DieColor.WHITE]

    game.activate_phase(player, Phase.PRODUCE, selected_by_player=False)

    assert player.sections[Section.PRODUCE] == []
    assert player.sections[Section.SHIP] == [DieColor.GREEN]
    assert player.sections[Section.EXPLORE] == [DieColor.WHITE]
    assert player.opponent_activations == 1
    assert player.forced_sown_dice == 2


def test_producer_becomes_good_and_ship_returns_both_dice_to_citizenry():
    game = RollAndSowGame(seed=5)
    player = game.players[0]
    empty_player(player)
    world = Tile(
        "w",
        "Novelty World",
        TileKind.WORLD,
        1,
        1,
        world_color="Novelty",
        produces=True,
        tags=("novelty",),
    )
    player.tableau = [world]
    player.sections[Section.PRODUCE] = [DieColor.GREEN]

    game.activate_phase(player, Phase.PRODUCE, selected_by_player=True)

    assert player.goods == [Good(world, DieColor.GREEN)]
    assert player.citizenry == []

    player.sections[Section.SHIP] = [DieColor.PURPLE]
    game.activate_phase(player, Phase.SHIP, selected_by_player=True)

    assert player.goods == []
    assert player.citizenry == [DieColor.PURPLE, DieColor.GREEN]
    assert player.credits == 4


def test_cup_gain_rolls_immediately_and_citizenry_recruit_costs_credit():
    game = RollAndSowGame(seed=6)
    player = game.players[0]
    empty_player(player)

    game.gain_die(player, DieColor.BLUE, "cup")
    assert sum(len(dice) for dice in player.sections.values()) == 1

    game.gain_die(player, DieColor.RED, "citizenry")
    assert player.citizenry == [DieColor.RED]
    before_bowls = sum(len(dice) for dice in player.sections.values())

    game.manage_empire(player)

    assert player.citizenry == []
    assert sum(len(dice) for dice in player.sections.values()) == before_bowls + 1
    assert player.credits == 1
    assert player.credits_spent == 1


def test_manage_empire_recalls_a_committed_die_when_all_bowls_are_empty():
    game = RollAndSowGame(seed=28)
    player = game.players[0]
    empty_player(player)
    build = SowConstruction(
        Tile("d", "Development", TileKind.DEVELOPMENT, 3, 3),
        workers=[DieColor.WHITE, DieColor.BROWN],
    )
    player.dev_stack = [build]

    game.manage_empire(player)

    assert build.progress == 1
    assert sum(len(dice) for dice in player.sections.values()) == 1
    assert player.recalled_dice == 1


def test_explore_sees_base_four_plus_one_per_extra_die_and_discards_rejections():
    game = RollAndSowGame(seed=7)
    player = game.players[0]
    empty_player(player)
    player.strategy = "settler"
    worlds = [
        Tile(f"w{i}", f"World {i}", TileKind.WORLD, i + 1, i + 1, produces=True)
        for i in range(5)
    ]
    game.tile_bag = list(worlds)
    game.tile_discard = []
    player.sections[Section.EXPLORE] = [DieColor.WHITE, DieColor.BLUE]

    game.activate_phase(player, Phase.EXPLORE, selected_by_player=True)

    assert player.explore_candidates_seen == 5
    assert len(player.world_stack) == 1
    assert len(game.tile_discard) == 4
    assert game.tile_bag == []
    assert player.citizenry == [DieColor.WHITE, DieColor.BLUE]


def test_newly_sown_die_can_be_used_by_a_later_selected_phase():
    game = RollAndSowGame(seed=8)
    player = game.players[0]
    empty_player(player)
    world = Tile("w", "World", TileKind.WORLD, 1, 1)
    player.world_stack = [SowConstruction(world)]
    player.sections[Section.DEVELOP] = [DieColor.WHITE]

    game.activate_phase(player, Phase.DEVELOP, selected_by_player=False)
    assert player.sections[Section.SETTLE] == [DieColor.WHITE]

    game.activate_phase(player, Phase.SETTLE, selected_by_player=True)
    assert world in player.tableau


def test_two_player_supply_die_adds_a_shared_phase():
    game = RollAndSowGame(
        players=(("P1", "balanced"), ("P2", "builder")),
        seed=9,
        config=RollAndSowConfig(two_player_dummy_phase=True),
    )
    for player in game.players:
        empty_player(player)
        player.sections[Section.DEVELOP] = [DieColor.WHITE]
        player.dev_stack = [
            SowConstruction(Tile(f"d-{player.name}", "Development", TileKind.DEVELOPMENT, 1, 1))
        ]

    report = game.play_round()

    assert Phase.DEVELOP in report.selected
    assert 1 <= len(report.selected) <= 2


def test_spreadsheet_reassign_power_routes_die_only_to_printed_destination():
    game = RollAndSowGame(seed=10)
    player = game.players[0]
    empty_player(player)
    player.tableau = [
        Tile(
            "technology_affinity",
            "Technology Affinity",
            TileKind.DEVELOPMENT,
            2,
            2,
            tags=("reassign",),
        )
    ]
    player.sections[Section.EXPLORE] = [DieColor.WHITE]

    game.apply_reassign_powers(player, Section.SETTLE)
    assert player.sections[Section.EXPLORE] == [DieColor.WHITE]

    game.apply_reassign_powers(player, Section.DEVELOP)
    assert player.sections[Section.EXPLORE] == []
    assert player.sections[Section.DEVELOP] == [DieColor.WHITE]
    assert player.reassigned_dice == 1


def test_spreadsheet_build_discount_reduces_dice_cost():
    game = RollAndSowGame(seed=11)
    player = game.players[0]
    empty_player(player)
    player.tableau = [
        Tile("investment_credits", "Investment Credits", TileKind.DEVELOPMENT, 4, 4)
    ]
    development = Tile("d", "Development", TileKind.DEVELOPMENT, 3, 3)
    player.dev_stack = [SowConstruction(development)]
    player.sections[Section.DEVELOP] = [DieColor.WHITE, DieColor.BROWN]

    game.activate_phase(player, Phase.DEVELOP, selected_by_player=True)

    assert development in player.tableau
    assert player.used_dice == 2


def test_spreadsheet_explorer_power_adds_virtual_candidates():
    game = RollAndSowGame(seed=12)
    player = game.players[0]
    empty_player(player)
    player.strategy = "settler"
    player.tableau = [
        Tile("major_research_labs", "Major Research Labs", TileKind.DEVELOPMENT, 3, 3)
    ]
    worlds = [
        Tile(f"w{i}", f"World {i}", TileKind.WORLD, 1, 1, produces=True)
        for i in range(5)
    ]
    game.tile_bag = worlds
    game.tile_discard = []
    player.sections[Section.EXPLORE] = [DieColor.WHITE]

    game.activate_phase(player, Phase.EXPLORE, selected_by_player=True)

    assert player.explore_candidates_seen == 5
    assert player.virtual_workers == 1


def test_spreadsheet_trade_and_completion_powers_generate_credits():
    game = RollAndSowGame(seed=13)
    player = game.players[0]
    empty_player(player)
    export = Tile("export_duties", "Export Duties", TileKind.DEVELOPMENT, 2, 2)
    public = Tile("public_works", "Public Works", TileKind.DEVELOPMENT, 1, 1)
    world = Tile(
        "w",
        "Novelty World",
        TileKind.WORLD,
        1,
        1,
        world_color="Novelty",
        produces=True,
        tags=("novelty",),
    )
    player.tableau = [export, public, world]
    player.goods = [Good(world, DieColor.BLUE)]
    player.sections[Section.SHIP] = [DieColor.PURPLE]

    game.activate_phase(player, Phase.SHIP, selected_by_player=True)
    assert player.credits == 5  # 1 start + 3 Trade + 1 Export Duties.
    assert player.power_credits == 1

    development = Tile("d", "Development", TileKind.DEVELOPMENT, 1, 1)
    player.dev_stack = [SowConstruction(development)]
    player.sections[Section.DEVELOP] = [DieColor.WHITE]
    game.activate_phase(player, Phase.DEVELOP, selected_by_player=True)
    assert player.credits == 6
    assert player.power_credits == 2


def test_spreadsheet_extra_shipper_uses_good_without_physical_ship_die():
    game = RollAndSowGame(seed=14)
    player = game.players[0]
    empty_player(player)
    docks = Tile("space_docks", "Space Docks", TileKind.DEVELOPMENT, 2, 2)
    world = Tile(
        "w",
        "World",
        TileKind.WORLD,
        1,
        1,
        world_color="Novelty",
        produces=True,
        tags=("novelty",),
    )
    player.tableau = [docks, world]
    player.goods = [Good(world, DieColor.GREEN)]
    player.sections[Section.SHIP] = [DieColor.WHITE]

    game.activate_phase(player, Phase.SHIP, selected_by_player=True)

    # The physical shipper handles the first good if available; set up another
    # activation with only the virtual worker to exercise the power directly.
    player.goods = [Good(world, DieColor.GREEN)]
    player.sections[Section.SHIP] = [DieColor.WHITE]
    player.goods.append(Good(Tile("w2", "World 2", TileKind.WORLD, 1, 1, world_color="Novelty", produces=True), DieColor.BLUE))
    game.activate_phase(player, Phase.SHIP, selected_by_player=True)

    assert player.goods == []
    assert player.virtual_workers == 2


def test_spreadsheet_phase_power_triggers_when_opponent_calls_empty_bowl():
    game = RollAndSowGame(seed=15)
    player = game.players[0]
    empty_player(player)
    player.tableau = [
        Tile("merchant_guild", "Merchant Guild", TileKind.DEVELOPMENT, 3, 3)
    ]

    game.activate_phase(player, Phase.SHIP, selected_by_player=False)

    assert player.credits == 3
    assert player.power_credits == 2
    assert player.activations == 0
    assert player.zero_use_activations == 0


def test_space_tourism_always_pays_one_and_pays_two_with_highest_world():
    game = RollAndSowGame(
        players=(("P1", "balanced"), ("P2", "balanced")), seed=16
    )
    player, opponent = game.players
    empty_player(player)
    empty_player(opponent)
    player.tableau = [
        Tile("space_tourism", "Space Tourism", TileKind.DEVELOPMENT, 4, 4),
        Tile("low", "Low World", TileKind.WORLD, 1, 1),
    ]
    opponent.tableau = [Tile("high", "High World", TileKind.WORLD, 5, 5)]

    game.activate_phase(player, Phase.SHIP, selected_by_player=False)
    assert player.credits == 2

    player.tableau.append(Tile("highest", "Highest World", TileKind.WORLD, 6, 6))
    game.activate_phase(player, Phase.SHIP, selected_by_player=False)
    assert player.credits == 4


def test_mad_scientists_gets_second_route_only_for_unique_most_novelty_worlds():
    game = RollAndSowGame(
        players=(("P1", "balanced"), ("P2", "balanced")), seed=17
    )
    player, opponent = game.players
    empty_player(player)
    empty_player(opponent)
    power = Tile("mad_scientists", "Mad Scientists", TileKind.DEVELOPMENT, 3, 3)
    novelty = Tile(
        "novelty", "Novelty", TileKind.WORLD, 1, 1, tags=("novelty",)
    )
    player.tableau = [power, novelty]
    opponent.tableau = [novelty]
    player.sections[Section.EXPLORE] = [DieColor.WHITE, DieColor.BLUE]

    game.apply_reassign_powers(player, Section.DEVELOP)
    assert len(player.sections[Section.DEVELOP]) == 1

    opponent.tableau = []
    game.apply_reassign_powers(player, Section.SETTLE)
    assert len(player.sections[Section.SETTLE]) == 2


def test_six_cost_goals_use_shared_market_and_stay_out_of_tile_bag():
    game = RollAndSowGame(
        players=(("P1", "builder"), ("P2", "builder"), ("P3", "builder")),
        seed=20,
    )

    assert len(game.endgame_goal_market) == 5
    assert all(len(game.goal_candidates[player.name]) == 2 for player in game.players)
    assert {
        goal.id for goal in game.goal_candidates["P1"]
    } == {goal.id for goal in game.goal_candidates["P2"]}
    assert not any("end_game" in tile.tags for tile in game.tile_bag)


def test_goal_commit_triggers_after_six_completed_tiles_and_keeps_one_candidate():
    game = RollAndSowGame(seed=21)
    player = game.players[0]
    player.completed_tiles = 6
    game.round_number = 7

    game.maybe_commit_goals()

    assert game.goal_commit_round == 7
    assert len(game.committed_goals[player.name]) == 1
    assert game.goal_candidates[player.name] == game.committed_goals[player.name]


def test_goal_commit_triggers_when_half_the_vp_pool_is_gone():
    game = RollAndSowGame(seed=22)
    game.round_number = 4
    game.vp_pool = game.starting_vp_pool // 2

    game.maybe_commit_goals()

    assert game.goal_commit_round == 4
    assert all(game.committed_goals[player.name] for player in game.players)


def test_final_scoring_forces_commit_if_normal_trigger_never_happened():
    game = RollAndSowGame(seed=23)
    assert game.goal_commit_round is None

    game.final_scores()

    assert game.goal_commit_round == 0
    assert all(game.committed_goals[player.name] for player in game.players)


def test_unfulfilled_committed_goal_scores_minus_six():
    game = RollAndSowGame(seed=24)
    player = game.players[0]
    empty_player(player)
    goal = goal_tile("new_economy")
    game.committed_goals[player.name] = [goal]

    assert not game.endgame_goal_fulfilled(player, goal)
    assert game.endgame_goal_score(player) == -6


def test_all_six_cost_goals_use_printed_bonus_formulas_after_minimums():
    game = RollAndSowGame(seed=25)
    player = game.players[0]
    empty_player(player)
    worlds = [
        Tile("novelty-3", "Novelty 3", TileKind.WORLD, 3, 3, world_color="Novelty", produces=True, tags=("novelty",)),
        Tile("novelty-2", "Novelty 2", TileKind.WORLD, 2, 2, world_color="Novelty", produces=True, tags=("novelty",)),
        Tile("alien", "Alien", TileKind.WORLD, 4, 4, world_color="Alien Technology", produces=True, tags=("alien_technology",)),
        Tile("rare-1", "Rare 1", TileKind.WORLD, 2, 2, world_color="Rare Elemental", produces=True, tags=("rare_elemental",)),
        Tile("rare-2", "Rare 2", TileKind.WORLD, 3, 3, world_color="Rare Elemental", produces=True, tags=("rare_elemental",)),
        Tile("genes", "Genes", TileKind.WORLD, 3, 3, world_color="Genes", produces=True, tags=("genes",)),
    ]
    developments = [
        Tile("route-1", "Route 1", TileKind.DEVELOPMENT, 1, 1, tags=("reassign",)),
        Tile("route-2", "Route 2", TileKind.DEVELOPMENT, 2, 2, tags=("reassign",)),
        Tile("plain-3", "Plain 3", TileKind.DEVELOPMENT, 3, 3),
        Tile("plain-4", "Plain 4", TileKind.DEVELOPMENT, 4, 4),
    ]
    player.tableau = worlds + developments
    player.completed_tiles = 8
    player.shipped_goods = 4
    player.vp_chips = 6
    player.citizenry = [
        DieColor.WHITE,
        DieColor.BLUE,
        DieColor.BROWN,
        DieColor.GREEN,
        DieColor.YELLOW,
        DieColor.PURPLE,
        DieColor.RED,
        DieColor.RED,
        DieColor.RED,
        DieColor.RED,
        DieColor.RED,
    ]
    player.goods = [Good(worlds[0], DieColor.BLUE), Good(worlds[2], DieColor.YELLOW)]
    expected = {
        "free_trade_association": 3,
        "galactic_bankers": 5,
        "galactic_exchange": 7,
        "galactic_federation": 6,
        "galactic_renaissance": 3,
        "galactic_reserves": 2,
        "mining_league": 4,
        "new_economy": 3,
        "new_galactic_order": 4,
        "system_diversification": 5,
    }

    for tile_id, bonus in expected.items():
        goal = goal_tile(tile_id)
        assert game.endgame_goal_fulfilled(player, goal), tile_id
        assert game.endgame_tile_bonus(player, goal) == bonus, tile_id
        game.committed_goals[player.name] = [goal]
        assert game.endgame_goal_score(player) == bonus, tile_id


def test_explore_can_claim_an_extra_goal_before_and_after_commit():
    game = RollAndSowGame(seed=26)
    player = game.players[0]
    before = len(game.goal_candidates[player.name])
    first = game.take_extra_goal(player)

    assert first is not None
    assert len(game.goal_candidates[player.name]) == before + 1

    game.goal_commit_round = 5
    second = game.take_extra_goal(player)
    assert second is not None
    assert second in game.committed_goals[player.name]


def test_solo_dummy_deck_reveals_each_phase_once_before_reshuffle():
    game = RollAndSowGame(players=(("Solo", "balanced"),), seed=27)

    first_cycle = [game.draw_solo_phase() for _ in range(5)]

    assert set(first_cycle) == set(Phase)
    assert game.draw_solo_phase() in set(Phase)
