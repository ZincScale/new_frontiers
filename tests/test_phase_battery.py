from phase_battery.engine import PhaseBatteryConfig, PhaseBatteryGame
from phase_battery.solo import (
    SOLO_DIFFICULTIES,
    SOLO_GOAL_COMMIT_ROUND,
    SOLO_ROUNDS,
    PhaseBatterySoloGame,
)
from roll_galaxy.model import BuildSlot, DieColor, Good, Phase, Tile, TileKind


def test_round_resolves_selected_phases_in_turn_order():
    game = PhaseBatteryGame([("P1", "builder"), ("P2", "producer")], seed=1)
    p1, p2 = game.players
    game.tile_bag = []
    p1.dev_stack = [BuildSlot(Tile("d", "Development", TileKind.DEVELOPMENT, 1, 1))]
    p1.world_stack = []
    p2.dev_stack = []
    p2.world_stack = [BuildSlot(Tile("w", "World", TileKind.WORLD, 1, 1))]
    p1.tracks[DieColor.BROWN].current = 1
    p2.credits = 1
    game.sync_credit_track(p2)

    report = game.play_round()

    assert report.phases == tuple(sorted(report.phases, key=lambda phase: (Phase.EXPLORE, Phase.DEVELOP, Phase.SETTLE, Phase.PRODUCE, Phase.SHIP).index(phase)))
    assert set(report.phases).issubset(set((Phase.EXPLORE, Phase.DEVELOP, Phase.SETTLE, Phase.PRODUCE, Phase.SHIP)))


def test_credits_are_unlimited_chips_and_red_is_the_only_settle_track():
    game = PhaseBatteryGame([("P1", "builder")], seed=16)
    player = game.players[0]

    game.set_credits(player, 40)

    assert player.credits == 40
    assert DieColor.WHITE not in player.tracks
    assert game.track(player, DieColor.RED).current >= 1
    assert game.track(player, DieColor.RED).maximum >= 1
    assert "white" not in game.player_summary(player)["tracks"]


def test_player_with_no_ready_pips_selects_no_phase():
    game = PhaseBatteryGame([("P1", "builder")], seed=21)
    player = game.players[0]
    for track in player.tracks.values():
        track.current = 0
    player.dev_stack = [BuildSlot(Tile("d", "Development", TileKind.DEVELOPMENT, 1, 1))]
    player.world_stack = [BuildSlot(Tile("w", "World", TileKind.WORLD, 1, 1))]

    assert game.choose_phase(player) is None
    assert game.selected_phases() == ()


def test_two_player_game_selects_one_eligible_phase_per_player():
    game = PhaseBatteryGame([("P1", "builder"), ("P2", "producer")], seed=24)
    p1, p2 = game.players
    for player in game.players:
        for track in player.tracks.values():
            track.current = 0
        player.dev_stack = []
        player.world_stack = []
        player.goods = []
    p1.tracks[DieColor.BLUE].current = 1
    p1.tracks[DieColor.BROWN].current = 1
    p1.dev_stack = [BuildSlot(Tile("d", "Development", TileKind.DEVELOPMENT, 1, 1))]
    p2.tracks[DieColor.GREEN].current = 1
    p2.tracks[DieColor.PURPLE].current = 1
    prod = Tile("prod", "Production World", TileKind.WORLD, 1, 1, produces=True)
    stocked = Tile("stocked", "Stocked World", TileKind.WORLD, 1, 1, produces=True)
    p2.tableau = [prod, stocked]
    game.add_windfall_good(p2, stocked, DieColor.GREEN)

    assert game.phase_selection_count() == 1
    selected = set(game.selected_phases())
    assert len(selected & {Phase.EXPLORE, Phase.DEVELOP}) == 1
    assert len(selected & {Phase.PRODUCE, Phase.SHIP}) == 1


def test_solo_game_selects_two_eligible_phases():
    game = PhaseBatteryGame([("P1", "builder")], seed=24)

    assert game.phase_selection_count() == 2


