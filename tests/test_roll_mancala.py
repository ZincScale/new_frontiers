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
    player.bonus_goods = []
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


def test_develop_keeps_partial_worker_progress_when_short():
    game = MancalaGame(seed=7)
    player = game.players[0]
    clear_player(player)
    player.sections[Section.DEVELOP] = [DieColor.BROWN, DieColor.BLUE]
    player.dev_stack = [Construction(Tile("d", "Large Development", TileKind.DEVELOPMENT, 3, 3))]

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack[0].progress == 2
    assert player.sections[Section.DEVELOP] == []
    assert player.spent[DieColor.BROWN] == 0


def test_develop_does_not_use_credits_to_complete_build():
    game = MancalaGame(seed=8)
    player = game.players[0]
    clear_player(player)
    player.credits = 5
    tile = Tile("d", "Large Development", TileKind.DEVELOPMENT, 3, 3)
    player.dev_stack = [Construction(tile, workers=[DieColor.BROWN, DieColor.BLUE])]

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack[0].progress == 2
    assert tile not in player.tableau
    assert player.credits == 5
    assert player.spent[DieColor.BROWN] == 0
    assert player.spent[DieColor.BLUE] == 0


def test_develop_completes_with_enough_workers_and_returns_workers_to_spent():
    game = MancalaGame(seed=8)
    player = game.players[0]
    clear_player(player)
    player.credits = 5
    tile = Tile("d", "Large Development", TileKind.DEVELOPMENT, 3, 3)
    player.dev_stack = [Construction(tile, workers=[DieColor.BROWN, DieColor.BLUE])]
    player.sections[Section.DEVELOP] = [DieColor.WHITE]

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack == []
    assert tile in player.tableau
    assert player.credits == 5
    assert player.spent[DieColor.BROWN] == 1
    assert player.spent[DieColor.BLUE] == 1
    assert player.spent[DieColor.WHITE] == 1


def test_develop_match_bonus_reduces_completion_cost():
    game = MancalaGame(seed=8)
    player = game.players[0]
    clear_player(player)
    tile = Tile("d", "Discounted Development", TileKind.DEVELOPMENT, 3, 3)
    player.dev_stack = [Construction(tile, workers=[DieColor.BROWN, DieColor.BLUE])]
    player.match_bonuses[Phase.DEVELOP] = 1

    game.resolve_phase(player, Phase.DEVELOP)

    assert player.dev_stack == []
    assert tile in player.tableau
    assert player.spent[DieColor.BROWN] == 1
    assert player.spent[DieColor.BLUE] == 1


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


def test_produce_places_worker_die_as_good_outside_mancala_loop():
    game = MancalaGame(seed=11)
    player = game.players[0]
    clear_player(player)
    world = Tile("w", "Novelty World", TileKind.WORLD, 1, 1, world_color="Novelty", produces=True)
    player.tableau = [world]
    player.sections[Section.PRODUCE] = [DieColor.GREEN]

    game.resolve_phase(player, Phase.PRODUCE)

    assert player.sections[Section.PRODUCE] == []
    assert player.goods == [Good(world, DieColor.GREEN)]
    assert player.spent[DieColor.GREEN] == 0


def test_produce_match_bonus_makes_temporary_good_without_capacity():
    game = MancalaGame(seed=11)
    player = game.players[0]
    clear_player(player)
    world = Tile("w", "Novelty World", TileKind.WORLD, 1, 1, world_color="Novelty", produces=True)
    player.tableau = [world]
    player.match_bonuses[Phase.PRODUCE] = 1

    game.resolve_phase(player, Phase.PRODUCE)

    assert player.goods == []
    assert player.bonus_goods == [world]


def test_ship_moves_worker_and_shipped_good_to_spent():
    game = MancalaGame(seed=12)
    player = game.players[0]
    clear_player(player)
    player.credits = 10
    world = Tile("w", "Novelty World", TileKind.WORLD, 1, 1, world_color="Novelty", produces=True)
    player.goods = [Good(world, DieColor.BLUE)]
    player.sections[Section.SHIP] = [DieColor.PURPLE]

    game.resolve_phase(player, Phase.SHIP)

    assert player.goods == []
    assert player.spent[DieColor.BLUE] == 1
    assert player.spent[DieColor.PURPLE] == 1
    assert player.vp_chips == 2


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

    assert player.vp_chips == 3


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
    assert SOLO_WIN_CONDITION_MAP["great"].min_score == 32
    assert SOLO_WIN_CONDITION_MAP["triumphant"].min_score == 34
    assert SOLO_WIN_CONDITION_MAP["epic"].min_score == 35
    assert SOLO_WIN_CONDITION_MAP["industrial"].min_max_capacity == 17
    assert SOLO_WIN_CONDITION_MAP["military"].min_red_capacity == 4
    assert SOLO_WIN_CONDITION_MAP["discovery"].min_blue_capacity == 4


def test_mancala_solo_campaigns_have_four_unique_conditions():
    canonical = set(SOLO_WIN_CONDITION_MAP)
    for campaign in SOLO_CAMPAIGNS:
        assert len(campaign.condition_names) == 4
        assert len(campaign.condition_names) == len(set(campaign.condition_names))
        assert set(campaign.condition_names) <= canonical
