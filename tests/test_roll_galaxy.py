from roll_galaxy.engine import BatteryConfig, BatteryGame
from roll_galaxy.model import BuildSlot, DieColor, Phase, Tile, TileKind
from roll_galaxy.solo import BatterySoloGame, SOLO_CAMPAIGNS, SOLO_DIFFICULTY_MAP, SOLO_WIN_CONDITION_MAP
from roll_galaxy.tiles import HOME_WORLDS, NON_START_TILES, START_FACTION_PAIRS


def test_gain_die_pips_color_track_up_to_max_six():
    game = BatteryGame(seed=1)
    player = game.players[0]
    red = player.tracks[DieColor.RED]
    red.current = 5
    red.maximum = 5

    game.gain_die(player, DieColor.RED)
    game.gain_die(player, DieColor.RED)

    assert red.current == 6
    assert red.maximum == 6


def test_red_track_is_persistent_military_level_not_spent():
    game = BatteryGame(seed=2)
    player = game.players[0]
    player.credits = 0
    player.tracks[DieColor.RED].current = 2
    player.tracks[DieColor.RED].maximum = 2
    player.world_stack = [BuildSlot(Tile("rebel-test", "Rebel Test World", TileKind.WORLD, 2, 2, grants=(DieColor.RED,)))]

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == []
    assert player.tracks[DieColor.RED].current == 3
    assert player.tracks[DieColor.RED].maximum == 3


def test_white_track_mirrors_credit_total():
    game = BatteryGame(seed=3)
    player = game.players[0]

    game.gain_credits(player, 3)
    game.spend_credits(player, 2)

    assert player.credits == 2
    assert player.tracks[DieColor.WHITE].current == 2
    assert player.tracks[DieColor.WHITE].maximum == game.config.max_credits


def test_explore_scout_uses_pips_as_search_depth_but_keeps_one_tile():
    game = BatteryGame(seed=30)
    player = game.players[0]
    player.dev_stack = []
    player.world_stack = []
    player.tracks[DieColor.BLUE].current = 2
    player.tracks[DieColor.WHITE].current = 0
    low = Tile("d-low", "Low Development", TileKind.DEVELOPMENT, 1, 1)
    high = Tile("d-high", "High Development", TileKind.DEVELOPMENT, 2, 4)
    game.tile_bag = [
        low,
        Tile("w-skip", "Skipped World", TileKind.WORLD, 1, 1),
        high,
    ]

    game.resolve_phase(player, Phase.EXPLORE)

    assert [slot.tile for slot in player.dev_stack] == [high]
    assert player.world_stack == []
    assert low in game.tile_bag
    assert player.tracks[DieColor.BLUE].current == 0
    assert player.used_pips == 2


def test_explore_stocks_for_credits_when_build_stacks_are_filled():
    game = BatteryGame(seed=31)
    player = game.players[0]
    player.credits = 0
    player.dev_stack = [BuildSlot(Tile("d-queued", "Queued Development", TileKind.DEVELOPMENT, 1, 1))]
    player.world_stack = [BuildSlot(Tile("w-queued", "Queued World", TileKind.WORLD, 1, 1))]
    player.tracks[DieColor.BLUE].current = 2
    player.tracks[DieColor.WHITE].current = 0

    game.resolve_phase(player, Phase.EXPLORE)

    assert player.credits == 4
    assert player.credits_earned == 4
    assert player.tracks[DieColor.BLUE].current == 0
    assert player.used_pips == 2


def test_mining_strategy_scout_prefers_rare_worlds():
    game = BatteryGame([("Miner", "mining")], seed=32)
    player = game.players[0]
    player.dev_stack = []
    player.world_stack = []
    player.tracks[DieColor.BLUE].current = 2
    player.tracks[DieColor.WHITE].current = 0
    generic = Tile("generic", "Generic World", TileKind.WORLD, 2, 4, world_color="gray")
    rare = Tile("rare", "Rare World", TileKind.WORLD, 2, 1, world_color="Rare Elemental", produces=True, tags=("rare_elemental",))
    game.tile_bag = [generic, rare]

    game.resolve_phase(player, Phase.EXPLORE)

    assert [slot.tile for slot in player.world_stack] == [rare]


