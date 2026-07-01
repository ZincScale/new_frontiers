import pytest

from tiny_galaxies.cards import PLANETS, RIVAL_EMPIRES, UPGRADES
from tiny_galaxies.engine import GameConfig, UpgradeGame
from tiny_galaxies.model import DieFace, Mission
from tiny_galaxies.solo_simulate import apply_rival_difficulty, difficulty_tuning, parse_sweep_values, run_profile
from tiny_galaxies.simulate import rotate_specs


def upgrade(upgrade_id):
    return next(card for card in UPGRADES if card.id == upgrade_id)


def test_rotate_specs_changes_player_order_without_losing_specs():
    specs = [("P1", "frontier_union", "mobility"), ("P2", "star_cartel", "economy"), ("P3", "archive_compact", "culture")]

    rotated = rotate_specs(specs, 1)

    assert rotated == [specs[1], specs[2], specs[0]]


def test_upgrade_market_starts_at_three_cards():
    game = UpgradeGame(seed=1)

    assert len(game.upgrade_market) == 3
    assert len(game.planet_market) == 4


def test_planet_deck_has_full_unique_set():
    planet_ids = [planet.id for planet in PLANETS]

    assert len(PLANETS) == 36
    assert len(planet_ids) == len(set(planet_ids))


def test_planet_market_scales_with_player_count():
    game = UpgradeGame(
        players=[
            ("P1", "frontier_union", "mobility"),
            ("P2", "star_cartel", "economy"),
            ("P3", "archive_compact", "culture"),
            ("P4", "settlement_charter", "colonizer"),
        ],
        seed=11,
    )

    assert len(game.planet_market) == 6


def test_buy_upgrade_spends_resource_and_refills_market():
    game = UpgradeGame(seed=2)
    player = game.players[0]
    player.energy = 3
    target = game.upgrade_market[0]

    game.buy_upgrade(player, target, spend="energy")

    assert player.energy == 0
    assert target in player.upgrades
    assert len(game.upgrade_market) == 3
    assert target not in game.upgrade_market
    assert game.discarded_upgrades == []


def test_upgrade_module_can_be_disabled_for_baseline_runs():
    game = UpgradeGame(seed=12, config=GameConfig(enable_upgrades=False))
    player = game.players[0]

    assert game.upgrade_market == []
    assert game.auto_buy_upgrade(player) is None


def test_upgrade_limit_requires_replacement():
    game = UpgradeGame(seed=3)
    player = game.players[0]
    player.energy = 6
    player.upgrades = [upgrade("warp_couriers"), upgrade("orbital_refineries"), upgrade("trade_league")]
    target = game.upgrade_market[0]

    with pytest.raises(ValueError):
        game.buy_upgrade(player, target, spend="energy")

    game.buy_upgrade(player, target, spend="energy", replace=player.upgrades[0])

    assert len(player.upgrades) == 3
    assert target in player.upgrades


def test_upgrade_only_triggers_on_matching_face():
    game = UpgradeGame(seed=4)
    player = game.players[0]
    player.upgrades = [upgrade("orbital_refineries")]
    player.energy = 0
    player.culture = 0

    game.use_die(player, DieFace.CULTURE)

    assert player.energy == 0
    assert player.culture == 1

    game.use_die(player, DieFace.ENERGY)

    assert player.energy == 3


def test_face_upgrade_can_accelerate_colony_claims():
    game = UpgradeGame(seed=5)
    player = game.players[0]
    player.upgrades = [upgrade("colony_prefabs")]
    player.energy = 0
    player.culture = 0
    planet = next(card for card in game.planet_market if card.track_length <= 3)
    player.available_ships -= 1
    player.missions = [Mission(planet, progress=planet.track_length - 1)]

    game.use_die(player, DieFace.COLONY)

    assert planet in player.colonies
    assert player.vp >= planet.vp
    assert player.missions == []


def test_settler_mandate_scores_when_colony_die_claims_planet():
    game = UpgradeGame(seed=35)
    player = game.players[0]
    player.upgrades = [upgrade("colony_prefabs"), upgrade("settler_mandate")]
    player.energy = 0
    player.culture = 0
    planet = game.planet_market[0]
    player.available_ships -= 1
    player.missions = [Mission(planet, progress=planet.track_length - 1)]

    game.use_die(player, DieFace.COLONY)

    assert planet in player.colonies
    assert player.culture == 1
    assert player.vp >= planet.vp + 1


