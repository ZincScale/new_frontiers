from __future__ import annotations

from .model import DevelopmentTile, Good, Powers, SettleKind, WorldKind, WorldTile


def score_military(view):
    return view.military_colony_count * 3


def score_production(view):
    return view.production_colony_count * 3


def score_windfall(view):
    return view.windfall_colony_count * 3


def score_developments(view):
    return view.development_count


def score_large_developments(view):
    return view.large_development_count * 4


def score_colonies(view):
    return view.colony_count


def score_goods(view):
    return view.goods_count * 2


def score_vp_chips(view):
    return view.vp_chips // 2


DEVELOPMENTS = [
    # Small developments, using Race for the Galaxy cards as simplified templates.
    DevelopmentTile("investment_credits", "Investment Credits", 2, 1, 1, powers=Powers(develop_discount=1)),
    DevelopmentTile("contact_specialist", "Contact Specialist", 2, 1, 1, powers=Powers(settle_discount=1)),
    DevelopmentTile("research_labs", "Research Labs", 2, 1, 1, powers=Powers(explore_extra=1)),
    DevelopmentTile("new_economy", "New Economy", 3, 1, 1, powers=Powers(consume_credit_per_good=1)),
    DevelopmentTile("consumer_markets", "Consumer Markets", 3, 1, 1, powers=Powers(consume_vp_per_good=1)),
    DevelopmentTile("export_duties", "Export Duties", 3, 1, 1, powers=Powers(trade_bonus=1)),
    DevelopmentTile("space_marines", "Space Marines", 3, 1, 1, powers=Powers(military=2)),
    DevelopmentTile("mining_robots", "Mining Robots", 3, 2, 1, powers=Powers(produce_credit=1)),
    DevelopmentTile("genetics_lab", "Genetics Lab", 3, 2, 1, powers=Powers(consume_vp_per_good=1, explore_extra=1)),
    DevelopmentTile("interstellar_bank", "Interstellar Bank", 3, 2, 1, powers=Powers(develop_discount=1, trade_bonus=1)),
    DevelopmentTile("public_works", "Public Works", 3, 2, 1, powers=Powers(develop_discount=1)),
    DevelopmentTile("trade_league", "Trade League", 3, 2, 1, powers=Powers(trade_bonus=1, consume_credit_per_good=1)),
    DevelopmentTile("diversified_economy", "Diversified Economy", 4, 2, 1, powers=Powers(consume_vp_per_good=1, consume_credit_per_good=1)),
    DevelopmentTile("expedition_force", "Expedition Force", 4, 2, 1, powers=Powers(military=1, explore_extra=1)),
    DevelopmentTile("improved_logistics", "Improved Logistics", 4, 2, 1, powers=Powers(settle_discount=1, military_settle_vp=1)),
    DevelopmentTile("replicant_robots", "Replicant Robots", 4, 2, 1, powers=Powers(develop_discount=1, settle_discount=1)),
    DevelopmentTile("terraforming_robots", "Terraforming Robots", 4, 2, 1, powers=Powers(settle_discount=2)),
    DevelopmentTile("alien_tech_institute", "Alien Tech Institute", 4, 2, 1, powers=Powers(explore_extra=2, trade_bonus=1)),
    DevelopmentTile("mercenary_fleet", "Mercenary Fleet", 4, 2, 1, powers=Powers(military=3)),
    DevelopmentTile("colonial_contracts", "Colonial Contracts", 4, 2, 1, powers=Powers(settle_discount=1, produce_credit=1)),
    DevelopmentTile("galactic_advertisers", "Galactic Advertisers", 4, 2, 1, powers=Powers(trade_bonus=2)),
    DevelopmentTile("consumer_consortium", "Consumer Consortium", 5, 3, 1, powers=Powers(consume_vp_per_good=2)),
    DevelopmentTile("mining_conglomerate", "Mining Conglomerate", 5, 3, 1, powers=Powers(produce_credit=1, trade_bonus=1)),
    DevelopmentTile("military_academy", "Military Academy", 5, 3, 1, powers=Powers(military=2, military_settle_vp=1)),
    # Large developments, the board-game analogue of RFTG 6-cost developments.
    DevelopmentTile("galactic_imperium", "Galactic Imperium", 9, 0, 3, large=True, powers=Powers(military=2, military_settle_vp=1), score_bonus=score_military),
    DevelopmentTile("free_trade_association", "Free Trade Association", 9, 0, 3, large=True, powers=Powers(trade_bonus=2), score_bonus=score_goods),
    DevelopmentTile("galactic_federation", "Galactic Federation", 9, 0, 3, large=True, powers=Powers(develop_discount=1), score_bonus=score_developments),
    DevelopmentTile("merchant_guild", "Merchant Guild", 9, 0, 3, large=True, powers=Powers(trade_bonus=1, consume_credit_per_good=1), score_bonus=score_production),
    DevelopmentTile("mining_league", "Mining League", 9, 0, 3, large=True, powers=Powers(produce_credit=2), score_bonus=score_production),
    DevelopmentTile("new_galactic_order", "New Galactic Order", 9, 0, 3, large=True, powers=Powers(military=3), score_bonus=score_military),
    DevelopmentTile("pan_galactic_league", "Pan-Galactic League", 9, 0, 3, large=True, powers=Powers(explore_extra=2), score_bonus=score_colonies),
    DevelopmentTile("galactic_renaissance", "Galactic Renaissance", 9, 0, 3, large=True, powers=Powers(develop_discount=1, consume_credit_per_good=1), score_bonus=score_developments),
    DevelopmentTile("galactic_survey_seti", "Galactic Survey: SETI", 9, 0, 3, large=True, powers=Powers(explore_extra=3), score_bonus=score_large_developments),
    DevelopmentTile("terraforming_guild", "Terraforming Guild", 9, 0, 3, large=True, powers=Powers(settle_discount=2), score_bonus=score_colonies),
    DevelopmentTile("trade_federation", "Trade Federation", 9, 0, 3, large=True, powers=Powers(consume_vp_per_good=1, trade_bonus=1), score_bonus=score_vp_chips),
    DevelopmentTile("alien_research_program", "Alien Research Program", 9, 0, 3, large=True, powers=Powers(explore_extra=2, trade_bonus=1), score_bonus=score_windfall),
]