def test_military_strategy_scout_prefers_red_grants():
    game = BatteryGame([("Military", "military")], seed=33)
    player = game.players[0]
    player.dev_stack = []
    player.world_stack = []
    player.tracks[DieColor.BLUE].current = 2
    player.tracks[DieColor.WHITE].current = 0
    generic = Tile("generic", "Generic World", TileKind.WORLD, 2, 4, world_color="Novelty", produces=True, tags=("novelty",))
    red = Tile("red", "Red World", TileKind.WORLD, 2, 1, grants=(DieColor.RED,), world_color="gray", tags=("gray",))
    game.tile_bag = [generic, red]

    game.resolve_phase(player, Phase.EXPLORE)

    assert [slot.tile for slot in player.world_stack] == [red]


def test_endgame_development_bonuses_score_strategy_payoffs():
    game = BatteryGame(seed=34)
    player = game.players[0]
    mining_league = Tile("mining_league", "Mining League", TileKind.DEVELOPMENT, 6, 6, tags=("phase_v", "end_game"))
    rare_a = Tile("rare-a", "Rare A", TileKind.WORLD, 2, 2, world_color="Rare Elemental", produces=True, tags=("rare_elemental",))
    rare_b = Tile("rare-b", "Rare B", TileKind.WORLD, 2, 2, world_color="Rare Elemental", produces=True, tags=("rare_elemental",))
    player.tableau = [mining_league, rare_a, rare_b]
    player.tracks[DieColor.BROWN].maximum = 4

    assert game.endgame_bonus(player) == 6
    assert game.score(player) == 16


def test_credit_track_does_not_count_as_owned_dice_for_endgame_bonuses():
    game = BatteryGame(seed=35)
    player = game.players[0]
    exchange = Tile("galactic_exchange", "Galactic Exchange", TileKind.DEVELOPMENT, 6, 6, tags=("end_game",))
    reserves = Tile("galactic_reserves", "Galactic Reserves", TileKind.DEVELOPMENT, 6, 6, tags=("end_game",))
    player.tableau = [exchange, reserves]
    for color in (DieColor.BLUE, DieColor.BROWN, DieColor.RED, DieColor.GREEN, DieColor.PURPLE):
        player.tracks[color].maximum = 1
        player.tracks[color].current = 1
    player.tracks[DieColor.YELLOW].maximum = 0
    player.tracks[DieColor.YELLOW].current = 0
    game.set_credits(player, 6)

    assert game.endgame_tile_bonus(player, exchange) == 5
    assert game.endgame_tile_bonus(player, reserves) == 1


def test_completed_world_grants_pip_instead_of_new_worker_die():
    game = BatteryGame(seed=4)
    player = game.players[0]
    world = Tile("w-grant", "Grant World", TileKind.WORLD, 1, 1, grants=(DieColor.GREEN,))
    before = player.tracks[DieColor.GREEN].maximum

    game.complete_tile(player, world)

    assert player.tracks[DieColor.GREEN].maximum == before + 1
    assert player.tracks[DieColor.GREEN].current == before + 1


def test_normal_settle_spends_credits_not_red_military_level():
    game = BatteryGame(seed=5)
    player = game.players[0]
    game.set_credits(player, 2)
    player.tracks[DieColor.RED].current = 2
    player.tracks[DieColor.RED].maximum = 3
    player.world_stack = [BuildSlot(Tile("w-test", "Test World", TileKind.WORLD, 2, 1, grants=(DieColor.BLUE,), world_color="Novelty"))]

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == []
    assert player.completed_tiles == 1
    assert player.tracks[DieColor.RED].current == 2
    assert player.tracks[DieColor.RED].maximum == 3
    assert player.credits == 0
    assert player.tracks[DieColor.WHITE].current == 0


def test_develop_can_use_credits_to_finish_tile_in_one_shot():
    game = BatteryGame(seed=22)
    player = game.players[0]
    player.credits = 2
    player.tracks[DieColor.BROWN].current = 1
    player.tracks[DieColor.WHITE].current = 0
    player.dev_stack = [BuildSlot(Tile("d-test", "Test Development", TileKind.DEVELOPMENT, 3, 3))]

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack == []
    assert player.completed_tiles == 1
    assert player.tracks[DieColor.BROWN].current == 0
    assert player.credits == 0
    assert player.credits_spent == 2