def test_main_tracks_start_with_one_ready_pip_before_tile_gains():
    game = PhaseBatteryGame([("P1", "builder")], seed=27)
    player = game.make_player("Fresh", "builder")

    for color in (
        DieColor.BLUE,
        DieColor.BROWN,
        DieColor.RED,
        DieColor.GREEN,
        DieColor.PURPLE,
    ):
        assert player.tracks[color].current == 1
        assert player.tracks[color].maximum == 1
    assert player.tracks[DieColor.YELLOW].current == 0
    assert player.tracks[DieColor.YELLOW].maximum == 0


def test_three_player_game_selects_one_eligible_phase_per_player():
    game = PhaseBatteryGame([("P1", "builder"), ("P2", "producer"), ("P3", "settler")], seed=25)

    assert game.phase_selection_count() == 1


def test_explore_requires_ready_blue_pip_to_select():
    game = PhaseBatteryGame([("P1", "builder")], seed=22)
    player = game.players[0]
    for track in player.tracks.values():
        track.current = 0
    player.dev_stack = []
    player.world_stack = []
    player.tracks[DieColor.BROWN].current = 1
    player.dev_stack = [BuildSlot(Tile("d", "Development", TileKind.DEVELOPMENT, 1, 1))]

    assert not game.can_select_phase(player, Phase.EXPLORE)
    assert game.can_select_phase(player, Phase.DEVELOP)
    assert game.choose_phase(player) is Phase.DEVELOP


def test_explore_scout_gets_three_bonus_candidates():
    game = PhaseBatteryGame([("P1", "novelty")], seed=26)
    player = game.players[0]
    player.dev_stack = []
    player.world_stack = [BuildSlot(Tile("w", "Queued World", TileKind.WORLD, 1, 1))]
    player.tracks[DieColor.BLUE].current = 1
    ordinary_1 = Tile("d-ordinary-1", "Ordinary 1", TileKind.DEVELOPMENT, 1, 1)
    ordinary_2 = Tile("d-ordinary-2", "Ordinary 2", TileKind.DEVELOPMENT, 1, 1)
    ordinary_3 = Tile("d-ordinary-3", "Ordinary 3", TileKind.DEVELOPMENT, 1, 1)
    blue = Tile(
        "d-blue",
        "Blue Grant",
        TileKind.DEVELOPMENT,
        2,
        2,
        grants=(DieColor.BLUE,),
    )
    game.tile_bag = [ordinary_1, ordinary_2, ordinary_3, blue]

    game.resolve_phase(player, Phase.EXPLORE)

    assert [slot.tile for slot in player.dev_stack] == [blue]
    assert player.tracks[DieColor.BLUE].current == 0


def test_red_grant_world_pays_its_full_cost_with_red_settle_pips():
    game = PhaseBatteryGame([("P1", "military")], seed=2)
    player = game.players[0]
    player.tracks[DieColor.RED].current = 3
    player.tracks[DieColor.RED].maximum = 3
    world = Tile(
        "gray-red",
        "Gray Red-Grant World",
        TileKind.WORLD,
        3,
        3,
        grants=(DieColor.RED,),
        placement="citizenry",
        world_color="gray",
    )
    player.world_stack = [BuildSlot(world)]

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == []
    assert world in player.tableau
    assert player.tracks[DieColor.RED].current == 0
    assert player.tracks[DieColor.RED].maximum == 4


def test_develop_pips_create_partial_progress_without_spending_credits():
    game = PhaseBatteryGame([("P1", "builder")], seed=6)
    player = game.players[0]
    player.credits = 0
    game.sync_credit_track(player)
    player.tracks[DieColor.BROWN].current = 2
    tile = Tile("d-big", "Large Development", TileKind.DEVELOPMENT, 4, 4)
    player.dev_stack = [BuildSlot(tile)]

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack == [BuildSlot(tile, progress=2)]
    assert player.tracks[DieColor.BROWN].current == 0
    assert player.credits == 0
    assert player.credits_spent == 0
    assert player.used_pips == 2