def test_colonizer_upgrade_package_scores_colonies_at_endgame():
    game = UpgradeGame(seed=37)
    player = game.players[0]
    player.upgrades = [upgrade("colony_prefabs"), upgrade("settler_mandate")]
    player.colonies = [PLANETS[0], PLANETS[1], PLANETS[2]]

    assert game.endgame_bonus(player) == 2


def test_empire_vp_requires_colonized_planets():
    game = UpgradeGame(seed=46)
    player = game.players[0]
    player.empire_level = 6

    assert game.empire_vp_score(player) == 0

    player.colonies = [PLANETS[0], PLANETS[1]]

    assert game.empire_vp_score(player) == 6


def test_zero_colony_empire_cannot_be_a_win_condition():
    game = UpgradeGame(seed=47)
    player = game.players[0]
    player.empire_level = 6
    player.energy = game.config.resource_cap
    player.culture = game.config.resource_cap
    player.upgrades = [upgrade("warp_couriers"), upgrade("frontier_beacons")]
    player.landed = [game.planet_market[0], game.planet_market[1]]

    assert player.colonies == []
    assert game.current_score(player) == 0
    assert game.final_scores()[0][1] < game.config.target_vp
    assert not game.game_over()


def test_frontier_upgrade_package_scores_active_presence_at_endgame():
    game = UpgradeGame(seed=38)
    player = game.players[0]
    player.upgrades = [upgrade("warp_couriers"), upgrade("frontier_beacons")]
    player.missions = [Mission(game.planet_market[0]), Mission(game.planet_market[1])]
    player.landed = [game.planet_market[2], game.planet_market[3]]

    assert game.endgame_bonus(player) == 3


def test_colony_prefabs_can_start_mission_when_none_are_active():
    game = UpgradeGame(seed=22)
    player = game.players[0]
    player.upgrades = [upgrade("colony_prefabs")]
    player.empire_level = 6
    player.energy = 2
    player.culture = 0

    game.use_die(player, DieFace.COLONY)

    assert len(player.missions) == 1
    assert player.available_ships == 1
    assert player.energy == 0


def test_colony_prefabs_can_use_culture_for_first_mission():
    game = UpgradeGame(seed=45)
    player = game.players[0]
    player.upgrades = [upgrade("colony_prefabs")]
    player.empire_level = 6
    player.energy = 0
    player.culture = 2

    game.use_die(player, DieFace.COLONY)

    assert len(player.missions) == 1
    assert player.culture == 0


def test_colony_face_without_upgrade_does_not_advance_mission():
    game = UpgradeGame(seed=29)
    player = game.players[0]
    player.energy = 0
    player.culture = 0
    planet = game.planet_market[0]
    player.available_ships -= 1
    player.missions = [Mission(planet)]

    game.use_die(player, DieFace.COLONY)

    assert player.missions[0].progress == 0


def test_emergency_protocol_spends_culture_to_advance_without_matching_face():
    game = UpgradeGame(seed=30)
    player = game.players[0]
    player.culture = 1
    planet = next(planet for planet in game.planet_market if planet.colonize_face is DieFace.ECONOMY)
    player.available_ships -= 1
    player.missions = [Mission(planet, progress=max(0, planet.track_length - 2))]

    assert game.can_use_emergency_protocol(player, [DieFace.ENERGY, DieFace.CULTURE])
    assert game.use_emergency_protocol(player)
    assert player.culture == 0
    assert player.missions[0].progress == planet.track_length - 1


def test_emergency_protocol_unavailable_with_matching_progress_face():
    game = UpgradeGame(seed=31)
    player = game.players[0]
    player.culture = 1
    planet = next(planet for planet in game.planet_market if planet.colonize_face is DieFace.ECONOMY)
    player.available_ships -= 1
    player.missions = [Mission(planet)]

    assert not game.can_use_emergency_protocol(player, [DieFace.ECONOMY])


