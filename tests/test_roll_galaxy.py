from roll_galaxy.engine import BatteryConfig, BatteryGame
from roll_galaxy.model import BuildSlot, DieColor, Phase, Tile, TileKind
from roll_galaxy.solo import BatterySoloGame, SOLO_CAMPAIGNS, SOLO_WIN_CONDITION_MAP
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


def test_spending_phase_uses_native_color_before_white():
    game = BatteryGame(seed=2)
    player = game.players[0]
    player.tracks[DieColor.RED].current = 1
    player.tracks[DieColor.WHITE].current = 3

    spent = game.spend_phase_pip(player, Phase.SETTLE)

    assert spent is DieColor.RED
    assert player.tracks[DieColor.RED].current == 0
    assert player.tracks[DieColor.WHITE].current == 3


def test_white_pip_can_pay_for_empty_phase_track():
    game = BatteryGame(seed=3)
    player = game.players[0]
    player.tracks[DieColor.BROWN].current = 0
    player.tracks[DieColor.WHITE].current = 2

    spent = game.spend_phase_pip(player, Phase.DEVELOP)

    assert spent is DieColor.WHITE
    assert player.tracks[DieColor.WHITE].current == 1


def test_completed_world_grants_pip_instead_of_new_worker_die():
    game = BatteryGame(seed=4)
    player = game.players[0]
    world = Tile("w-grant", "Grant World", TileKind.WORLD, 1, 1, grants=(DieColor.GREEN,))
    before = player.tracks[DieColor.GREEN].maximum

    game.complete_tile(player, world)

    assert player.tracks[DieColor.GREEN].maximum == before + 1
    assert player.tracks[DieColor.GREEN].current == before + 1


def test_settle_spends_track_pips_to_build_world():
    game = BatteryGame(seed=5)
    player = game.players[0]
    player.credits = 0
    player.tracks[DieColor.RED].current = 2
    player.tracks[DieColor.RED].maximum = 3
    player.tracks[DieColor.WHITE].current = 0
    player.world_stack = [BuildSlot(Tile("w-test", "Test World", TileKind.WORLD, 2, 1, grants=(DieColor.RED,)))]

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == []
    assert player.completed_tiles == 1
    assert player.tracks[DieColor.RED].current == 1
    assert player.tracks[DieColor.RED].maximum == 4


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
    player.tracks[DieColor.RED].current = 0
    player.tracks[DieColor.RED].maximum = 3
    player.credits = 0

    game.manage_empire(player)

    assert player.tracks[DieColor.RED].current == 1
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
    assert SOLO_WIN_CONDITION_MAP["great"].min_score == 40
    assert SOLO_WIN_CONDITION_MAP["triumphant"].min_score == 43
    assert SOLO_WIN_CONDITION_MAP["epic"].min_score == 46


def test_solo_campaign_conditions_do_not_repeat_within_sheet():
    canonical = set(SOLO_WIN_CONDITION_MAP)
    for campaign in SOLO_CAMPAIGNS:
        names = campaign.condition_names

        assert len(names) == 4
        assert len(names) == len(set(names))
        assert set(names) <= canonical