def test_develop_does_not_keep_partial_progress_when_short_on_funds():
    game = BatteryGame(seed=23)
    player = game.players[0]
    player.credits = 0
    player.tracks[DieColor.BROWN].current = 1
    player.tracks[DieColor.WHITE].current = 0
    player.dev_stack = [BuildSlot(Tile("d-test", "Test Development", TileKind.DEVELOPMENT, 2, 2))]

    game.resolve_phase(player, Phase.DEVELOP)

    assert len(player.dev_stack) == 1
    assert player.dev_stack[0].progress == 0
    assert player.tracks[DieColor.BROWN].current == 1


def test_credits_recharge_depleted_tracks_and_record_spending():
    game = BatteryGame(seed=6, config=BatteryConfig(minimum_recharge=0))
    player = game.players[0]
    player.tracks[DieColor.BROWN].current = 0
    player.tracks[DieColor.BROWN].maximum = 3
    player.credits = 2

    game.manage_empire(player)

    assert player.tracks[DieColor.BROWN].current == 2
    assert player.credits_spent == 2
    assert player.credits == 1


def test_free_recharge_can_be_tuned_separately_from_credits():
    game = BatteryGame(seed=7, config=BatteryConfig(minimum_recharge=1))
    player = game.players[0]
    player.tracks[DieColor.BROWN].current = 0
    player.tracks[DieColor.BROWN].maximum = 3
    player.credits = 0

    game.manage_empire(player)

    assert player.tracks[DieColor.BROWN].current == 1
    assert player.free_recharged == 1
    assert player.credits_spent == 0
    assert player.credits == 1


def test_spreadsheet_first_sheet_imports_non_start_tiles():
    worlds = [tile for tile in NON_START_TILES if tile.kind is TileKind.WORLD]
    developments = [tile for tile in NON_START_TILES if tile.kind is TileKind.DEVELOPMENT]

    assert len(NON_START_TILES) == 110
    assert len(worlds) == 55
    assert len(developments) == 55
    assert len({tile.id for tile in NON_START_TILES}) == 110


def test_spreadsheet_second_sheet_imports_start_tiles():
    assert len(START_FACTION_PAIRS) == 9
    assert all(len(pair) == 2 for pair in START_FACTION_PAIRS)
    assert len(HOME_WORLDS) == 9
    assert all(home.kind is TileKind.WORLD for home in HOME_WORLDS)


def test_spreadsheet_tile_grants_map_to_phase_tracks():
    tile = next(tile for tile in NON_START_TILES if tile.id == "blaster_gem_mines")

    assert tile.grants == (DieColor.RED, DieColor.BROWN)
    assert tile.world_color == "Rare Elemental"
    assert tile.produces


def test_world_placement_creates_windfall_good_and_pips_track():
    game = BatteryGame(seed=8)
    player = game.players[0]
    tile = next(tile for tile in NON_START_TILES if tile.id == "comet_zone")
    before = player.tracks[DieColor.BROWN].maximum

    game.complete_tile(player, tile)

    assert player.tracks[DieColor.BROWN].maximum == before + 1
    assert any(good.world is tile and good.color is DieColor.BROWN for good in player.goods)


def test_die_loss_reduces_a_track_before_granting_new_pips():
    game = BatteryGame(seed=9)
    player = game.players[0]
    tile = next(tile for tile in NON_START_TILES if tile.id == "conscription")
    red_before = player.tracks[DieColor.RED].maximum
    total_before = sum(track.maximum for track in player.tracks.values())

    game.complete_tile(player, tile)

    assert player.tracks[DieColor.RED].maximum == red_before + 2
    assert sum(track.maximum for track in player.tracks.values()) == total_before + 1


def test_setup_uses_real_start_tiles_and_initial_construction_tiles():
    game = BatteryGame(seed=10)
    player = game.players[0]
    start_tiles = [tile for tile in player.tableau if "faction" in tile.tags or "home" in tile.tags]

    assert len(start_tiles) == 3
    assert len(player.dev_stack) == 1
    assert len(player.world_stack) == 1
    assert len(player.tableau) == 3


