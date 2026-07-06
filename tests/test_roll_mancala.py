from roll_galaxy.model import DieColor, Good, Phase, Tile, TileKind
from roll_mancala.engine import MancalaConfig, MancalaGame
from roll_mancala.model import Construction, SECTION_ORDER, Section, SourceChoice
from roll_mancala.solo import (
    MancalaSoloGame,
    SOLO_CAMPAIGNS,
    SOLO_ROUNDS,
    SOLO_WIN_CONDITION_MAP,
)


def clear_player(player):
    for section in SECTION_ORDER:
        player.sections[section] = []
    for color in DieColor:
        player.spent[color] = 0
    player.dev_stack = []
    player.world_stack = []
    player.goods = []
    player.tableau = []
    player.credits = 0
    player.match_bonuses.clear()


def test_setup_uses_only_five_mancala_phase_sections_and_spent_area():
    game = MancalaGame(seed=1)
    player = game.players[0]

    assert tuple(player.sections) == SECTION_ORDER
    assert len(SECTION_ORDER) == 5
    assert len(player.sections[Section.EXPLORE]) >= 1
    assert len(player.sections[Section.DEVELOP]) >= 1
    assert len(player.sections[Section.SETTLE]) >= 1
    assert len(player.sections[Section.PRODUCE]) >= 1
    assert len(player.sections[Section.SHIP]) >= 1
    assert player.spent[DieColor.WHITE] >= 2
    assert player.spent[DieColor.YELLOW] >= 0
    assert all(color in player.spent for color in DieColor)


def test_sowing_from_board_selects_final_landing_phase():
    game = MancalaGame(seed=2)
    player = game.players[0]
    clear_player(player)
    player.sections[Section.EXPLORE] = [DieColor.BLUE, DieColor.BROWN]

    result = game.sow_choice(player, SourceChoice("section", section=Section.EXPLORE))

    assert result.placed == ((Section.DEVELOP, DieColor.BLUE), (Section.SETTLE, DieColor.BROWN))
    assert result.final_section is Section.SETTLE
    assert result.selected_phase is Phase.SETTLE
    assert player.sections[Section.EXPLORE] == []


def test_sowing_from_spent_enters_matching_color_section():
    game = MancalaGame(seed=3)
    player = game.players[0]
    clear_player(player)
    player.spent[DieColor.RED] = 2

    result = game.sow_choice(player, SourceChoice("spent", color=DieColor.RED, count=2))

    assert result.placed == ((Section.SETTLE, DieColor.RED), (Section.PRODUCE, DieColor.RED))
    assert result.selected_phase is Phase.PRODUCE
    assert player.spent[DieColor.RED] == 0


def test_white_and_yellow_spent_recovery_chooses_normal_entry_section():
    game = MancalaGame(seed=33)
    player = game.players[0]
    clear_player(player)
    player.spent[DieColor.WHITE] = 1
    player.spent[DieColor.YELLOW] = 1

    white_result = game.sow_choice(
        player,
        SourceChoice("spent", color=DieColor.WHITE, count=1, entry_section=Section.SHIP),
    )
    yellow_result = game.sow_choice(
        player,
        SourceChoice("spent", color=DieColor.YELLOW, count=1, entry_section=Section.DEVELOP),
    )

    assert white_result.placed == ((Section.SHIP, DieColor.WHITE),)
    assert white_result.selected_phase is Phase.SHIP
    assert yellow_result.placed == ((Section.DEVELOP, DieColor.YELLOW),)
    assert yellow_result.selected_phase is Phase.DEVELOP


def test_first_color_match_per_sow_gains_one_credit():
    game = MancalaGame(seed=4, config=MancalaConfig(conservative_bonus=True))
    player = game.players[0]
    clear_player(player)
    player.spent[DieColor.RED] = 1

    result = game.sow_choice(player, SourceChoice("spent", color=DieColor.RED, count=1))

    assert result.bonus_credit
    assert player.credits == 1
    assert player.color_match_bonuses == 1


def test_final_color_match_records_phase_bonus_by_default():
    game = MancalaGame(seed=4)
    player = game.players[0]
    clear_player(player)
    player.spent[DieColor.RED] = 1

    result = game.sow_choice(player, SourceChoice("spent", color=DieColor.RED, count=1))

    assert result.match_bonus_phase is Phase.SETTLE
    assert player.match_bonuses[Phase.SETTLE] == 1
    assert player.credits == 0
    assert player.color_match_bonuses == 1