def test_develop_completes_later_from_stored_progress():
    game = PhaseBatteryGame([("P1", "builder")], seed=7)
    player = game.players[0]
    player.credits = 1
    game.sync_credit_track(player)
    player.tracks[DieColor.BROWN].current = 2
    tile = Tile("d-big", "Large Development", TileKind.DEVELOPMENT, 4, 4)
    player.dev_stack = [BuildSlot(tile, progress=2)]

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack == []
    assert tile in player.tableau
    assert player.tracks[DieColor.BROWN].current == 0
    assert player.credits == 1
    assert player.credits_earned == 0
    assert player.credits_spent == 0
    assert player.used_pips == 2


def test_completed_development_does_not_create_special_credits():
    game = PhaseBatteryGame([("P1", "builder")], seed=20)
    player = game.players[0]
    existing = Tile("existing-dev", "Existing Development", TileKind.DEVELOPMENT, 1, 1)
    player.tableau.append(existing)
    player.credits = 0
    game.sync_credit_track(player)
    player.tracks[DieColor.BROWN].current = 1
    tile = Tile("d-credit", "Credit Development", TileKind.DEVELOPMENT, 1, 1)
    player.dev_stack = [BuildSlot(tile)]
    earned_before = player.credits_earned

    game.resolve_phase(player, Phase.DEVELOP)

    assert tile in player.tableau
    assert player.credits == 0
    assert player.credits_earned == earned_before

    game.manage_empire(player)

    assert player.credits_earned == earned_before


def test_develop_can_complete_multiple_developments_in_one_phase():
    game = PhaseBatteryGame([("P1", "builder")], seed=8)
    player = game.players[0]
    player.credits = 0
    game.sync_credit_track(player)
    player.tracks[DieColor.BROWN].current = 2
    first = Tile("d1", "Development 1", TileKind.DEVELOPMENT, 1, 1)
    second = Tile("d2", "Development 2", TileKind.DEVELOPMENT, 1, 1)
    player.dev_stack = [BuildSlot(first), BuildSlot(second)]

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack == []
    assert first in player.tableau
    assert second in player.tableau
    assert player.tracks[DieColor.BROWN].current == 0
    assert player.used_pips == 2


def test_develop_can_skip_blocking_top_card_for_affordable_development():
    game = PhaseBatteryGame([("P1", "builder")], seed=9)
    player = game.players[0]
    player.credits = 0
    game.sync_credit_track(player)
    player.tracks[DieColor.BROWN].current = 1
    expensive = Tile("d-big", "Large Development", TileKind.DEVELOPMENT, 6, 6)
    cheap = Tile("d-cheap", "Cheap Development", TileKind.DEVELOPMENT, 1, 1, grants=(DieColor.BROWN,))
    player.dev_stack = [BuildSlot(expensive), BuildSlot(cheap)]

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack == [BuildSlot(expensive)]
    assert cheap in player.tableau
    assert expensive not in player.tableau


def test_builder_values_worlds_that_support_planned_six_cost_development():
    game = PhaseBatteryGame([("P1", "builder")], seed=17)
    player = game.players[0]
    player.dev_stack = [
        BuildSlot(Tile("free_trade_association", "Free Trade Association", TileKind.DEVELOPMENT, 6, 6, tags=("end_game",)))
    ]
    novelty = Tile("novelty-world", "Novelty World", TileKind.WORLD, 2, 2, world_color="Novelty", produces=True, tags=("novelty",))
    plain = Tile("plain-world", "Plain World", TileKind.WORLD, 2, 2, world_color="gray")

    assert game.strategy_tile_value(player, novelty) > game.strategy_tile_value(player, plain)


def test_builder_scouts_world_support_after_queuing_six_cost_plan():
    game = PhaseBatteryGame([("P1", "builder")], seed=19)
    player = game.players[0]
    player.dev_stack = [
        BuildSlot(Tile("new_economy", "New Economy", TileKind.DEVELOPMENT, 6, 6, tags=("end_game",)))
    ]
    player.world_stack = [
        BuildSlot(Tile("starter-world", "Starter World", TileKind.WORLD, 1, 1))
    ]

    assert game.explore_scout_kind(player) is TileKind.WORLD