WORLDS = [
    # Start/home-world style civilian and military templates.
    WorldTile("old_earth", "Old Earth", WorldKind.GRAY, SettleKind.CIVILIAN, 1, 1, 1),
    WorldTile("alpha_centauri", "Alpha Centauri", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 2, 1, 1, Good.NOVELTY),
    WorldTile("epsilon_eridani", "Epsilon Eridani", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 3, 1, 2, Good.RARE),
    WorldTile("new_vinland", "New Vinland", WorldKind.WINDFALL, SettleKind.CIVILIAN, 2, 1, 1, Good.NOVELTY),
    WorldTile("earths_lost_colony", "Earth's Lost Colony", WorldKind.GRAY, SettleKind.CIVILIAN, 2, 1, 1, powers=Powers(explore_extra=1)),
    WorldTile("new_sparta", "New Sparta", WorldKind.GRAY, SettleKind.MILITARY, 2, 1, 2, powers=Powers(military=1)),
    # Civilian gray worlds.
    WorldTile("galactic_resort", "Galactic Resort", WorldKind.GRAY, SettleKind.CIVILIAN, 2, 1, 1, powers=Powers(consume_vp_per_good=1)),
    WorldTile("space_port", "Space Port", WorldKind.GRAY, SettleKind.CIVILIAN, 2, 1, 1, powers=Powers(trade_bonus=1)),
    WorldTile("former_penal_colony", "Former Penal Colony", WorldKind.GRAY, SettleKind.CIVILIAN, 3, 1, 2, powers=Powers(settle_discount=1)),
    WorldTile("ancient_race", "Ancient Race", WorldKind.GRAY, SettleKind.CIVILIAN, 3, 1, 2, powers=Powers(explore_extra=1)),
    WorldTile("galactic_capitol", "Galactic Capitol", WorldKind.GRAY, SettleKind.CIVILIAN, 5, 2, 4, powers=Powers(consume_credit_per_good=1)),
    WorldTile("alien_rosetta_stone_world", "Alien Rosetta Stone World", WorldKind.GRAY, SettleKind.CIVILIAN, 5, 2, 4, powers=Powers(explore_extra=2)),
    # Novelty worlds.
    WorldTile("artists_colony", "Artists Colony", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 2, 1, 1, Good.NOVELTY),
    WorldTile("spice_world", "Spice World", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 2, 1, 1, Good.NOVELTY),
    WorldTile("alien_toy_shop", "Alien Toy Shop", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 3, 1, 2, Good.NOVELTY, powers=Powers(trade_bonus=1)),
    WorldTile("tourist_world", "Tourist World", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 3, 1, 2, Good.NOVELTY, powers=Powers(consume_vp_per_good=1)),
    WorldTile("luxury_world", "Luxury World", WorldKind.WINDFALL, SettleKind.CIVILIAN, 2, 1, 1, Good.NOVELTY),
    WorldTile("designer_species", "Designer Species", WorldKind.WINDFALL, SettleKind.CIVILIAN, 3, 1, 2, Good.NOVELTY, powers=Powers(consume_credit_per_good=1)),
    WorldTile("rebel_cantina", "Rebel Cantina", WorldKind.WINDFALL, SettleKind.MILITARY, 3, 1, 3, Good.NOVELTY, powers=Powers(trade_bonus=1)),
    WorldTile("raider_haven", "Raider Haven", WorldKind.WINDFALL, SettleKind.MILITARY, 3, 1, 3, Good.NOVELTY),
    # Rare element worlds.
    WorldTile("mining_world", "Mining World", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 3, 1, 2, Good.RARE),
    WorldTile("ore_refinery", "Ore Refinery", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 4, 1, 2, Good.RARE, powers=Powers(produce_credit=1)),
    WorldTile("gem_world", "Gem World", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 4, 2, 3, Good.RARE),
    WorldTile("industrial_mines", "Industrial Mines", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 5, 2, 4, Good.RARE, powers=Powers(trade_bonus=1)),
    WorldTile("rare_element_world", "Rare Element World", WorldKind.WINDFALL, SettleKind.CIVILIAN, 3, 1, 2, Good.RARE),
    WorldTile("asteroid_belt", "Asteroid Belt", WorldKind.WINDFALL, SettleKind.CIVILIAN, 4, 2, 3, Good.RARE),
    WorldTile("rebel_miners", "Rebel Miners", WorldKind.WINDFALL, SettleKind.MILITARY, 4, 1, 4, Good.RARE),
    WorldTile("blaster_gem_mines", "Blaster Gem Mines", WorldKind.PRODUCTION, SettleKind.MILITARY, 4, 1, 3, Good.RARE),
    # Genes worlds.
    WorldTile("lost_species_ark_world", "Lost Species Ark World", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 4, 1, 2, Good.GENES),
    WorldTile("gene_labs", "Gene Labs", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 4, 1, 2, Good.GENES, powers=Powers(consume_vp_per_good=1)),
    WorldTile("uplift_world", "Uplift World", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 5, 2, 4, Good.GENES),
    WorldTile("cloning_world", "Cloning World", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 6, 2, 5, Good.GENES, powers=Powers(produce_credit=1)),
    WorldTile("prehistoric_world", "Prehistoric World", WorldKind.WINDFALL, SettleKind.CIVILIAN, 4, 2, 3, Good.GENES),
    WorldTile("uplift_code", "Uplift Code", WorldKind.WINDFALL, SettleKind.CIVILIAN, 5, 2, 4, Good.GENES, powers=Powers(explore_extra=1)),
    WorldTile("rebel_warrior_race", "Rebel Warrior Race", WorldKind.PRODUCTION, SettleKind.MILITARY, 4, 1, 3, Good.GENES, powers=Powers(military=1)),
    WorldTile("uplift_revolt_world", "Uplift Revolt World", WorldKind.WINDFALL, SettleKind.MILITARY, 5, 2, 5, Good.GENES, powers=Powers(military=1)),
    # Alien worlds.
    WorldTile("alien_research_team", "Alien Research Team", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 5, 2, 4, Good.ALIEN, powers=Powers(explore_extra=1)),
    WorldTile("alien_robotic_factory", "Alien Robotic Factory", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 6, 3, 6, Good.ALIEN, powers=Powers(produce_credit=1)),
    WorldTile("alien_oort_cloud_refinery", "Alien Oort Cloud Refinery", WorldKind.PRODUCTION, SettleKind.CIVILIAN, 6, 3, 5, Good.ALIEN, powers=Powers(trade_bonus=1)),
    WorldTile("alien_data_repository", "Alien Data Repository", WorldKind.WINDFALL, SettleKind.CIVILIAN, 5, 2, 4, Good.ALIEN, powers=Powers(explore_extra=1)),
    WorldTile("alien_sentinel", "Alien Sentinel", WorldKind.WINDFALL, SettleKind.CIVILIAN, 6, 2, 5, Good.ALIEN),
    WorldTile("alien_robot_sentry", "Alien Robot Sentry", WorldKind.WINDFALL, SettleKind.MILITARY, 5, 2, 4, Good.ALIEN, powers=Powers(military=1)),
    WorldTile("alien_ruins", "Alien Ruins", WorldKind.WINDFALL, SettleKind.MILITARY, 6, 2, 6, Good.ALIEN),
    WorldTile("lost_alien_battle_fleet", "Lost Alien Battle Fleet", WorldKind.WINDFALL, SettleKind.MILITARY, 7, 3, 7, Good.ALIEN, powers=Powers(military=2)),
    # Military gray/rebel worlds.
    WorldTile("rebel_outpost", "Rebel Outpost", WorldKind.GRAY, SettleKind.MILITARY, 2, 1, 2, powers=Powers(military=1)),
    WorldTile("rebel_base", "Rebel Base", WorldKind.GRAY, SettleKind.MILITARY, 4, 1, 4, powers=Powers(military=2)),
    WorldTile("rebel_fleet", "Rebel Fleet", WorldKind.GRAY, SettleKind.MILITARY, 5, 2, 5, powers=Powers(military=2)),
    WorldTile("rebel_homeworld", "Rebel Homeworld", WorldKind.GRAY, SettleKind.MILITARY, 6, 2, 6, powers=Powers(military=2, military_settle_vp=1)),
    WorldTile("imperium_warlord_world", "Imperium Warlord World", WorldKind.GRAY, SettleKind.MILITARY, 6, 2, 6, powers=Powers(military=2)),
    WorldTile("distant_world", "Distant World", WorldKind.GRAY, SettleKind.MILITARY, 3, 1, 3, powers=Powers(explore_extra=1)),
    WorldTile("doomed_world", "Doomed World", WorldKind.GRAY, SettleKind.MILITARY, 1, 1, 1),
    WorldTile("fortress_world", "Fortress World", WorldKind.GRAY, SettleKind.MILITARY, 5, 2, 5, powers=Powers(military=1)),
    WorldTile("imperium_seat", "Imperium Seat", WorldKind.GRAY, SettleKind.MILITARY, 7, 3, 7, powers=Powers(military=3)),
    WorldTile("pirate_world", "Pirate World", WorldKind.WINDFALL, SettleKind.MILITARY, 4, 1, 4, Good.RARE, powers=Powers(trade_bonus=1)),
    WorldTile("rebel_fuel_cache", "Rebel Fuel Cache", WorldKind.WINDFALL, SettleKind.MILITARY, 4, 1, 4, Good.RARE),
    WorldTile("warbot_world", "Warbot World", WorldKind.PRODUCTION, SettleKind.MILITARY, 5, 2, 4, Good.RARE, powers=Powers(military=1)),
    # Extra civilian depth so the bag is close to base RFTG world scale.
    WorldTile("colony_ship", "Colony Ship", WorldKind.GRAY, SettleKind.CIVILIAN, 3, 1, 2, powers=Powers(settle_discount=1)),
    WorldTile("secluded_world", "Secluded World", WorldKind.WINDFALL, SettleKind.CIVILIAN, 3, 1, 2, Good.NOVELTY),
    WorldTile("comet_zone", "Comet Zone", WorldKind.WINDFALL, SettleKind.CIVILIAN, 4, 2, 3, Good.RARE, powers=Powers(produce_credit=1)),
    WorldTile("living_ocean", "Living Ocean", WorldKind.WINDFALL, SettleKind.CIVILIAN, 5, 2, 4, Good.GENES, powers=Powers(consume_vp_per_good=1)),
]
