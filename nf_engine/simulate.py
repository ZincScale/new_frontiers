from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from .engine import Game, GameConfig


def run_one(strategies, seed, config):
    game = Game(strategies, seed=seed, config=config)
    scores = game.play()
    return game.round, scores


def main():
    parser = argparse.ArgumentParser(description="Run New Frontiers-style AI simulations.")
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--no-military-logistics", action="store_true", help="Disable the modified military logistics cost.")
    parser.add_argument("--military-defense-bonus", type=int, default=0, help="Increase military world defense requirements by this amount.")
    parser.add_argument(
        "--players",
        nargs="+",
        default=["balanced", "military", "economy", "builder"],
        help="Strategies: random, balanced, military, economy, builder",
    )
    args = parser.parse_args()

    config = GameConfig(
        military_logistics=not args.no_military_logistics,
        military_defense_bonus=args.military_defense_bonus,
    )

    wins = Counter()
    appearances = Counter()
    display_strategies = list(dict.fromkeys(args.players))
    totals = defaultdict(int)
    metrics = defaultdict(lambda: defaultdict(int))
    rounds = []
    last_scores = None
    for i in range(args.games):
        game_rounds, scores = run_one(args.players, args.seed + i, config)
        rounds.append(game_rounds)
        last_scores = scores
        winner = scores[0][0].split("-", 1)[1]
        wins[winner] += 1
        for name, score, _tie, summary in scores:
            strategy = name.split("-", 1)[1]
            appearances[strategy] += 1
            totals[strategy] += score
            for key, value in summary.items():
                metrics[strategy][key] += value

    print(f"Games: {args.games}")
    print(f"Players: {', '.join(args.players)}")
    print(f"Military logistics: {config.military_logistics}")
    print(f"Military defense bonus: {config.military_defense_bonus}")
    print(f"Average rounds: {sum(rounds) / len(rounds):.1f}")
    print()
    print("Wins")
    for strategy, count in wins.most_common():
        print(f"  {strategy}: {count}")
    print()
    print("Average score")
    for strategy in display_strategies:
        print(f"  {strategy}: {totals[strategy] / appearances[strategy]:.1f}")
    print()
    print("Average final metrics")
    for strategy in display_strategies:
        denom = appearances[strategy]
        colonies = metrics[strategy]["colonies"] / denom
        military = metrics[strategy]["military"] / denom
        devs = metrics[strategy]["developments"] / denom
        credits = metrics[strategy]["credits"] / denom
        vp_chips = metrics[strategy]["vp_chips"] / denom
        print(
            f"  {strategy}: colonies {colonies:.1f}, devs {devs:.1f}, "
            f"military {military:.1f}, credits {credits:.1f}, VP chips {vp_chips:.1f}"
        )
    print()
    print("Last game final table")
    for name, score, tie, summary in last_scores or []:
        print(f"  {name}: {score} VP, tie {tie}, {summary}")


if __name__ == "__main__":
    main()