def test_builder_values_six_cost_developments_by_current_bonus_fit():
    game = PhaseBatteryGame([("P1", "builder")], seed=18)
    player = game.players[0]
    player.tableau = [
        Tile("rare-1", "Rare World 1", TileKind.WORLD, 2, 2, world_color="Rare Elements", tags=("rare_elemental",)),
        Tile("rare-2", "Rare World 2", TileKind.WORLD, 2, 2, world_color="Rare Elements", tags=("rare_elemental",)),
    ]
    player.tracks[DieColor.BROWN].maximum = 4
    mining = Tile("mining_league", "Mining League", TileKind.DEVELOPMENT, 6, 6, tags=("end_game",))
    federation = Tile("galactic_federation", "Galactic Federation", TileKind.DEVELOPMENT, 6, 6, tags=("end_game",))

    assert game.strategy_tile_value(player, mining) > game.strategy_tile_value(player, federation)


def test_committed_goal_with_nonzero_bonus_still_penalizes_if_minimum_not_met():
    game = PhaseBatteryGame([("P1", "producer")], seed=27)
    player = game.players[0]
    goal = Tile("new_economy", "New Economy", TileKind.DEVELOPMENT, 6, 6, tags=("end_game",))
    player.tableau = [Tile("prod", "Production World", TileKind.WORLD, 1, 1, produces=True)]
    game.committed_goals[player.name] = [goal]

    assert game.endgame_tile_bonus(player, goal) == 1
    assert not game.endgame_goal_fulfilled(player, goal)
    assert game.endgame_goal_score(player) == -6


def test_committed_goal_scores_bonus_when_minimum_is_met():
    game = PhaseBatteryGame([("P1", "producer")], seed=28)
    player = game.players[0]
    goal = Tile("new_economy", "New Economy", TileKind.DEVELOPMENT, 6, 6, tags=("end_game",))
    player.tableau = [
        Tile(f"prod-{index}", f"Production World {index}", TileKind.WORLD, 1, 1, produces=True)
        for index in range(3)
    ]
    game.committed_goals[player.name] = [goal]

    assert game.endgame_goal_fulfilled(player, goal)
    assert game.endgame_goal_score(player) == 3
    assert game.player_summary(player)["goal_requirements"]["New Economy"]["fulfilled"]


def test_settle_can_complete_multiple_worlds_in_one_phase():
    game = PhaseBatteryGame([("P1", "settler")], seed=10)
    player = game.players[0]
    player.credits = 2
    game.sync_credit_track(player)
    first = Tile("w1", "World 1", TileKind.WORLD, 1, 1, world_color="Novelty")
    second = Tile("w2", "World 2", TileKind.WORLD, 1, 1, world_color="Genes")
    player.world_stack = [BuildSlot(first), BuildSlot(second)]
    player.tracks[DieColor.RED].current = 3
    player.tracks[DieColor.RED].maximum = 3

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == []
    assert first in player.tableau
    assert second in player.tableau
    assert player.credits == 2
    assert player.credits_spent == 0
    assert player.tracks[DieColor.RED].current == 1


def test_settle_pips_create_partial_world_progress():
    game = PhaseBatteryGame([("P1", "settler")], seed=11)
    player = game.players[0]
    player.tracks[DieColor.RED].current = 2
    game.sync_credit_track(player)
    world = Tile("w-big", "Large World", TileKind.WORLD, 5, 5)
    player.world_stack = [BuildSlot(world)]

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == [BuildSlot(world, progress=2)]
    assert world not in player.tableau
    assert player.tracks[DieColor.RED].current == 0


def test_settle_completes_later_from_stored_world_progress():
    game = PhaseBatteryGame([("P1", "settler")], seed=29)
    player = game.players[0]
    player.tracks[DieColor.RED].current = 2
    world = Tile("w-big", "Large World", TileKind.WORLD, 5, 5)
    player.world_stack = [BuildSlot(world, progress=3)]

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == []
    assert world in player.tableau
    assert player.tracks[DieColor.RED].current == 0
    assert player.used_pips == 2