def test_sowing_skips_full_sections_and_keeps_ownership():
    game = MancalaGame(seed=5, config=MancalaConfig(section_cap=1))
    player = game.players[0]
    clear_player(player)
    player.sections[Section.EXPLORE] = [DieColor.BLUE]
    player.sections[Section.DEVELOP] = [DieColor.BROWN]

    result = game.sow_choice(player, SourceChoice("section", section=Section.EXPLORE))

    assert result.placed == ((Section.SETTLE, DieColor.BLUE),)
    assert player.sections[Section.SETTLE] == [DieColor.BLUE]
    assert sum(len(player.sections[section]) for section in SECTION_ORDER) == 2


def test_phase_selected_by_one_player_is_shared_by_others():
    game = MancalaGame(players=[("P1", "builder"), ("P2", "producer")], seed=6)
    p1, p2 = game.players
    clear_player(p1)
    clear_player(p2)
    p1.sections[Section.EXPLORE] = [DieColor.BLUE]
    p2.sections[Section.DEVELOP] = [DieColor.BROWN]
    p2.sections[Section.PRODUCE] = [DieColor.GREEN]
    p2.dev_stack = [Construction(Tile("d", "Development", TileKind.DEVELOPMENT, 1, 1))]

    report = game.play_round()

    assert Phase.DEVELOP in report.selected
    assert p2.dev_stack == []
    assert p2.completed_tiles == 1


def test_explore_adds_new_tiles_to_bottom_of_shorter_queue_without_credits():
    game = MancalaGame(seed=6)
    player = game.players[0]
    clear_player(player)
    player.credits = 1
    player.sections[Section.EXPLORE] = [DieColor.BLUE, DieColor.BLUE, DieColor.BLUE]
    current_dev = Tile("current-dev", "Current Development", TileKind.DEVELOPMENT, 1, 1)
    current_world = Tile("current-world", "Current World", TileKind.WORLD, 1, 1)
    new_dev_1 = Tile("new-dev-1", "New Development 1", TileKind.DEVELOPMENT, 1, 1)
    new_world = Tile("new-world", "New World", TileKind.WORLD, 1, 1)
    new_dev_2 = Tile("new-dev-2", "New Development 2", TileKind.DEVELOPMENT, 1, 1)
    player.dev_stack = [Construction(current_dev)]
    player.world_stack = [Construction(current_world)]
    game.tile_bag = [new_dev_1, new_world, new_dev_2]

    game.resolve_phase(player, Phase.EXPLORE)

    assert [build.tile for build in player.dev_stack] == [current_dev, new_dev_1, new_dev_2]
    assert [build.tile for build in player.world_stack] == [current_world, new_world]
    assert player.credits == 1
    assert player.credits_earned == 0


def test_opponent_selected_phase_requires_matching_color_assist():
    game = MancalaGame(seed=6)
    player = game.players[0]
    clear_player(player)
    world = Tile("w", "Production World", TileKind.WORLD, 1, 1, produces=True)
    player.tableau = [world]
    player.sections[Section.PRODUCE] = [DieColor.BLUE, DieColor.WHITE]

    game.resolve_phase(player, Phase.PRODUCE, full_strength=False)

    assert player.goods == []
    assert player.phase_actions == 0


def test_opponent_selected_phase_gives_one_matching_color_assist():
    game = MancalaGame(seed=6)
    player = game.players[0]
    clear_player(player)
    worlds = [
        Tile("w1", "Production World 1", TileKind.WORLD, 1, 1, produces=True),
        Tile("w2", "Production World 2", TileKind.WORLD, 1, 1, produces=True),
    ]
    player.tableau = worlds
    player.sections[Section.PRODUCE] = [DieColor.GREEN, DieColor.GREEN, DieColor.GREEN]

    game.resolve_phase(player, Phase.PRODUCE, full_strength=False)

    assert len(player.goods) == 1
    assert player.phase_actions == 1


def test_own_selected_phase_uses_full_section_strength():
    game = MancalaGame(seed=6)
    player = game.players[0]
    clear_player(player)
    worlds = [
        Tile("w1", "Production World 1", TileKind.WORLD, 1, 1, produces=True),
        Tile("w2", "Production World 2", TileKind.WORLD, 1, 1, produces=True),
        Tile("w3", "Production World 3", TileKind.WORLD, 1, 1, produces=True),
    ]
    player.tableau = worlds
    player.sections[Section.PRODUCE] = [DieColor.GREEN, DieColor.BLUE, DieColor.WHITE]

    game.resolve_phase(player, Phase.PRODUCE)

    assert len(player.goods) == 3
    assert player.phase_actions == 3


