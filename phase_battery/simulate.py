from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from statistics import mean

from .engine import PhaseBatteryConfig, PhaseBatteryGame


def rotate_specs(specs, offset):
    if not specs:
        return specs
    offset %= len(specs)
    return specs[offset:] + specs[:offset]


def run_one(specs, seed, config):
    game = PhaseBatteryGame(specs, seed=seed, config=config)
    scores, reports = game.play()
    return scores, reports


def game_vp_pool_per_player(config, player_count):
    if config.vp_pool_per_player is not None:
        return config.vp_pool_per_player
    return 7


def main():
    parser = argparse.ArgumentParser(description="Run the main Roll Phase Battery prototype.")
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--max-track-capacity", type=int, default=6)
    parser.add_argument("--starting-capacity", type=int, default=3)
    parser.add_argument("--starting-credits", type=int, default=1)
    parser.add_argument("--free-recharge", type=int, default=0)
    parser.add_argument("--yellow-mode", choices=("ship", "alien"), default="alien")
    parser.add_argument("--vp-pool-per-player", type=int, default=None)
    parser.add_argument("--max-rounds", type=int, default=40)
    parser.add_argument("--construction-limit", type=int, default=3)
    parser.add_argument("--red-grants-max-only", action="store_true")
    parser.add_argument("--fixed-seats", action="store_true")
    parser.add_argument(
        "--players",
        nargs="+",
        default=["P1:builder", "P2:producer"],
        help=(
            "Players as name:strategy. Strategies: balanced, builder, settler, producer, "
            "shipper, mining, novelty, genes, alien, military, diverse."
        ),
    )
    args = parser.parse_args()

    specs = []
    for spec in args.players:
        name, strategy = spec.split(":", 1)
        specs.append((name, strategy))

    config = PhaseBatteryConfig(
        starting_capacity=args.starting_capacity,
        starting_credits=args.starting_credits,
        max_track_capacity=args.max_track_capacity,
        minimum_recharge=args.free_recharge,
        yellow_mode=args.yellow_mode,
        vp_pool_per_player=args.vp_pool_per_player,
        max_rounds=args.max_rounds,
        construction_limit=args.construction_limit,
        red_grants_current=not args.red_grants_max_only,
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
        wins[scores[0][2]["strategy"]] += 1
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
                "red_exhausts",
                "cup_recharges",
                "unready_die_gains",
                "reassigned_pips",
                "shipped_goods",
                "credits_earned",
                "credits_spent",
                "goal_score",
                "completed_tiles",
                "military_worlds",
                "normal_worlds",
                "production_worlds",
            ):
                metrics[strategy][key] += summary[key]
            metrics[strategy]["goal_commits"] += int(summary["goal_commit_round"] is not None)
            metrics[strategy]["committed_goals"] += len(summary["committed_goals"])
            metrics[strategy]["current_capacity"] += sum(current for current, _maximum in summary["tracks"].values())
            metrics[strategy]["max_capacity"] += sum(maximum for _current, maximum in summary["tracks"].values())

    print(f"Games: {args.games}")
    print(f"Players: {', '.join(args.players)}")
    print(f"Starting capacity: {config.starting_capacity}")
    print(f"Starting credits: {config.starting_credits}")
    print(f"Max track capacity: {config.max_track_capacity}")
    print("Credits: unlimited chips")
    print("White: non-Military Settle track")
    print(f"Free recharge: {config.minimum_recharge}")
    print(f"Yellow mode: {config.yellow_mode}")
    print(f"Red grants current: {config.red_grants_current}")
    print(f"Construction limit: {config.construction_limit}")
    print(f"VP pool per player: {game_vp_pool_per_player(config, len(specs))}")
    print(f"End-game goal pool: {config.endgame_goal_pool_extra} + players, penalty {config.endgame_goal_penalty}")
    print("Scoring: tableau VP + VP chips + chosen 6-cost goals")
    print(f"Average rounds: {mean(rounds):.1f}")
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
            f"military/normal worlds {metrics[strategy]['military_worlds'] / denom:.1f}/"
            f"{metrics[strategy]['normal_worlds'] / denom:.1f}, "
            f"production worlds {metrics[strategy]['production_worlds'] / denom:.1f}, "
            f"used pips {metrics[strategy]['used_pips'] / denom:.1f}, "
            f"red exhausts {metrics[strategy]['red_exhausts'] / denom:.1f}, "
            f"cup/unready/reassigned {metrics[strategy]['cup_recharges'] / denom:.1f}/"
            f"{metrics[strategy]['unready_die_gains'] / denom:.1f}/"
            f"{metrics[strategy]['reassigned_pips'] / denom:.1f}, "
            f"shipped goods {metrics[strategy]['shipped_goods'] / denom:.1f}, "
            f"credits earned/spent {metrics[strategy]['credits_earned'] / denom:.1f}/"
            f"{metrics[strategy]['credits_spent'] / denom:.1f}, "
            f"goals {metrics[strategy]['committed_goals'] / denom:.1f} "
            f"({metrics[strategy]['goal_score'] / denom:.1f} VP), "
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
        print(
            f"  R{report.round_number}: used {report.used_pips}, "
            f"red {report.red_exhausts}, scores {report.scores}"
        )


if __name__ == "__main__":
    main()