def test_move_die_starts_a_planet_mission():
    game = UpgradeGame(seed=8)
    player = game.players[0]
    player.energy = 3
    player.culture = 3

    game.use_die(player, DieFace.MOVE)

    assert len(player.missions) == 1
    assert player.missions[0].planet in game.planet_market
    assert player.available_ships == 1


def test_low_resource_move_lands_on_surface_for_income():
    game = UpgradeGame(seed=13)
    player = game.players[0]
    player.energy = 0
    player.culture = 0

    game.use_die(player, DieFace.MOVE)

    assert len(player.landed) == 1
    assert len(player.missions) == 0
    assert player.energy + player.culture > 0


def test_move_die_redeploys_landed_ship_when_none_are_available():
    game = UpgradeGame(seed=42)
    player = game.players[0]
    player.available_ships = 0
    player.landed = [game.planet_market[0], game.planet_market[1]]

    game.use_die(player, DieFace.MOVE)

    assert len(player.landed) == 1
    assert len(player.missions) == 0
    assert player.available_ships == 1


def test_landed_ship_makes_move_face_valuable():
    game = UpgradeGame(seed=43)
    player = game.players[0]
    player.available_ships = 0
    player.landed = [game.planet_market[0]]

    assert game.move_face_has_value(player)


def test_redeploy_does_not_add_mission_when_one_is_already_active():
    game = UpgradeGame(seed=44)
    player = game.players[0]
    player.available_ships = 0
    player.landed = [game.planet_market[0]]
    player.missions = [Mission(game.planet_market[1])]

    game.use_die(player, DieFace.MOVE)

    assert len(player.landed) == 0
    assert len(player.missions) == 1
    assert player.available_ships == 1


def test_claimed_planet_enters_tableau_and_refills_market():
    game = UpgradeGame(seed=9)
    player = game.players[0]
    planet = game.planet_market[0]
    player.available_ships -= 1
    player.missions = [Mission(planet, progress=planet.track_length - 1)]

    game.advance_specific_mission(player, player.missions[0], 1)

    assert planet in player.colonies
    assert planet not in game.planet_market
    assert len(game.planet_market) == 4
    assert player.available_ships == 2


def test_ship_count_does_not_exceed_physical_limit():
    game = UpgradeGame(seed=10, config=GameConfig(max_ships=4))
    player = game.players[0]
    player.upgrades = [upgrade("warp_couriers")]
    player.available_ships = 3
    player.missions = [Mission(game.planet_market[0])]

    game.use_die(player, DieFace.MOVE)

    assert player.available_ships + len(player.missions) <= 4


def test_warp_couriers_gains_resource_when_ship_moves_to_orbit_track():
    game = UpgradeGame(seed=20)
    player = game.players[0]
    player.upgrades = [upgrade("warp_couriers")]
    player.energy = 3
    player.culture = 4

    game.use_die(player, DieFace.MOVE)

    assert len(player.missions) == 1
    assert player.energy == 4
    assert player.culture == 4
    assert player.available_ships == 1


def test_warp_couriers_does_not_trigger_when_ship_lands_on_surface():
    game = UpgradeGame(seed=48)
    player = game.players[0]
    player.upgrades = [upgrade("warp_couriers")]
    player.energy = 0
    player.culture = 0

    game.use_die(player, DieFace.MOVE)

    assert len(player.landed) == 1
    assert player.energy + player.culture == 1


def test_frontier_beacons_does_not_advance_new_zero_progress_mission():
    game = UpgradeGame(seed=21)
    player = game.players[0]
    player.upgrades = [upgrade("frontier_beacons")]
    player.energy = 3
    player.culture = 3
    player.colonies = [PLANETS[0]]

    game.use_die(player, DieFace.MOVE)

    assert len(player.missions) == 1
    assert player.missions[0].progress == 0


def test_frontier_beacons_can_pay_energy_for_first_foothold_progress():
    game = UpgradeGame(seed=39)
    player = game.players[0]
    player.upgrades = [upgrade("frontier_beacons")]
    player.energy = 2
    player.culture = 3

    game.use_die(player, DieFace.MOVE)

    assert len(player.missions) == 1
    assert player.missions[0].progress == 1
    assert player.energy == 1


