from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass

from .cards import RIVAL_DIFFICULTIES, RIVAL_EMPIRES
from .engine import GameConfig, UpgradeGame


RIVAL_SEATS = {
    "devourer_swarm": ("frontier_union", "mobility"),
    "iron_directorate": ("star_cartel", "economy"),
    "void_corsairs": ("star_cartel", "economy"),
    "oracle_singularity": ("archive_compact", "culture"),
}


@dataclass(frozen=True)
class RivalDifficultyTuning:
    id: str
    name: str
    text: str
    empire_level: int
    energy: int
    culture: int
    vp: int


def available_profiles():
    return tuple(profile.id for profile in RIVAL_EMPIRES)


def available_difficulties():
    return tuple(board.id for board in RIVAL_DIFFICULTIES)


def difficulty_by_id(difficulty_id: str):
    return next(difficulty for difficulty in RIVAL_DIFFICULTIES if difficulty.id == difficulty_id)


def difficulty_tuning(
    difficulty_id: str,
    empire_level: int | None = None,
    energy: int | None = None,
    culture: int | None = None,
    vp: int | None = None,
):
    difficulty = difficulty_by_id(difficulty_id)
    overrides = {
        "empire_level": empire_level,
        "energy": energy,
        "culture": culture,
        "vp": vp,
    }
    active = {key: value for key, value in overrides.items() if value is not None}
    suffix = ""
    if active:
        suffix = " with overrides: " + ", ".join(f"{key}={value}" for key, value in active.items())
    return RivalDifficultyTuning(
        id=difficulty.id,
        name=difficulty.name,
        text=difficulty.text + suffix,
        empire_level=difficulty.empire_level if empire_level is None else empire_level,
        energy=difficulty.energy if energy is None else energy,
        culture=difficulty.culture if culture is None else culture,
        vp=difficulty.vp if vp is None else vp,
    )


def build_specs(human: str, profile_id: str):
    human_personality, human_strategy = human.split(":", 1)
    rival_personality, rival_strategy = RIVAL_SEATS[profile_id]
    return [
        (f"Human-{human_personality}", human_personality, human_strategy),
        (f"Rival-{profile_id}", rival_personality, rival_strategy, profile_id),
    ]


def apply_rival_difficulty(game: UpgradeGame, difficulty: str | RivalDifficultyTuning):
    tuning = difficulty_tuning(difficulty) if isinstance(difficulty, str) else difficulty
    rival = next(player for player in game.players if player.rival_profile)
    rival.empire_level = tuning.empire_level
    rival.energy = tuning.energy
    rival.culture = tuning.culture
    rival.vp = tuning.vp
    rival.available_ships = game.empire_step(tuning.empire_level).ships
    return tuning


def run_one(human: str, profile_id: str, difficulty: RivalDifficultyTuning, seed: int, config: GameConfig):
    game = UpgradeGame(build_specs(human, profile_id), seed=seed, config=config)
    apply_rival_difficulty(game, difficulty)
    scores, reports = game.play()
    return game.turn, scores, reports


def winner_side(scores):
    return scores[0][0].split("-", 1)[0]


def side_summary(scores, side: str):
    return next(summary for name, _score, _tie, summary in scores if name.startswith(f"{side}-"))


def run_profile(human: str, profile_id: str, difficulty: str | RivalDifficultyTuning, games: int, seed: int, config: GameConfig):
    tuning = difficulty_tuning(difficulty) if isinstance(difficulty, str) else difficulty
    wins = Counter()
    turns = []
    totals = Counter()
    metrics = defaultdict(int)
    last_scores = None

    for index in range(games):
        game_turns, scores, _reports = run_one(human, profile_id, tuning, seed + index, config)
        turns.append(game_turns)
        last_scores = scores
        wins[winner_side(scores)] += 1
        for side in ("Human", "Rival"):
            summary = side_summary(scores, side)
            score = next(score for name, score, _tie, _summary in scores if name.startswith(f"{side}-"))
            totals[side] += score
            metrics[(side, "colonies")] += summary["colonies"]
            metrics[(side, "empire_level")] += summary["empire_level"]
            metrics[(side, "upgrades")] += len(summary["upgrades"])

    return {
        "profile": profile_id,
        "difficulty": tuning.id,
        "difficulty_text": tuning.text,
        "difficulty_tuning": tuning,
        "wins": wins,
        "average_turns": sum(turns) / len(turns),
        "average_scores": {side: totals[side] / games for side in ("Human", "Rival")},
        "average_metrics": {
            side: {
                "colonies": metrics[(side, "colonies")] / games,
                "empire_level": metrics[(side, "empire_level")] / games,
                "upgrades": metrics[(side, "upgrades")] / games,
            }
            for side in ("Human", "Rival")
        },
        "last_scores": last_scores,
    }


