from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from .engine import BatteryConfig, BatteryGame


def rotate_specs(specs, offset):
    if not specs:
        return specs
    offset %= len(specs)
    return specs[offset:] + specs[:offset]


def run_one(specs, seed, config):
    game = BatteryGame(specs, seed=seed, config=config)
    scores, reports = game.play()
    return scores, reports


def main():
    parser = argparse.ArgumentParser(description="Run the Roll phase-battery prototype.")
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--max-track-capacity", type=int, default=6)
    parser.add_argument("--starting-capacity", type=int, default=2)
    parser.add_argument("--starting-white-capacity", type=int, default=2)
    parser.add_argument("--starting-credits", type=int, default=1)
    parser.add_argument("--free-recharge", type=int, default=0)
    parser.add_argument("--yellow-mode", choices=("ship", "alien"), default="alien")
    parser.add_argument("--max-rounds", type=int, default=40)
    parser.add_argument("--fixed-seats", action="store_true")
    parser.add_argument(
        "--players",
        nargs="+",
        default=["P1:builder", "P2:producer"],
        help="Players as name:strategy. Strategies: balanced, builder, settler, producer, shipper.",
    )
    args = parser.parse_args()

    specs = []
    for spec in args.players:
        name, strategy = spec.split(":", 1)
        specs.append((name, strategy))

    config = BatteryConfig(
        starting_capacity=args.starting_capacity,
        starting_white_capacity=args.starting_white_capacity,
        max_track_capacity=args.max_track_capacity,
        starting_credits=args.starting_credits,
        minimum_recharge=args.free_recharge,
        yellow_mode=args.yellow_mode,
        max_rounds=args.max_rounds,
    )
    wins = Counter()
    appearances = Counter()
    totals = defaultdict(int)
    metrics = defaultdict(lambda: defaultdict(int))
    rounds = []
    last_scores = None
    last_reports = None

    for index in range(args.games):
        seated = specs if args.fixed_seats else rotate_specs(specs, index)
        scores, reports = run_one(seated, args.seed + index, config)
        last_scores = scores
        last_reports = reports
        rounds.append(scores[0][2]["rounds"])
        winner_strategy = scores[0][2]["strategy"]
        wins[winner_strategy] += 1
        for _name, score, summary in scores:
            strategy = summary["strategy"]
            appearances[strategy] += 1
            totals[strategy] += score
            for key in (
                "tableau",
                "credits",
                "goods",
                "dead_rounds",
                "used_pips",
                "credits_earned",
                "credits_spent",
                "free_recharged",
                "blocked_recharge",
                "completed_tiles",
            ):
                metrics[strategy][key] += summary[key]
            metrics[strategy]["current_capacity"] += sum(current for current, _maximum in summary["tracks"].values())
            metrics[strategy]["max_capacity"] += sum(maximum for _current, maximum in summary["tracks"].values())

    print(f"Games: {args.games}")
    print(f"Players: {', '.join(args.players)}")
    print(f"Starting capacity: {config.starting_capacity}")
    print(f"Starting white capacity: {config.starting_white_capacity}")
    print(f"Max track capacity: {config.max_track_capacity}")
    print(f"Starting credits: {config.starting_credits}")
    print(f"Free recharge: {config.minimum_recharge}")
    print(f"Yellow mode: {config.yellow_mode}")
    print(f"Average rounds: {sum(rounds) / len(rounds):.1f}")
    print()
    print("Wins")
    for strategy, count in wins.most_common():
        print(f"  {strategy}: {count}")
    print()
    print("Average final metrics")
    for _name, strategy in specs:
        denom = appearances[strategy]
        print(
            f"  {strategy}: score {totals[strategy] / denom:.1f}, "
            f"tableau {metrics[strategy]['tableau'] / denom:.1f}, "
            f"completed {metrics[strategy]['completed_tiles'] / denom:.1f}, "
            f"used pips {metrics[strategy]['used_pips'] / denom:.1f}, "
            f"credits earned/spent {metrics[strategy]['credits_earned'] / denom:.1f}/"
            f"{metrics[strategy]['credits_spent'] / denom:.1f}, "
            f"free recharge {metrics[strategy]['free_recharged'] / denom:.1f}, "
            f"blocked {metrics[strategy]['blocked_recharge'] / denom:.1f}, "
            f"dead rounds {metrics[strategy]['dead_rounds'] / denom:.2f}, "
            f"capacity {metrics[strategy]['current_capacity'] / denom:.1f}/"
            f"{metrics[strategy]['max_capacity'] / denom:.1f}"
        )
    print()
    print("Last game final table")
    for name, score, summary in last_scores or []:
        print(f"  {name}: {score} VP, {summary}")
    print()
    print("Last game final rounds")
    for report in (last_reports or [])[-5:]:
        phases = [phase.value for phase in report.selected]
        print(f"  R{report.round_number}: phases {phases}, used {report.used_pips}, scores {report.scores}")


if __name__ == "__main__":
    main()
