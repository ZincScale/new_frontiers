from phase_battery.engine import PhaseBatteryConfig, PhaseBatteryGame
from phase_battery.solo import PhaseBatterySoloGame
from roll_galaxy.model import BuildSlot, DieColor, Phase, Tile, TileKind


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


def test_credits_are_unlimited_chips_and_white_is_settle_track():
    game = PhaseBatteryGame([("P1", "builder")], seed=16)
    player = game.players[0]

    game.set_credits(player, 40)

    assert player.credits == 40
    assert DieColor.WHITE in player.tracks
    assert game.track(player, DieColor.WHITE).current == 3
    assert game.track(player, DieColor.WHITE).maximum == 3
    assert game.player_summary(player)["tracks"]["white"] == (3, 3)


def test_player_with_no_ready_pips_selects_no_phase():
    game = PhaseBatteryGame([("P1", "builder")], seed=21)
    player = game.players[0]
    for track in player.tracks.values():
        track.current = 0
    player.dev_stack = [BuildSlot(Tile("d", "Development", TileKind.DEVELOPMENT, 1, 1))]
    player.world_stack = [BuildSlot(Tile("w", "World", TileKind.WORLD, 1, 1))]

    assert game.choose_phase(player) is None
    assert game.selected_phases() == ()


def test_two_player_game_selects_two_eligible_phases_per_player():
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

    assert game.phase_selection_count() == 2
    assert game.selected_phases() == (Phase.EXPLORE, Phase.DEVELOP, Phase.PRODUCE, Phase.SHIP)


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


def test_military_world_requires_red_max_and_exhausts_current_red():
    game = PhaseBatteryGame([("P1", "military")], seed=2)
    player = game.players[0]
    player.tracks[DieColor.RED].current = 3
    player.tracks[DieColor.RED].maximum = 3
    player.world_stack = [BuildSlot(Tile("rebel-test", "Rebel Test World", TileKind.WORLD, 3, 3, grants=()))]

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == []
    assert player.tracks[DieColor.RED].current == 2
    assert player.tracks[DieColor.RED].maximum == 3
    assert game.player_summary(player)["red_exhausts"] == 1


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

    game.resolve_phase(player, Phase.DEVELOP)

    assert tile in player.tableau
    assert player.credits == 0
    assert player.credits_earned == 0

    game.manage_empire(player)

    assert player.credits_earned == 0


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

    assert player.dev_stack == [BuildSlot(expensive, progress=1)]
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
        for index in range(4)
    ]
    game.committed_goals[player.name] = [goal]

    assert game.endgame_goal_fulfilled(player, goal)
    assert game.endgame_goal_score(player) == 4
    assert game.player_summary(player)["goal_requirements"]["New Economy"]["fulfilled"]


def test_settle_can_complete_multiple_worlds_in_one_phase():
    game = PhaseBatteryGame([("P1", "settler")], seed=10)
    player = game.players[0]
    player.credits = 2
    game.sync_credit_track(player)
    first = Tile("w1", "World 1", TileKind.WORLD, 1, 1, world_color="Novelty")
    second = Tile("w2", "World 2", TileKind.WORLD, 1, 1, world_color="Genes")
    player.world_stack = [BuildSlot(first), BuildSlot(second)]

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == []
    assert first in player.tableau
    assert second in player.tableau
    assert player.credits == 2
    assert player.credits_spent == 0
    assert player.tracks[DieColor.WHITE].current == 1


def test_settle_can_skip_blocking_top_world_for_affordable_world():
    game = PhaseBatteryGame([("P1", "settler")], seed=11)
    player = game.players[0]
    player.tracks[DieColor.WHITE].current = 1
    game.sync_credit_track(player)
    expensive = Tile("w-big", "Large World", TileKind.WORLD, 6, 6)
    cheap = Tile("w-cheap", "Cheap World", TileKind.WORLD, 1, 1)
    player.world_stack = [BuildSlot(expensive), BuildSlot(cheap)]

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == [BuildSlot(expensive)]
    assert cheap in player.tableau
    assert expensive not in player.tableau


def test_settle_can_complete_multiple_military_worlds_with_red_readiness():
    game = PhaseBatteryGame([("P1", "military")], seed=12)
    player = game.players[0]
    player.tracks[DieColor.RED].current = 4
    player.tracks[DieColor.RED].maximum = 4
    first = Tile("rebel-1", "Rebel World 1", TileKind.WORLD, 2, 2, grants=())
    second = Tile("rebel-2", "Rebel World 2", TileKind.WORLD, 3, 3, grants=())
    player.world_stack = [BuildSlot(first), BuildSlot(second)]

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == []
    assert first in player.tableau
    assert second in player.tableau
    assert player.tracks[DieColor.RED].current == 2
    assert game.player_summary(player)["red_exhausts"] == 2


def test_military_world_blocks_without_enough_current_red_even_with_level():
    game = PhaseBatteryGame([("P1", "military")], seed=3)
    player = game.players[0]
    player.tracks[DieColor.RED].current = 2
    player.tracks[DieColor.RED].maximum = 3
    world = Tile("rebel-test", "Rebel Test World", TileKind.WORLD, 3, 3, grants=())
    player.world_stack = [BuildSlot(world)]

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == [BuildSlot(world)]
    assert game.player_summary(player)["red_exhausts"] == 0


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


def test_red_grants_max_only_option_delays_current_red_gain():
    config = PhaseBatteryConfig(red_grants_current=False)
    game = PhaseBatteryGame([("P1", "military")], seed=5, config=config)
    player = game.players[0]
    player.tracks[DieColor.RED].current = 0
    player.tracks[DieColor.RED].maximum = 2

    game.gain_die(player, DieColor.RED)

    assert player.tracks[DieColor.RED].current == 0
    assert player.tracks[DieColor.RED].maximum == 3


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
    assert game.score(player) == 4


def test_ship_credit_value_uses_good_type():
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


def test_solo_defaults_to_twenty_four_vp_chips():
    solo = PhaseBatterySoloGame(seed=26)

    assert solo.player.credits == 1
    assert solo.game.vp_pool_per_player == 24
    assert solo.game.vp_pool == 24