def test_dead_move_face_gets_lower_priority_when_no_ships_are_available():
    game = UpgradeGame(seed=40)
    player = game.players[0]
    player.available_ships = 0
    player.missions = [Mission(game.planet_market[0])]

    assert game.face_priority(player, DieFace.MOVE) < game.face_priority(player, DieFace.COLONY)


def test_frontier_beacons_keeps_committed_move_face_relevant():
    game = UpgradeGame(seed=41)
    player = game.players[0]
    player.upgrades = [upgrade("frontier_beacons")]
    player.available_ships = 0
    player.energy = 1
    player.missions = [Mission(game.planet_market[0])]

    assert game.face_priority(player, DieFace.MOVE) > 0


def test_frontier_beacons_advances_when_fleet_is_fully_committed():
    game = UpgradeGame(seed=32)
    player = game.players[0]
    player.upgrades = [upgrade("frontier_beacons")]
    player.energy = 1
    player.available_ships = 0
    player.missions = [Mission(game.planet_market[0])]

    game.use_die(player, DieFace.MOVE)

    assert player.missions[0].progress == 1
    assert player.energy == 0


def test_soft_power_networks_advances_only_once_per_turn():
    game = UpgradeGame(seed=33)
    player = game.players[0]
    planet = next(planet for planet in game.planet_market if planet.colonize_face is DieFace.DIPLOMACY)
    player.upgrades = [upgrade("soft_power_networks")]
    player.available_ships -= 1
    player.missions = [Mission(planet)]
    game._turn_scored_abilities = set()

    game.use_die(player, DieFace.CULTURE)
    game.use_die(player, DieFace.CULTURE)

    assert player.missions[0].progress == 1


def test_resources_are_capped():
    game = UpgradeGame(seed=14)
    player = game.players[0]
    player.energy = 6

    game.gain_resource(player, PLANETS[0].resource, 5)

    assert player.energy <= game.config.resource_cap


def test_orbital_refineries_turns_capped_energy_into_economy_progress():
    game = UpgradeGame(seed=23)
    player = game.players[0]
    planet = next(planet for planet in game.planet_market if planet.colonize_face is DieFace.ECONOMY)
    player.upgrades = [upgrade("orbital_refineries")]
    player.energy = game.config.resource_cap
    player.available_ships -= 1
    player.missions = [Mission(planet)]

    game.use_die(player, DieFace.ENERGY)

    assert player.energy == game.config.resource_cap
    assert player.missions[0].progress == 1


def test_capped_energy_conversion_only_happens_once_per_turn():
    game = UpgradeGame(seed=28)
    player = game.players[0]
    planet = next(planet for planet in game.planet_market if planet.colonize_face is DieFace.ECONOMY)
    player.upgrades = [upgrade("orbital_refineries")]
    player.energy = game.config.resource_cap
    player.available_ships -= 1
    player.missions = [Mission(planet)]
    game._turn_scored_abilities = set()

    game.use_die(player, DieFace.ENERGY)
    game.use_die(player, DieFace.ENERGY)

    assert player.missions[0].progress == 1


def test_merchant_convoys_turns_capped_energy_into_economy_progress():
    game = UpgradeGame(seed=34)
    player = game.players[0]
    planet = next(planet for planet in game.planet_market if planet.colonize_face is DieFace.ECONOMY)
    player.upgrades = [upgrade("merchant_convoys")]
    player.energy = game.config.resource_cap
    player.colonies = [PLANETS[0]]
    player.available_ships -= 1
    player.missions = [Mission(planet)]
    game._turn_scored_abilities = set()

    game.use_die(player, DieFace.ECONOMY)

    assert player.energy == game.config.resource_cap
    assert player.missions[0].progress == 2


def test_merchant_convoys_does_not_overflow_without_colonies():
    game = UpgradeGame(seed=36)
    player = game.players[0]
    planet = next(planet for planet in game.planet_market if planet.colonize_face is DieFace.ECONOMY)
    player.upgrades = [upgrade("merchant_convoys")]
    player.energy = game.config.resource_cap
    player.available_ships -= 1
    player.missions = [Mission(planet)]
    game._turn_scored_abilities = set()

    game.use_die(player, DieFace.ECONOMY)

    assert player.missions[0].progress == 1