def test_red_can_recharge_with_credits():
    game = PhaseBatteryGame([("P1", "military")], seed=4)
    player = game.players[0]
    player.tracks[DieColor.RED].current = 0
    player.tracks[DieColor.RED].maximum = 3
    player.credits = 1
    game.sync_credit_track(player)

    game.manage_empire(player)

    assert player.tracks[DieColor.RED].current == 1
    assert player.credits == 1
    assert player.credits_spent == 1


def test_cup_die_gain_recharges_for_free_during_manage_empire():
    game = PhaseBatteryGame([("P1", "balanced")], seed=31)
    player = game.players[0]
    player.tracks[DieColor.BLUE].current = 0
    player.tracks[DieColor.BLUE].maximum = 2
    player.credits = 0
    tile = Tile(
        "cup-grant",
        "Cup Grant",
        TileKind.DEVELOPMENT,
        1,
        1,
        grants=(DieColor.BLUE,),
        placement="cup",
    )

    game.complete_tile(player, tile)

    assert player.tracks[DieColor.BLUE].maximum == 3
    assert player.tracks[DieColor.BLUE].current == 0

    game.manage_empire(player)

    assert player.tracks[DieColor.BLUE].current == 1
    assert game.player_summary(player)["cup_recharges"] == 1


def test_citizenry_die_gain_adds_capacity_without_readiness():
    game = PhaseBatteryGame([("P1", "balanced")], seed=32)
    player = game.players[0]
    player.tracks[DieColor.GREEN].current = 0
    player.tracks[DieColor.GREEN].maximum = 2
    player.credits = 0
    before_unready = game.player_summary(player)["unready_die_gains"]
    tile = Tile(
        "citizenry-grant",
        "Citizenry Grant",
        TileKind.WORLD,
        1,
        1,
        grants=(DieColor.GREEN,),
        placement="citizenry",
    )

    game.complete_tile(player, tile)
    game.manage_empire(player)

    assert player.tracks[DieColor.GREEN].maximum == 3
    assert player.tracks[DieColor.GREEN].current == 0
    assert game.player_summary(player)["unready_die_gains"] == before_unready + 1


def test_world_die_gain_adds_capacity_and_a_good_but_not_readiness():
    game = PhaseBatteryGame([("P1", "producer")], seed=33)
    player = game.players[0]
    player.tracks[DieColor.BROWN].current = 0
    player.tracks[DieColor.BROWN].maximum = 2
    player.goods = []
    tile = Tile(
        "windfall",
        "Windfall World",
        TileKind.WORLD,
        1,
        1,
        grants=(DieColor.BROWN,),
        placement="world",
        world_color="Rare Elemental",
        produces=True,
    )

    game.complete_tile(player, tile)

    assert player.tracks[DieColor.BROWN].maximum == 3
    assert player.tracks[DieColor.BROWN].current == 0
    assert len(player.goods) == 1
    assert player.goods[0].world == tile


def test_starting_cup_die_is_ready_for_the_first_round():
    game = PhaseBatteryGame([("P1", "balanced")], seed=34)
    player = game.players[0]
    player.tracks[DieColor.PURPLE].current = 0
    player.tracks[DieColor.PURPLE].maximum = 2
    tile = Tile(
        "starting-cup",
        "Starting Cup",
        TileKind.WORLD,
        1,
        1,
        grants=(DieColor.PURPLE,),
        placement="cup",
    )

    game.add_start_tile(player, tile)

    assert player.tracks[DieColor.PURPLE].maximum == 3
    assert player.tracks[DieColor.PURPLE].current == 1


def test_reassign_power_routes_a_pip_without_changing_track_identity():
    game = PhaseBatteryGame([("P1", "builder")], seed=35)
    player = game.players[0]
    for track in player.tracks.values():
        track.current = 0
    player.tracks[DieColor.BLUE].current = 1
    player.tableau = [
        Tile("router", "Router", TileKind.DEVELOPMENT, 1, 1, tags=("reassign",))
    ]
    target = Tile("target", "Target", TileKind.DEVELOPMENT, 1, 1)
    player.dev_stack = [BuildSlot(target)]
    blue_max = player.tracks[DieColor.BLUE].maximum
    brown_max = player.tracks[DieColor.BROWN].maximum
    game.start_reassign_round(player)

    game.resolve_phase(player, Phase.DEVELOP)

    assert target in player.tableau
    assert player.tracks[DieColor.BLUE].current == 0
    assert player.tracks[DieColor.BLUE].maximum == blue_max
    assert player.tracks[DieColor.BROWN].maximum == brown_max
    assert game.player_summary(player)["reassigned_pips"] == 1