def test_default_multiplayer_vp_pool_scales_for_two_player_games():
    two_player = BatteryGame([("P1", "balanced"), ("P2", "builder")], seed=35)
    three_player = BatteryGame([("P1", "balanced"), ("P2", "builder"), ("P3", "settler")], seed=36)
    overridden = BatteryGame(
        [("P1", "balanced"), ("P2", "builder")],
        seed=37,
        config=BatteryConfig(vp_pool_per_player=12),
    )

    assert two_player.vp_pool_per_player == 8
    assert two_player.vp_pool == 16
    assert three_player.vp_pool_per_player == 12
    assert three_player.vp_pool == 36
    assert overridden.vp_pool_per_player == 12
    assert overridden.vp_pool == 24


def test_yellow_ship_mode_counts_as_ship_capacity():
    game = BatteryGame(seed=11, config=BatteryConfig(yellow_mode="ship"))
    player = game.players[0]
    player.tracks[DieColor.PURPLE].current = 0
    player.tracks[DieColor.YELLOW].current = 1
    player.tracks[DieColor.WHITE].current = 0

    spent = game.spend_phase_pip(player, Phase.SHIP)

    assert spent is DieColor.YELLOW
    assert player.tracks[DieColor.YELLOW].current == 0


def test_yellow_alien_mode_can_settle_alien_world():
    game = BatteryGame(seed=12, config=BatteryConfig(yellow_mode="alien"))
    player = game.players[0]
    player.tracks[DieColor.RED].current = 0
    player.tracks[DieColor.YELLOW].current = 1
    player.tracks[DieColor.WHITE].current = 0
    player.world_stack = [
        BuildSlot(Tile("alien-test", "Alien Test World", TileKind.WORLD, 1, 1, world_color="Alien Technology"))
    ]

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == []
    assert player.tracks[DieColor.YELLOW].current == 0


def test_yellow_alien_mode_does_not_pay_for_non_alien_settle():
    game = BatteryGame(seed=13, config=BatteryConfig(yellow_mode="alien"))
    player = game.players[0]
    player.credits = 0
    player.tracks[DieColor.RED].current = 0
    player.tracks[DieColor.YELLOW].current = 1
    player.tracks[DieColor.WHITE].current = 0
    player.world_stack = [BuildSlot(Tile("novelty-test", "Novelty Test World", TileKind.WORLD, 1, 1, world_color="Novelty"))]

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack
    assert player.tracks[DieColor.YELLOW].current == 1


def test_yellow_alien_mode_produces_only_on_alien_world():
    game = BatteryGame(seed=14, config=BatteryConfig(yellow_mode="alien"))
    player = game.players[0]
    alien = Tile("alien-prod", "Alien Production World", TileKind.WORLD, 1, 1, world_color="Alien Technology", produces=True)
    novelty = Tile("novelty-prod", "Novelty Production World", TileKind.WORLD, 5, 5, world_color="Novelty", produces=True)
    player.tableau = [novelty, alien]

    assert game.produce(player, DieColor.YELLOW)

    assert player.goods[0].world is alien


def test_solo_dummy_phase_adds_selected_phase_for_player():
    game = BatterySoloGame(strategy="builder", seed=15)
    game.phase_deck = [Phase.SHIP]
    game.dummy_count = 1

    report = game.play_round()

    assert report.dummy_phases == (Phase.SHIP,)
    assert Phase.SHIP in report.selected
    assert report.human_score == game.game.score(game.player)


def test_solo_dummy_draw_reshuffles_before_short_round_draw():
    game = BatterySoloGame(seed=20)
    game.phase_deck = [Phase.SHIP]

    phases = game.draw_dummy_phases()

    assert len(phases) == 2
    assert len(set(phases)) == 2


def test_solo_dummy_explore_churns_one_development_and_one_world():
    game = BatterySoloGame(seed=16)
    before_devs = sum(1 for tile in game.game.tile_bag if tile.kind is TileKind.DEVELOPMENT)
    before_worlds = sum(1 for tile in game.game.tile_bag if tile.kind is TileKind.WORLD)

    game.resolve_dummy_phase(Phase.EXPLORE)

    after_devs = sum(1 for tile in game.game.tile_bag if tile.kind is TileKind.DEVELOPMENT)
    after_worlds = sum(1 for tile in game.game.tile_bag if tile.kind is TileKind.WORLD)

    assert after_devs == before_devs - 1
    assert after_worlds == before_worlds - 1
    assert len(game.dummy.claimed_tiles) == 2