def test_cultural_archives_turns_capped_culture_into_diplomacy_progress():
    game = UpgradeGame(seed=24)
    player = game.players[0]
    planet = next(planet for planet in game.planet_market if planet.colonize_face is DieFace.DIPLOMACY)
    player.upgrades = [upgrade("cultural_archives")]
    player.culture = game.config.resource_cap
    player.colonies = [PLANETS[0]]
    player.available_ships -= 1
    player.missions = [Mission(planet)]

    game.use_die(player, DieFace.CULTURE)

    assert player.culture == game.config.resource_cap
    assert player.missions[0].progress == 1


def test_colony_face_can_upgrade_empire():
    game = UpgradeGame(seed=15)
    player = game.players[0]
    player.energy = 2

    game.use_die(player, DieFace.COLONY)

    assert player.empire_level == 2
    assert player.energy == 0
    assert player.available_ships == 3


def test_converter_turns_bad_setup_roll_into_move():
    game = UpgradeGame(seed=16)
    player = game.players[0]
    roll = [DieFace.ENERGY, DieFace.CULTURE, DieFace.ECONOMY]

    mitigated = game.convert_for_missing_setup(player, roll)

    assert mitigated == [DieFace.MOVE]


def test_converter_turns_off_after_second_upgrade():
    game = UpgradeGame(seed=18)
    player = game.players[0]
    player.upgrades = [upgrade("warp_couriers"), upgrade("orbital_refineries")]
    roll = [DieFace.ENERGY, DieFace.CULTURE, DieFace.ECONOMY]

    mitigated = game.convert_for_missing_setup(player, roll)

    assert mitigated == roll


def test_converter_stays_available_when_upgrade_module_is_disabled():
    game = UpgradeGame(seed=19, config=GameConfig(enable_upgrades=False))
    player = game.players[0]
    player.upgrades = [upgrade("warp_couriers"), upgrade("orbital_refineries")]
    roll = [DieFace.ENERGY, DieFace.CULTURE, DieFace.ECONOMY]

    mitigated = game.convert_for_missing_setup(player, roll)

    assert mitigated == [DieFace.MOVE]


def test_player_can_spend_culture_to_follow_available_die():
    game = UpgradeGame(seed=25)
    player = game.players[0]
    player.culture = 2
    player.energy = 3

    followed = game.auto_follow(player, [DieFace.ENERGY])

    assert followed is DieFace.ENERGY
    assert player.culture == 1


def test_player_cannot_follow_without_culture():
    game = UpgradeGame(seed=26)
    player = game.players[0]
    player.culture = 0

    followed = game.auto_follow(player, [DieFace.MOVE])

    assert followed is None


def test_player_can_follow_only_once_per_round():
    game = UpgradeGame(seed=27)
    player = game.players[0]
    player.culture = 3
    game._followed_this_round = set()

    first = game.auto_follow(player, [DieFace.ENERGY])
    second = game.auto_follow(player, [DieFace.ENERGY])

    assert first is DieFace.ENERGY
    assert second is None


def test_personality_biases_generic_market_purchase():
    game = UpgradeGame(seed=6)
    player = game.players[0]
    player.energy = 3
    player.culture = 3
    game.upgrade_market = [
        upgrade("orbital_refineries"),
        upgrade("warp_couriers"),
        upgrade("trade_league"),
    ]

    bought = game.auto_buy_upgrade(player)

    assert bought.id == "warp_couriers"


def test_simulation_keeps_tableaus_to_three_upgrades():
    game = UpgradeGame(
        players=[
            ("P1", "frontier_union", "mobility"),
            ("P2", "star_cartel", "economy"),
            ("P3", "archive_compact", "culture"),
        ],
        seed=7,
        config=GameConfig(max_turns=18),
    )

    scores, _reports = game.play()

    assert scores
    assert all(len(player.upgrades) <= 3 for player in game.players)
    assert any(player.upgrades for player in game.players)


def test_solo_opponents_have_distinct_priorities_and_pressure():
    ids = [profile.id for profile in RIVAL_EMPIRES]
    pressures = {profile.pressure for profile in RIVAL_EMPIRES}
    attacks = {profile.attack for profile in RIVAL_EMPIRES}

    assert len(RIVAL_EMPIRES) >= 4
    assert len(ids) == len(set(ids))
    assert len(pressures) == len(RIVAL_EMPIRES)
    assert len(attacks) == len(RIVAL_EMPIRES)