def test_each_generic_reassign_power_routes_only_one_pip_per_round():
    game = PhaseBatteryGame([("P1", "builder")], seed=36)
    player = game.players[0]
    for track in player.tracks.values():
        track.current = 0
    player.tracks[DieColor.BLUE].current = 2
    player.tableau = [
        Tile("router", "Router", TileKind.DEVELOPMENT, 1, 1, tags=("reassign",))
    ]
    target = Tile("target", "Target", TileKind.DEVELOPMENT, 2, 2)
    player.dev_stack = [BuildSlot(target)]
    game.start_reassign_round(player)

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack == [BuildSlot(target, progress=1)]
    assert player.tracks[DieColor.BLUE].current == 1
    assert game.player_summary(player)["reassigned_pips"] == 1


def test_routable_pip_does_not_make_its_destination_phase_eligible():
    game = PhaseBatteryGame([("P1", "builder")], seed=37)
    player = game.players[0]
    for track in player.tracks.values():
        track.current = 0
    player.tracks[DieColor.BLUE].current = 1
    player.tableau = [
        Tile("router", "Router", TileKind.DEVELOPMENT, 1, 1, tags=("reassign",))
    ]
    player.dev_stack = [BuildSlot(Tile("target", "Target", TileKind.DEVELOPMENT, 1, 1))]
    game.start_reassign_round(player)

    assert not game.can_select_phase(player, Phase.DEVELOP)


def test_reassign_into_produce_performs_the_normal_produce_action():
    game = PhaseBatteryGame([("P1", "balanced")], seed=42)
    player = game.players[0]
    for track in player.tracks.values():
        track.current = 0
    player.tracks[DieColor.BLUE].current = 1
    world = Tile("produce", "Production World", TileKind.WORLD, 1, 1, world_color="Novelty", produces=True)
    player.tableau = [
        world,
        Tile("router", "Router", TileKind.DEVELOPMENT, 1, 1, tags=("reassign",)),
    ]
    player.goods = []
    game.start_reassign_round(player)

    game.resolve_phase(player, Phase.PRODUCE)

    assert len(player.goods) == 1
    assert player.goods[0].world == world
    assert player.goods[0].color is DieColor.GREEN
    assert player.tracks[DieColor.BLUE].current == 0


def test_reassign_into_ship_performs_normal_fixed_value_consume():
    game = PhaseBatteryGame([("P1", "balanced")], seed=43)
    player = game.players[0]
    for track in player.tracks.values():
        track.current = 0
    player.tracks[DieColor.BLUE].current = 1
    player.credits = 3
    world = Tile("ship", "Shipping World", TileKind.WORLD, 1, 1, world_color="Genes", produces=True)
    player.tableau = [
        world,
        Tile("router", "Router", TileKind.DEVELOPMENT, 1, 1, tags=("reassign",)),
    ]
    player.goods = [Good(world, DieColor.GREEN)]
    game.start_reassign_round(player)

    game.resolve_phase(player, Phase.SHIP)

    assert player.goods == []
    assert player.vp_chips == 1
    assert player.tracks[DieColor.BLUE].current == 0


def test_world_placement_does_not_create_good_when_track_is_at_cap():
    game = PhaseBatteryGame([("P1", "producer")], seed=38)
    player = game.players[0]
    player.goods = []
    player.tracks[DieColor.GREEN].current = 6
    player.tracks[DieColor.GREEN].maximum = 6
    tile = Tile(
        "capped-windfall",
        "Capped Windfall",
        TileKind.WORLD,
        1,
        1,
        grants=(DieColor.GREEN,),
        placement="world",
        world_color="Genes",
        produces=True,
    )

    game.complete_tile(player, tile)

    assert player.goods == []