def test_develop_does_not_complete_without_enough_credits_after_discount():
    game = MancalaGame(seed=7)
    player = game.players[0]
    clear_player(player)
    player.sections[Section.DEVELOP] = [DieColor.BROWN, DieColor.BLUE]
    player.dev_stack = [Construction(Tile("d", "Large Development", TileKind.DEVELOPMENT, 3, 3))]

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack[0].tile == Tile("d", "Large Development", TileKind.DEVELOPMENT, 3, 3)
    assert player.sections[Section.DEVELOP] == [DieColor.BROWN, DieColor.BLUE]
    assert player.credits == 0


def test_develop_keeps_partial_credit_progress_until_later_phase():
    game = MancalaGame(seed=7)
    player = game.players[0]
    clear_player(player)
    player.credits = 1
    tile = Tile("d", "Large Development", TileKind.DEVELOPMENT, 5, 5)
    player.dev_stack = [Construction(tile)]
    player.sections[Section.DEVELOP] = [DieColor.BROWN]

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack == [Construction(tile, progress=1)]
    assert tile not in player.tableau
    assert player.credits == 0
    assert player.credits_spent == 1

    player.credits = 3
    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack == []
    assert tile in player.tableau
    assert player.credits == 0
    assert player.credits_spent == 4


def test_opponent_selected_build_assist_uses_one_matching_discount():
    game = MancalaGame(seed=8)
    player = game.players[0]
    clear_player(player)
    player.credits = 2
    tile = Tile("d", "Assisted Development", TileKind.DEVELOPMENT, 3, 3)
    player.dev_stack = [Construction(tile)]
    player.sections[Section.DEVELOP] = [DieColor.BROWN, DieColor.BROWN, DieColor.WHITE]

    game.resolve_phase(player, Phase.DEVELOP, full_strength=False)

    assert player.dev_stack == []
    assert tile in player.tableau
    assert player.credits == 0
    assert player.credits_spent == 2
    assert player.phase_actions == 1


def test_develop_uses_credits_to_complete_build_after_section_discount():
    game = MancalaGame(seed=8)
    player = game.players[0]
    clear_player(player)
    player.credits = 5
    tile = Tile("d", "Large Development", TileKind.DEVELOPMENT, 3, 3)
    player.dev_stack = [Construction(tile)]
    player.sections[Section.DEVELOP] = [DieColor.BROWN, DieColor.BLUE]

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack == []
    assert tile in player.tableau
    assert player.credits == 3
    assert player.credits_spent == 2
    assert player.sections[Section.DEVELOP] == [DieColor.BROWN, DieColor.BLUE]


def test_develop_can_be_free_when_matching_discount_meets_cost():
    game = MancalaGame(seed=8)
    player = game.players[0]
    clear_player(player)
    tile = Tile("d", "Large Development", TileKind.DEVELOPMENT, 3, 3)
    player.dev_stack = [Construction(tile)]
    player.sections[Section.DEVELOP] = [DieColor.BROWN, DieColor.BROWN, DieColor.WHITE]

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack == []
    assert tile in player.tableau
    assert player.credits == 0
    assert player.sections[Section.DEVELOP] == [DieColor.BROWN, DieColor.BROWN, DieColor.WHITE]


def test_develop_match_bonus_reduces_completion_cost():
    game = MancalaGame(seed=8)
    player = game.players[0]
    clear_player(player)
    player.credits = 1
    tile = Tile("d", "Discounted Development", TileKind.DEVELOPMENT, 3, 3)
    player.dev_stack = [Construction(tile)]
    player.sections[Section.DEVELOP] = [DieColor.BROWN]
    player.match_bonuses[Phase.DEVELOP] = 1

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack == []
    assert tile in player.tableau
    assert player.credits == 0


