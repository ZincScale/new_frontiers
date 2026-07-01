from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from .engine import GameConfig, UpgradeGame


def run_one(player_specs, seed, config):
    game = UpgradeGame(player_specs, seed=seed, config=config)
    scores, reports = game.play()
    return game.turn, scores, reports


def rotate_specs(player_specs, offset):
    if not player_specs:
        return player_specs
    offset %= len(player_specs)
    return player_specs[offset:] + player_specs[:offset]


def main():
    parser = argparse.ArgumentParser(description="Run the dice-galaxy upgrade prototype.")
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--target-vp", type=int, default=21)
    parser.add_argument("--no-upgrades", action="store_true", help="Disable the optional upgrade-card expansion module.")
    parser.add_argument("--fixed-seats", action="store_true", help="Do not rotate player order between games.")
    parser.add_argument(
        "--players",
        nargs="+",
        default=["frontier_union:mobility", "star_cartel:economy"],
        help="Players as personality:strategy. Personalities: frontier_union, star_cartel, archive_compact, settlement_charter.",
    )
    args = parser.parse_args()

    player_specs = []
    for index, spec in enumerate(args.players, start=1):
        personality, strategy = spec.split(":", 1)
        player_specs.append((f"P{index}-{personality}", personality, strategy))

    config = GameConfig(target_vp=args.target_vp, enable_upgrades=not args.no_upgrades)
    wins = Counter()
    turns = []
    totals = defaultdict(int)
    appearances = Counter()
    upgrade_counts = Counter()
    metrics = defaultdict(lambda: defaultdict(int))
    zero_colony_finishes = Counter()
    zero_colony_wins = Counter()
    last_scores = None
    last_reports = None

    for i in range(args.games):
        seated_specs = player_specs if args.fixed_seats else rotate_specs(player_specs, i)
        game_turns, scores, reports = run_one(seated_specs, args.seed + i, config)
        turns.append(game_turns)
        last_scores = scores
        last_reports = reports
        winner = scores[0][0].split("-", 1)[1]
        wins[winner] += 1
        if scores[0][3]["colonies"] == 0:
            zero_colony_wins[winner] += 1
        for name, score, _tie, summary in scores:
            identity = name.split("-", 1)[1]
            appearances[identity] += 1
            totals[identity] += score
            metrics[identity]["colonies"] += summary["colonies"]
            metrics[identity]["empire_level"] += summary["empire_level"]
            metrics[identity]["energy"] += summary["energy"]
            metrics[identity]["culture"] += summary["culture"]
            metrics[identity]["upgrades"] += len(summary["upgrades"])
            metrics[identity]["active_presence"] += len(summary["missions"]) + len(summary["landed"])
            if summary["colonies"] == 0:
                zero_colony_finishes[identity] += 1
            for upgrade in summary["upgrades"]:
                upgrade_counts[(identity, upgrade)] += 1

    print(f"Games: {args.games}")
    print(f"Players: {', '.join(args.players)}")
    print(f"Upgrade module: {config.enable_upgrades}")
    print(f"Seat rotation: {not args.fixed_seats}")
    print(f"Average turns: {sum(turns) / len(turns):.1f}")
    print()
    print("Wins")
    for identity, count in wins.most_common():
        print(f"  {identity}: {count}")
    print()
    print("Average score")
    for _name, personality, _strategy in player_specs:
        print(f"  {personality}: {totals[personality] / appearances[personality]:.1f}")
    print()
    print("Most bought upgrades")
    for (identity, upgrade), count in upgrade_counts.most_common(10):
        print(f"  {identity}: {upgrade} ({count})")
    print()
    print("Average final metrics")
    for _name, personality, _strategy in player_specs:
        denom = appearances[personality]
        colonies = metrics[personality]["colonies"] / denom
        empire_level = metrics[personality]["empire_level"] / denom
        upgrades = metrics[personality]["upgrades"] / denom
        presence = metrics[personality]["active_presence"] / denom
        zero_rate = zero_colony_finishes[personality] / denom
        zero_win_rate = zero_colony_wins[personality] / wins[personality] if wins[personality] else 0
        print(
            f"  {personality}: colonies {colonies:.1f}, empire {empire_level:.1f}, "
            f"upgrades {upgrades:.1f}, active presence {presence:.1f}, "
            f"zero-colony {zero_rate:.1%}, zero-colony wins {zero_win_rate:.1%}"
        )
    print()
    print("Last game final table")
    for name, score, tie, summary in last_scores or []:
        print(f"  {name}: {score} VP, tie {tie}, {summary}")
    print()
    print("Last game final turns")
    for report in (last_reports or [])[-6:]:
        bought = f", bought {report.bought_upgrade}" if report.bought_upgrade else ""
        claimed = f", claimed {list(report.claimed_planets)}" if report.claimed_planets else ""
        print(
            f"  {report.player}: roll {[face.value for face in report.roll]} -> "
            f"{[face.value for face in report.used]}, {report.vp} VP, {report.colonies} colonies{bought}{claimed}"
        )


if __name__ == "__main__":
    main()