def test_produce_spends_one_green_pip_per_empty_colored_world():
    game = PhaseBatteryGame([("P1", "producer")], seed=40)
    player = game.players[0]
    first = Tile("first", "First World", TileKind.WORLD, 1, 1, world_color="Novelty", produces=True)
    second = Tile("second", "Second World", TileKind.WORLD, 1, 1, world_color="Genes", produces=True)
    gray = Tile("gray", "Gray World", TileKind.WORLD, 1, 1, world_color="gray", produces=False)
    player.tableau = [first, second, gray]
    player.goods = []
    player.tracks[DieColor.GREEN].current = 3

    game.resolve_phase(player, Phase.PRODUCE)

    assert {good.world for good in player.goods} == {first, second}
    assert player.tracks[DieColor.GREEN].current == 1


def test_ship_trades_goods_for_credits_without_vp_chips():
    game = PhaseBatteryGame([("P1", "producer")], seed=13)
    player = game.players[0]
    world = Tile("trade-world", "Trade World", TileKind.WORLD, 4, 4, world_color="Genes", produces=True)
    player.tableau = [world]
    player.goods = []
    player.credits = 0
    game.sync_credit_track(player)
    player.tracks[DieColor.GREEN].current = 1
    player.tracks[DieColor.PURPLE].current = 1

    game.resolve_phase(player, Phase.PRODUCE)
    game.resolve_phase(player, Phase.SHIP)

    assert player.goods == []
    assert player.credits == 5
    assert player.vp_chips == 0
    assert player.shipped_goods == 1
    assert game.score(player) == 4


def test_ship_credit_value_uses_world_color_not_good_color():
    game = PhaseBatteryGame([("P1", "producer")], seed=15)

    assert game.ship_credit_value(Tile("plain", "Plain World", TileKind.WORLD, 1, 1)) == 1
    assert game.ship_credit_value(
        Tile("novelty", "Novelty World", TileKind.WORLD, 1, 1, world_color="Novelty")
    ) == 3
    assert game.ship_credit_value(
        Tile("rare", "Rare World", TileKind.WORLD, 1, 1, world_color="Rare Elements")
    ) == 4
    assert game.ship_credit_value(Tile("genes", "Genes World", TileKind.WORLD, 1, 1, world_color="Genes")) == 5
    assert game.ship_credit_value(
        Tile("alien", "Alien World", TileKind.WORLD, 1, 1, world_color="Alien Technology")
    ) == 6
    novelty = Tile("novelty-good", "Novelty World", TileKind.WORLD, 1, 1, world_color="Novelty")

    assert game.ship_credit_value(Good(novelty, DieColor.GREEN)) == 3


def test_consume_is_fixed_at_one_vp_without_color_matching():
    game = PhaseBatteryGame([("P1", "shipper")], seed=41)
    player = game.players[0]
    world = Tile("genes", "Genes World", TileKind.WORLD, 1, 1, world_color="Genes", produces=True)
    player.goods = [Good(world, DieColor.GREEN)]
    player.credits = 3
    player.tracks[DieColor.PURPLE].current = 1

    game.resolve_phase(player, Phase.SHIP)

    assert player.vp_chips == 1
    assert player.goods == []
def test_galactic_bankers_goal_uses_satisfied_populace_named_condition():
    game = PhaseBatteryGame([("P1", "shipper")], seed=30)
    player = game.players[0]
    goal = Tile("galactic_bankers", "Galactic Bankers", TileKind.DEVELOPMENT, 6, 6, tags=("end_game",))
    game.committed_goals[player.name] = [goal]
    player.shipped_goods = 3

    assert not game.endgame_goal_fulfilled(player, goal)
    assert game.endgame_goal_score(player) == -6

    player.shipped_goods = 4

    assert game.endgame_goal_fulfilled(player, goal)
    assert game.player_summary(player)["goal_requirements"]["Galactic Bankers"]["label"] == "Satisfied Populace"