def test_alien_world_requires_yellow_in_settle():
    game = MancalaGame(seed=8)
    player = game.players[0]
    clear_player(player)
    player.credits = 10
    world = Tile(
        "alien-world",
        "Alien World",
        TileKind.WORLD,
        3,
        3,
        world_color="Alien Technology",
        tags=("alien_technology",),
    )
    player.world_stack = [Construction(world)]
    player.sections[Section.SETTLE] = [DieColor.RED, DieColor.WHITE]
    player.match_bonuses[Phase.SETTLE] = 1

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == [Construction(world)]
    assert world not in player.tableau
    assert player.credits == 10


def test_yellow_settles_alien_world_and_is_only_discount():
    game = MancalaGame(seed=8)
    player = game.players[0]
    clear_player(player)
    player.credits = 5
    world = Tile(
        "alien-world",
        "Alien World",
        TileKind.WORLD,
        4,
        4,
        world_color="Alien Technology",
        tags=("alien_technology",),
    )
    player.world_stack = [Construction(world)]
    player.sections[Section.SETTLE] = [DieColor.YELLOW, DieColor.RED, DieColor.WHITE]
    player.match_bonuses[Phase.SETTLE] = 1

    game.resolve_phase(player, Phase.SETTLE)

    assert player.world_stack == []
    assert world in player.tableau
    assert player.credits == 2
    assert player.credits_spent == 3


def test_gain_die_goes_to_matching_section_or_spent_when_full():
    game = MancalaGame(seed=9, config=MancalaConfig(section_cap=1))
    player = game.players[0]
    clear_player(player)
    player.sections[Section.SETTLE] = [DieColor.RED]

    game.gain_die(player, DieColor.RED)

    assert player.sections[Section.SETTLE] == [DieColor.RED]
    assert player.spent[DieColor.RED] == 1


def test_manage_empire_spends_exact_credits_to_recover_spent_dice_without_free_credit():
    game = MancalaGame(seed=34, config=MancalaConfig(recovery_sow_cost=2))
    player = game.players[0]
    clear_player(player)
    player.credits = 2
    player.spent[DieColor.RED] = 1

    game.manage_empire(player)

    assert player.credits == 0
    assert player.credits_spent == 2
    assert player.recovery_sows == 1
    assert player.spent[DieColor.RED] == 0
    assert player.sections[Section.SETTLE] == [DieColor.RED]


def test_loss_removes_from_spent_before_board_goods_or_progress():
    game = MancalaGame(seed=10)
    player = game.players[0]
    clear_player(player)
    player.spent[DieColor.RED] = 1
    player.sections[Section.SETTLE] = [DieColor.RED]

    assert game.lose_die(player)

    assert player.spent[DieColor.RED] == 0
    assert player.sections[Section.SETTLE] == [DieColor.RED]


def test_produce_places_good_marker_without_moving_stone():
    game = MancalaGame(seed=11)
    player = game.players[0]
    clear_player(player)
    world = Tile("w", "Novelty World", TileKind.WORLD, 1, 1, world_color="Novelty", produces=True)
    player.tableau = [world]
    player.sections[Section.PRODUCE] = [DieColor.GREEN]

    game.resolve_phase(player, Phase.PRODUCE)

    assert player.sections[Section.PRODUCE] == [DieColor.GREEN]
    assert player.goods == [Good(world, DieColor.WHITE)]
    assert player.spent[DieColor.GREEN] == 0


def test_produce_match_bonus_makes_extra_good_marker():
    game = MancalaGame(seed=11)
    player = game.players[0]
    clear_player(player)
    world = Tile("w", "Novelty World", TileKind.WORLD, 1, 1, world_color="Novelty", produces=True)
    player.tableau = [world]
    player.match_bonuses[Phase.PRODUCE] = 1

    game.resolve_phase(player, Phase.PRODUCE)

    assert player.goods == [Good(world, DieColor.WHITE)]


def test_ship_consumes_good_marker_without_moving_stone():
    game = MancalaGame(seed=12)
    player = game.players[0]
    clear_player(player)
    player.credits = 10
    world = Tile("w", "Novelty World", TileKind.WORLD, 1, 1, world_color="Novelty", produces=True)
    player.goods = [Good(world, DieColor.BLUE)]
    player.sections[Section.SHIP] = [DieColor.PURPLE]

    game.resolve_phase(player, Phase.SHIP)

    assert player.goods == []
    assert player.sections[Section.SHIP] == [DieColor.PURPLE]
    assert player.spent[DieColor.BLUE] == 0
    assert player.spent[DieColor.PURPLE] == 0
    assert player.vp_chips == 1