def test_solo_dummy_build_phases_claim_matching_tile_from_bag():
    game = BatterySoloGame(seed=19)
    before_devs = sum(1 for tile in game.game.tile_bag if tile.kind is TileKind.DEVELOPMENT)
    before_worlds = sum(1 for tile in game.game.tile_bag if tile.kind is TileKind.WORLD)

    game.resolve_dummy_phase(Phase.DEVELOP)
    game.resolve_dummy_phase(Phase.SETTLE)

    after_devs = sum(1 for tile in game.game.tile_bag if tile.kind is TileKind.DEVELOPMENT)
    after_worlds = sum(1 for tile in game.game.tile_bag if tile.kind is TileKind.WORLD)

    assert after_devs == before_devs - 1
    assert after_worlds == before_worlds - 1
    assert len(game.dummy.claimed_tiles) == 2


def test_solo_dummy_ship_drains_vp_pool_from_goods_or_minimum_raid():
    game = BatterySoloGame(seed=17)
    before_pool = game.game.vp_pool

    game.resolve_dummy_phase(Phase.SHIP)

    assert game.game.vp_pool == before_pool - 2
    assert game.dummy.vp_chips_drained == 2

    game.dummy.goods = 3
    game.resolve_dummy_phase(Phase.SHIP)

    assert game.dummy.goods == 0
    assert game.dummy.vp_chips_drained == 8


def test_solo_game_returns_human_score_and_win_condition_summary():
    game = BatterySoloGame(strategy="balanced", seed=18, condition="all")

    scores, reports = game.play()

    assert {name for name, _score, _summary in scores} == {"You"}
    assert reports
    assert "satisfied_conditions" in scores[0][2]
    assert "great_success" in scores[0][2]
    assert "builder_success" in scores[0][2]
    assert "colonizer_success" in scores[0][2]
    assert scores[0][2]["dummy_claimed_tiles"] > 0
    assert game.end_reason() in {"vp_pool", "human_tableau", "round_limit"}


def test_solo_campaign_filters_to_campaign_conditions():
    game = BatterySoloGame(strategy="balanced", seed=21, campaign="outreach")

    scores, _reports = game.play()
    summary = scores[0][2]

    assert summary["campaign"] == "outreach"
    assert summary["campaign_name"] == "Outreach"
    assert {condition.name for condition in game.active_conditions()} == {
        "great",
        "colonizer",
        "builder",
        "industrial",
    }
    assert "epic_success" not in summary


def test_solo_score_only_thresholds_are_retuned_for_one_shot_builds():
    assert SOLO_WIN_CONDITION_MAP["great"].min_score == 31
    assert SOLO_WIN_CONDITION_MAP["triumphant"].min_score == 36
    assert SOLO_WIN_CONDITION_MAP["epic"].min_score == 42
    assert SOLO_WIN_CONDITION_MAP["builder"].min_score == 32
    assert SOLO_WIN_CONDITION_MAP["builder"].min_completed_tiles == 8
    assert SOLO_WIN_CONDITION_MAP["colonizer"].min_worlds == 6
    assert SOLO_WIN_CONDITION_MAP["industrial"].min_max_capacity == 14
    assert SOLO_WIN_CONDITION_MAP["military"].min_red_capacity == 4
    assert SOLO_WIN_CONDITION_MAP["discovery"].min_blue_capacity == 4


def test_solo_difficulty_tiers_have_distinct_score_targets():
    assert SOLO_DIFFICULTY_MAP["easy"].great_score == 23
    assert SOLO_DIFFICULTY_MAP["normal"].great_score == 31
    assert SOLO_DIFFICULTY_MAP["advanced"].great_score == 36
    assert SOLO_DIFFICULTY_MAP["very_hard"].great_score == 42


def test_solo_campaign_conditions_do_not_repeat_within_sheet():
    canonical = set(SOLO_WIN_CONDITION_MAP)
    for campaign in SOLO_CAMPAIGNS:
        names = campaign.condition_names

        assert len(names) == 4
        assert len(names) == len(set(names))
        assert set(names) <= canonical