def test_solo_dummy_phase_effects_claim_and_ship_without_vp_pool():
    solo = PhaseBatterySoloGame(seed=13)
    dev = Tile("dummy-dev", "Dummy Development", TileKind.DEVELOPMENT, 1, 1)
    world = Tile("dummy-world", "Dummy World", TileKind.WORLD, 1, 1)
    solo.game.tile_bag = [dev, world]
    solo.dummy.goods = 2

    solo.resolve_dummy_phase(Phase.EXPLORE)
    solo.resolve_dummy_phase(Phase.SHIP)

    assert solo.dummy.claimed_tiles == [dev, world]
    assert solo.dummy.goods == 0
    assert solo.dummy.shipped_goods == 2


def test_solo_resolves_only_player_and_dummy_selected_phases():
    solo = PhaseBatterySoloGame(strategy="builder", seed=23, dummy_count=1)
    player = solo.player
    solo.phase_deck = [Phase.EXPLORE]
    for track in player.tracks.values():
        track.current = 0
    player.tracks[DieColor.BLUE].current = 0
    player.tracks[DieColor.BROWN].current = 1
    player.tracks[DieColor.GREEN].current = 1
    player.dev_stack = [BuildSlot(Tile("d", "Development", TileKind.DEVELOPMENT, 1, 1))]
    player.world_stack = []
    player.tableau = [Tile("prod", "Production World", TileKind.WORLD, 1, 1, produces=True)]
    player.goods = []

    report = solo.play_round()

    assert report.player_phases == (Phase.DEVELOP, Phase.PRODUCE)
    assert report.dummy_phases == (Phase.EXPLORE,)
    assert report.selected_phases == (Phase.EXPLORE, Phase.DEVELOP, Phase.PRODUCE)
    assert player.dev_stack == []
    assert player.goods


def test_solo_play_returns_summary():
    solo = PhaseBatterySoloGame(strategy="builder", seed=14)

    scores, reports = solo.play()
    summary = scores[0][2]

    assert scores[0][0] == "You"
    assert summary["rounds"] == len(reports)
    assert summary["end_reason"] in {"round_limit", "tableau"}
    assert summary["dummy_claimed_tiles"] >= 0
    assert solo.game.round_number <= solo.game.config.max_rounds


def test_solo_defaults_to_rebased_clock_thresholds_and_twenty_four_vp_chips():
    solo = PhaseBatterySoloGame(seed=26)

    assert solo.player.credits == 1
    assert solo.game.config.max_rounds == SOLO_ROUNDS == 20
    assert solo.game.vp_pool_per_player == 24
    assert solo.game.vp_pool == 24
    assert solo.difficulty == "normal"
    assert SOLO_DIFFICULTIES["normal"] == {
        "great": 32,
        "triumphant": 36,
        "epic": 40,
        "named": 32,
        "industrial": 9,
    }


def test_solo_commits_a_goal_by_round_ten():
    solo = PhaseBatterySoloGame(seed=42)
    solo.game.round_number = SOLO_GOAL_COMMIT_ROUND - 1
    solo.player.dev_stack = []
    solo.player.world_stack = []

    solo.play_round()

    assert solo.game.goal_commit_round == SOLO_GOAL_COMMIT_ROUND
    assert len(solo.game.committed_goals[solo.player.name]) == 1


def test_goal_requirements_match_rebased_solo_structure_targets():
    game = PhaseBatteryGame([("P1", "balanced")], seed=43)
    player = game.players[0]
    goals = {tile.id: tile for tile in game.endgame_goal_market}
    for tile in game.extra_endgame_goals:
        goals[tile.id] = tile

    assert game.endgame_goal_requirement(
        player, goals["galactic_renaissance"]
    )[1] == 7
    assert game.endgame_goal_requirement(
        player, goals["galactic_reserves"]
    )[1] == 9
    assert game.endgame_goal_requirement(
        player, goals["new_galactic_order"]
    )[1] == 3

    easy_solo = PhaseBatterySoloGame(seed=44, difficulty="easy")
    easy_goals = {
        tile.id: tile
        for tile in (
            easy_solo.game.endgame_goal_market
            + easy_solo.game.extra_endgame_goals
        )
    }
    assert easy_solo.game.endgame_goal_requirement(
        easy_solo.player, easy_goals["galactic_reserves"]
    )[1] == 7