def test_rival_action_order_uses_profile_priority():
    game = UpgradeGame(seed=17)
    swarm = next(profile for profile in RIVAL_EMPIRES if profile.id == "devourer_swarm")
    roll = [DieFace.CULTURE, DieFace.MOVE, DieFace.ECONOMY]

    assert game.rival_action_order(swarm, roll)[0] is DieFace.MOVE


def test_rival_empire_profile_attaches_to_player_seat():
    game = UpgradeGame(
        players=[
            ("Human", "frontier_union", "mobility"),
            ("Rival", "frontier_union", "mobility", "devourer_swarm"),
        ],
        seed=49,
    )

    assert game.players[0].rival_profile is None
    assert game.players[1].rival_profile.id == "devourer_swarm"


def test_rival_difficulty_sets_starting_state():
    game = UpgradeGame(
        players=[
            ("Human", "frontier_union", "mobility"),
            ("Rival", "frontier_union", "mobility", "devourer_swarm"),
        ],
        seed=55,
    )

    difficulty = apply_rival_difficulty(game, "standard")
    rival = game.players[1]

    assert difficulty.id == "standard"
    assert rival.empire_level == 1
    assert rival.energy == 2
    assert rival.culture == 1
    assert rival.vp == 2
    assert rival.available_ships == game.empire_step(1).ships


def test_rival_difficulty_tuning_can_override_values():
    tuning = difficulty_tuning("standard", energy=3, culture=2, vp=4)

    assert tuning.id == "standard"
    assert tuning.empire_level == 1
    assert tuning.energy == 3
    assert tuning.culture == 2
    assert tuning.vp == 4


def test_parse_sweep_values():
    assert parse_sweep_values("0, 2,4") == [0, 2, 4]


def test_rival_empire_pressure_regresses_orbiting_ship():
    game = UpgradeGame(
        players=[
            ("Human", "frontier_union", "mobility"),
            ("Rival", "frontier_union", "mobility", "devourer_swarm"),
        ],
        seed=50,
    )
    human = game.players[0]
    rival = game.players[1]
    human.missions = [Mission(game.planet_market[0], progress=2)]

    game.apply_rival_pressure(rival, game.planet_market[1])

    assert human.missions[0].progress == 1


def test_rival_empire_tax_pressure_reduces_highest_resource():
    game = UpgradeGame(
        players=[
            ("Human", "frontier_union", "mobility"),
            ("Rival", "star_cartel", "economy", "iron_directorate"),
        ],
        seed=51,
    )
    human = game.players[0]
    rival = game.players[1]
    human.energy = 5
    human.culture = 2

    game.apply_rival_pressure(rival, game.planet_market[0])

    assert human.energy == 4
    assert human.culture == 2


def test_rival_empire_momentum_advances_colony_track():
    game = UpgradeGame(
        players=[
            ("Human", "frontier_union", "mobility"),
            ("Rival", "frontier_union", "mobility", "devourer_swarm"),
        ],
        seed=53,
    )
    rival = game.players[1]
    rival.missions = [Mission(game.planet_market[0], progress=1)]
    game._turn_faces = [DieFace.MOVE]

    game.apply_rival_momentum(rival)

    assert rival.missions[0].progress == 2


def test_devourer_momentum_does_not_advance_new_orbiting_ship():
    game = UpgradeGame(
        players=[
            ("Human", "frontier_union", "mobility"),
            ("Rival", "frontier_union", "mobility", "devourer_swarm"),
        ],
        seed=54,
    )
    rival = game.players[1]
    rival.missions = [Mission(game.planet_market[0], progress=0)]
    game._turn_faces = [DieFace.MOVE]

    game.apply_rival_momentum(rival)

    assert rival.missions[0].progress == 0


def test_solo_simulator_runs_rival_empire_profile():
    result = run_profile(
        "frontier_union:mobility",
        "devourer_swarm",
        "training",
        games=3,
        seed=52,
        config=GameConfig(max_turns=12),
    )

    assert result["wins"]["Human"] + result["wins"]["Rival"] == 3
    assert result["average_metrics"]["Rival"]["colonies"] >= 0