def print_result(result):
    tuning = result["difficulty_tuning"]
    print(
        f"Profile: {result['profile']} ({result['difficulty']}: "
        f"empire {tuning.empire_level}, energy {tuning.energy}, culture {tuning.culture}, VP {tuning.vp})"
    )
    print(f"  Wins: Human {result['wins']['Human']}, Rival {result['wins']['Rival']}")
    print(f"  Average turns: {result['average_turns']:.1f}")
    print(
        "  Average score: "
        f"Human {result['average_scores']['Human']:.1f}, "
        f"Rival {result['average_scores']['Rival']:.1f}"
    )
    for side, metrics in result["average_metrics"].items():
        print(
            f"  {side}: colonies {metrics['colonies']:.1f}, "
            f"empire {metrics['empire_level']:.1f}, upgrades {metrics['upgrades']:.1f}"
        )
    print()


def print_sweep_row(results):
    tuning = results[0]["difficulty_tuning"]
    rival_wins = sum(result["wins"]["Rival"] for result in results)
    total_games = sum(result["wins"]["Rival"] + result["wins"]["Human"] for result in results)
    profile_rates = ", ".join(
        f"{result['profile']} {result['wins']['Rival'] / (result['wins']['Rival'] + result['wins']['Human']):.0%}"
        for result in results
    )
    print(
        f"empire {tuning.empire_level}, energy {tuning.energy}, culture {tuning.culture}, VP {tuning.vp}: "
        f"Rival {rival_wins / total_games:.0%} ({profile_rates})"
    )


def parse_sweep_values(raw: str):
    values = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        values.append(int(part))
    return values


def main():
    parser = argparse.ArgumentParser(description="Run Rival Empire solo simulations.")
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--target-vp", type=int, default=21)
    parser.add_argument("--no-upgrades", action="store_true", help="Disable the optional upgrade-card expansion module.")
    parser.add_argument(
        "--human",
        default="frontier_union:mobility",
        help="Human as personality:strategy.",
    )
    parser.add_argument(
        "--profile",
        default="all",
        choices=("all",) + available_profiles(),
        help="Rival Empire profile to test.",
    )
    parser.add_argument(
        "--difficulty",
        default="standard",
        choices=available_difficulties(),
        help="Rival difficulty card.",
    )
    parser.add_argument("--board", choices=available_difficulties(), help=argparse.SUPPRESS)
    parser.add_argument("--rival-empire", type=int, help="Override rival starting empire level for tuning.")
    parser.add_argument("--rival-energy", type=int, help="Override rival starting energy for tuning.")
    parser.add_argument("--rival-culture", type=int, help="Override rival starting culture for tuning.")
    parser.add_argument("--rival-vp", type=int, help="Override rival starting VP for tuning.")
    parser.add_argument("--sweep-vp", help="Comma-separated Rival starting VP values to test.")
    parser.add_argument("--sweep-energy", help="Comma-separated Rival starting energy values to test.")
    parser.add_argument("--sweep-culture", help="Comma-separated Rival starting culture values to test.")
    args = parser.parse_args()

    config = GameConfig(target_vp=args.target_vp, enable_upgrades=not args.no_upgrades)
    profiles = available_profiles() if args.profile == "all" else (args.profile,)
    difficulty_id = args.board or args.difficulty
    if args.sweep_vp or args.sweep_energy or args.sweep_culture:
        base = difficulty_tuning(
            difficulty_id,
            empire_level=args.rival_empire,
            energy=args.rival_energy,
            culture=args.rival_culture,
            vp=args.rival_vp,
        )
        vp_values = parse_sweep_values(args.sweep_vp) if args.sweep_vp else [base.vp]
        energy_values = parse_sweep_values(args.sweep_energy) if args.sweep_energy else [base.energy]
        culture_values = parse_sweep_values(args.sweep_culture) if args.sweep_culture else [base.culture]
        print(f"Human: {args.human}")
        print(f"Base difficulty: {base.id} - {base.text}")
        print(f"Games per profile per scenario: {args.games}")
        print(f"Upgrade module: {config.enable_upgrades}")
        print()
        scenario = 0
        for energy in energy_values:
            for culture in culture_values:
                for vp in vp_values:
                    tuning = difficulty_tuning(
                        difficulty_id,
                        empire_level=base.empire_level,
                        energy=energy,
                        culture=culture,
                        vp=vp,
                    )
                    results = [
                        run_profile(
                            args.human,
                            profile_id,
                            tuning,
                            args.games,
                            args.seed + scenario * args.games * max(1, len(profiles)) + offset * args.games,
                            config,
                        )
                        for offset, profile_id in enumerate(profiles)
                    ]
                    print_sweep_row(results)
                    scenario += 1
        return

    tuning = difficulty_tuning(
        difficulty_id,
        empire_level=args.rival_empire,
        energy=args.rival_energy,
        culture=args.rival_culture,
        vp=args.rival_vp,
    )
    print(f"Human: {args.human}")
    print(f"Rival difficulty: {tuning.id} - {tuning.text}")
    print(f"Games per profile: {args.games}")
    print(f"Upgrade module: {config.enable_upgrades}")
    print()
    for offset, profile_id in enumerate(profiles):
        result = run_profile(args.human, profile_id, tuning, args.games, args.seed + offset * args.games, config)
        print_result(result)


if __name__ == "__main__":
    main()