def test_ship_match_bonus_adds_vp_to_first_consume():
    game = MancalaGame(seed=12)
    player = game.players[0]
    clear_player(player)
    player.credits = 3
    world = Tile("w", "Novelty World", TileKind.WORLD, 1, 1, world_color="Novelty", produces=True)
    player.goods = [Good(world, DieColor.BLUE)]
    player.sections[Section.SHIP] = [DieColor.PURPLE]
    player.match_bonuses[Phase.SHIP] = 1

    game.resolve_phase(player, Phase.SHIP)

    assert player.vp_chips == 2


def test_mancala_solo_dummy_phase_selects_shared_phase():
    game = MancalaSoloGame(seed=13, dummy_count=1)
    clear_player(game.player)
    game.player.sections[Section.EXPLORE] = [DieColor.BLUE]
    game.phase_deck = [Phase.SHIP]

    report = game.play_round()

    assert report.dummy_phases == (Phase.SHIP,)
    assert Phase.SHIP in report.selected
    assert report.round_number == 1


def test_mancala_solo_summary_counts_physical_dice_capacity():
    game = MancalaSoloGame(seed=14)

    summary = game.human_summary()

    assert summary["max_capacity"] == game.owned_die_count()
    assert summary["blue_capacity"] == game.owned_die_count(DieColor.BLUE)
    assert summary["red_capacity"] == game.owned_die_count(DieColor.RED)
    assert game.game.config.max_rounds == SOLO_ROUNDS


def test_mancala_solo_thresholds_are_tuned_for_mancala_pace():
    assert SOLO_WIN_CONDITION_MAP["great"].min_score == 38
    assert SOLO_WIN_CONDITION_MAP["triumphant"].min_score == 42
    assert SOLO_WIN_CONDITION_MAP["epic"].min_score == 46
    assert SOLO_WIN_CONDITION_MAP["builder"].min_score == 34
    assert SOLO_WIN_CONDITION_MAP["workforce"].min_max_capacity == 17
    assert SOLO_WIN_CONDITION_MAP["phase_specialist"].min_color_match_bonuses == 3
    assert SOLO_WIN_CONDITION_MAP["credit_economy"].min_credits_spent == 18
    assert SOLO_WIN_CONDITION_MAP["logistics"].min_recovery_sows == 2
    assert SOLO_WIN_CONDITION_MAP["phase_momentum"].min_phase_actions == 65


def test_mancala_solo_condition_success_uses_stone_economy_metrics():
    game = MancalaSoloGame(seed=15)
    game.player.vp_chips = 34
    summary = {
        "tableau": 12,
        "completed_tiles": 7,
        "developments": 4,
        "worlds": 6,
        "production_worlds": 4,
        "distinct_world_colors": 3,
        "vp_chips": 8,
        "max_capacity": 17,
        "credits_spent": 18,
        "recovery_sows": 2,
        "color_match_bonuses": 3,
        "phase_actions": 65,
    }

    for name in ("phase_specialist", "credit_economy", "logistics", "phase_momentum"):
        assert game.condition_success_without_summary(SOLO_WIN_CONDITION_MAP[name], summary)


def test_mancala_solo_campaigns_have_four_unique_conditions():
    canonical = set(SOLO_WIN_CONDITION_MAP)
    for campaign in SOLO_CAMPAIGNS:
        assert len(campaign.condition_names) == 4
        assert len(campaign.condition_names) == len(set(campaign.condition_names))
        assert set(campaign.condition_names) <= canonical


def test_mancala_solo_campaigns_focus_on_current_mancala_design():
    campaigns = {campaign.key: campaign.condition_names for campaign in SOLO_CAMPAIGNS}

    assert campaigns["frontier_survey"] == ("great", "colonizer", "diverse", "phase_specialist")
    assert campaigns["core_worlds"] == ("triumphant", "developer", "builder", "credit_economy")
    assert campaigns["trade_league"] == ("triumphant", "producer", "shipper", "diverse")
    assert campaigns["supply_lines"] == ("great", "workforce", "logistics", "phase_momentum")
    assert campaigns["colonial_boom"] == ("great", "colonizer", "producer", "logistics")
    assert campaigns["industrial_push"] == ("epic", "workforce", "credit_economy", "phase_momentum")
    assert campaigns["imperial_prestige"] == ("epic", "builder", "shipper", "phase_specialist")
    assert campaigns["mastery"] == ("epic", "credit_economy", "logistics", "phase_momentum")
