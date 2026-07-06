from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from .engine import MancalaConfig, MancalaGame


def rotate_specs(specs, offset):
    if not specs:
        return specs
    offset %= len(specs)
    return specs[offset:] + specs[:offset]


def run_one(specs, seed, config):
    game = MancalaGame(specs, seed=seed, config=config)
    scores, reports = game.play()
    return scores, reports


def main():
    parser = argparse.ArgumentParser(description="Run the Roll mancala dice prototype.")
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--section-cap", type=int, default=6)
    parser.add_argument("--starting-per-phase", type=int, default=2)
    parser.add_argument("--starting-white", type=int, default=2)
    parser.add_argument("--starting-yellow", type=int, default=0)
    parser.add_argument("--starting-credits", type=int, default=1)
    parser.add_argument("--recovery-sow-cost", type=int, default=2)
    parser.add_argument(
        "--dummy-phase-count",
        type=int,
        default=0,
        help="Extra random unselected phases per round.",
    )
    parser.add_argument("--vp-pool-per-player", type=int, default=8)
    parser.add_argument("--max-rounds", type=int, default=50)
    parser.add_argument("--conservative-bonus", action="store_true")
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

    config = MancalaConfig(
        section_cap=args.section_cap,
        starting_per_phase=args.starting_per_phase,
        starting_white=args.starting_white,
        starting_yellow=args.starting_yellow,
        starting_credits=args.starting_credits,
        recovery_sow_cost=args.recovery_sow_cost,
        conservative_bonus=args.conservative_bonus,
        dummy_phase_count=args.dummy_phase_count,
        vp_pool_per_player=args.vp_pool_per_player,
        max_rounds=args.max_rounds,
    )

    wins = Counter()
    appearances = Counter()
    totals = defaultdict(int)
    metrics = defaultdict(lambda: defaultdict(int))
    rounds = []
    phase_counts = Counter()
    last_scores = None
    last_reports = None

    for index in range(args.games):
        seated = specs if args.fixed_seats else rotate_specs(specs, index)
        scores, reports = run_one(seated, args.seed + index, config)
        last_scores = scores
        last_reports = reports
        rounds.append(scores[0][2]["rounds"])
        wins[scores[0][2]["strategy"]] += 1
        for report in reports:
            for phase in report.selected:
                phase_counts[phase.value] += 1
        for _name, score, summary in scores:
            strategy = summary["strategy"]
            appearances[strategy] += 1
            totals[strategy] += score
            for key in (
                "tableau",
                "credits",
                "goods",
                "dead_rounds",
                "used_workers",
                "completed_tiles",
                "credits_earned",
                "credits_spent",
                "recovery_sows",
                "color_match_bonuses",
            ):
                metrics[strategy][key] += summary[key]

    print(f"Games: {args.games}")
    print(f"Players: {', '.join(args.players)}")
    print(f"Section cap: {config.section_cap}")
    print(f"Starting dice: {config.starting_per_phase} per phase, white {config.starting_white}, yellow {config.starting_yellow}")
    print(f"Starting credits: {config.starting_credits}")
    print(f"Recovery sow cost: {config.recovery_sow_cost}")
    print(f"Dummy phase count: {config.dummy_phase_count}")
    print(f"Conservative bonus: {config.conservative_bonus}")
    print(f"VP pool per player: {config.vp_pool_per_player}")
    print(f"Average rounds: {sum(rounds) / len(rounds):.1f}")
    print()
    print("Wins")
    for strategy, count in wins.most_common():
        print(f"  {strategy}: {count}")
    print()
    print("Selected phase counts")
    for phase, count in phase_counts.most_common():
        print(f"  {phase}: {count}")
    print()
    print("Average final metrics")
    for _name, strategy in specs:
        denom = appearances[strategy]
        print(
            f"  {strategy}: score {totals[strategy] / denom:.1f}, "
            f"tableau {metrics[strategy]['tableau'] / denom:.1f}, "
            f"completed {metrics[strategy]['completed_tiles'] / denom:.1f}, "
            f"used workers {metrics[strategy]['used_workers'] / denom:.1f}, "
            f"credits earned/spent {metrics[strategy]['credits_earned'] / denom:.1f}/"
            f"{metrics[strategy]['credits_spent'] / denom:.1f}, "
            f"recovery sows {metrics[strategy]['recovery_sows'] / denom:.1f}, "
            f"match bonuses {metrics[strategy]['color_match_bonuses'] / denom:.1f}, "
            f"dead rounds {metrics[strategy]['dead_rounds'] / denom:.2f}"
        )
    print()
    print("Last game final table")
    for name, score, summary in last_scores or []:
        print(f"  {name}: {score} VP, {summary}")
    print()
    print("Last game final rounds")
    for report in (last_reports or [])[-5:]:
        phases = [phase.value for phase in report.selected]
        selections = {name: phase.value if phase else None for name, phase in report.selections.items()}
        dummy = [phase.value for phase in report.dummy_phases]
        print(f"  R{report.round_number}: phases {phases}, dummy {dummy}, selected {selections}, used {report.used_workers}, scores {report.scores}")


if __name__ == "__main__":
    main()
